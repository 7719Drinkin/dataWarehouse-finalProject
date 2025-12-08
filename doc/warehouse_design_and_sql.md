# 数据存储设计说明与部署脚本

> **文件说明**：本文档同时包含设计说明、E-R / 星型模型说明、关系型DDL、Hive 表定义、Spark 作业模板、Neo4j Cypher 脚本，以及 openGauss / Hive 的部署脚本。它与仓库目录 `warehouse/` 的文件结构对应：

```
warehouse/
├── relational/
│   ├── star_schema.pdf
│   ├── ddl/
│   │   ├── fact_reviews.sql
│   │   ├── dim_movies.sql
│   │   ├── dim_actors.sql
│   │   └── index.sql
│   └── scripts/
│        └── deploy_opengauss.sh
│
├── distributed/
│   ├── hive_tables/
│   │    └── create_movie_reviews.hql
│   ├── spark_jobs/
│   │    ├── movie_statistics.py
│   │    └── lineage_analysis.py
│   └── scripts/
│        └── deploy_hive.sh
│
└── graph/
     ├── node_definitions.cypher
     ├── relationships.cypher
     └── scripts/
          └── deploy_neo4j.sh
```

---

## 1. 整体存储模式（协同工作说明）

### 总体思想
- **Single-source-of-truth**: ETL（`etl/`）先在本地对 `data_source/` 完成 Extract & Transform，输出清洗后的中间表（Parquet/JSONL）。这些中间表用作向三套数据库加载的统一输入。
- **职责划分**:
  - **openGauss（关系型）**：保存面向业务的星型模型（事实表 `fact_review` + 多个维表 `dim_movie/dim_actor/dim_director/dim_time`）。用于低延迟、结构化、聚合型查询（例如：某年电影数、导演电影计数、评分分布等）。
  - **Hive/HDFS（分布式文件）**：保存原始和清洗过的海量数据（Parquet 格式），作为历史存储与大规模批量计算（SparkSQL）使用。适合需要扫描大量 review 的统计或复杂 ETL。支持按时间分区以提升查询性能。
  - **Neo4j（图数据库）**：保存电影-演员-导演-用户的关系图。适合复杂关系检索，如演员合作网络、常见演员组合、2人/3人组合热度计算。

### 数据流（简明）
1. 本地 ETL 抽取 `movies.txt` 与 `html_raw/`，生成 `movies_canonical.parquet` 与 `reviews_enriched.parquet`。
2. 将 Parquet/CSV 通过网络上传或直接用本地脚本连接服务器将数据写入 openGauss，或将 Parquet 上传至 HDFS 后创建 Hive 表。
3. 通过 Spark 作业对 Hive 表进行离线分析（movie_statistics.py），并将结果下沉至 openGauss（按需）和 Neo4j（关系导出并导入）。

---

## 2. 关系型存储逻辑模型（ER 图与存储模型）

### 2.1 设计目标
- 支持典型 OLAP 查询（按时间、电影、演员、导演统计）；
- 易于在 openGauss 上做索引与分区优化；
- 提供审计列（created_at, source_files）以支持血缘追踪。

### 2.2 星型模型（Star Schema）
- **Fact**: `fact_review`（每条评论作为事实行，度量：score, helpfulness, review_count等）
- **Dims**: `dim_movie`, `dim_actor`, `dim_director`, `dim_time`, `dim_user`（如果需要）

#### ER 说明（文本版）
- `fact_review` (fact) -> FK -> `dim_movie` (movie_id)
- `fact_review` -> FK -> `dim_time` (date_id)
- `movie` <-> `dim_actor` via bridge table `movie_actor` (many-to-many)


---

## 3. 关系型存储物理模型：DDL 与优化

下面给出可直接用于 openGauss 的 DDL 文件内容（请放 `warehouse/relational/ddl/`）：

### `dim_movies.sql`
```sql
-- dim_movies.sql
CREATE TABLE IF NOT EXISTS dim_movies (
  movie_id TEXT PRIMARY KEY,
  title TEXT,
  release_year INT,
  release_date DATE,
  genres TEXT[],
  versions TEXT[],
  primary_title TEXT,
  runtime_minutes INT,
  language TEXT,
  country TEXT,
  source_files TEXT[], -- 溯源：来自哪些HTML文件/ASIN
  created_at TIMESTAMP DEFAULT now()
);
```

### `dim_actors.sql`
```sql
-- dim_actors.sql
CREATE TABLE IF NOT EXISTS dim_actors (
  actor_id TEXT PRIMARY KEY,
  actor_name TEXT,
  normalized_name TEXT,
  birth_year INT,
  roles_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT now()
);

-- 中间表: movie-actor 关系
CREATE TABLE IF NOT EXISTS movie_actor (
  movie_id TEXT,
  actor_id TEXT,
  role_name TEXT,
  PRIMARY KEY (movie_id, actor_id)
);
```

### `fact_reviews.sql`
```sql
-- fact_reviews.sql
CREATE TABLE IF NOT EXISTS fact_reviews (
  review_id BIGSERIAL PRIMARY KEY,
  movie_id TEXT NOT NULL,
  user_id TEXT,
  profile_name TEXT,
  helpful_num INT,
  helpful_den INT,
  helpful_ratio FLOAT,
  score NUMERIC(3,1),
  review_time TIMESTAMP,
  review_unix BIGINT,
  summary TEXT,
  review_text TEXT,
  source_file TEXT, -- 哪个HTML或SNAP行
  loaded_at TIMESTAMP DEFAULT now(),
  date_id INT -- FK 到 dim_time
);
```

### `dim_time`（示例）
```sql
CREATE TABLE IF NOT EXISTS dim_time (
  date_id INT PRIMARY KEY,
  date DATE,
  year INT,
  quarter INT,
  month INT,
  day INT,
  weekday INT
);
```

### `index.sql`（索引与分区建议）
```sql
-- index.sql
-- 基本索引
CREATE INDEX IF NOT EXISTS idx_fact_movie ON fact_reviews(movie_id);
CREATE INDEX IF NOT EXISTS idx_fact_score ON fact_reviews(score);
CREATE INDEX IF NOT EXISTS idx_fact_time ON fact_reviews(review_unix);

-- 分区策略建议（openGauss 支持分区，按时间分区）
-- 示例分区（伪代码，需根据 openGauss 语法调整）
-- CREATE TABLE fact_reviews_y2024 PARTITION OF fact_reviews FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 存储优化设计 & Denormalization
- **优化点**:
  - 对 `fact_reviews` 建索引（movie_id、score、review_unix）；
  - 对较热维（dim_movie.title）创建 Gin 索引（全文或词条搜索）；
  - 对 `dim_movies.genres` 使用数组，并对常用 genre 查询建立倒排或物化视图。
- **反规范化**:
  - 将 `dim_movie` 的常用属性（title, release_year, main_genre）冗余存储到 `fact_reviews` 中（可选），以减少 join 成本并加速 OLAP 查询（适用于 read-heavy 场景）。
  - 在 ETL 中使用物化视图（MV）保存热点聚合（如 movie_rating_summary），并定期刷新。

---

## 4. 分布式文件系统存储模型（Hive schema 定义）

Hive 表结构主要保存清洗后和原始大表（Parquet）。放置位置：`warehouse/distributed/hive_tables/create_movie_reviews.hql`

### `create_movie_reviews.hql`
```sql
-- 创建 clean reviews 的外部表 (Parquet, partitioned by year/month)
CREATE EXTERNAL TABLE IF NOT EXISTS dw.reviews_clean (
  movie_id STRING,
  user_id STRING,
  profile_name STRING,
  helpful_num INT,
  helpful_den INT,
  helpful_ratio DOUBLE,
  score DOUBLE,
  review_time TIMESTAMP,
  review_unix BIGINT,
  summary STRING,
  review_text STRING,
  source_file STRING
)
PARTITIONED BY (year INT, month INT)
STORED AS PARQUET
LOCATION '/warehouse/clean/reviews/';

-- 电影元数据表
CREATE EXTERNAL TABLE IF NOT EXISTS dw.movies_meta (
  movie_id STRING,
  title STRING,
  release_year INT,
  genres ARRAY<STRING>,
  directors ARRAY<STRING>,
  actors ARRAY<STRING>
)
STORED AS PARQUET
LOCATION '/warehouse/clean/movies_meta/';
```

### Hive 优化建议
- 使用 **Parquet** 格式 + Snappy 压缩（列式存储）以节省 IO 与存储。
- 按 `year` / `month` 分区可有效减少全表扫描。
- 对于高基数字段避免 partition（如 movie_id 用 bucketing）。
- 可以结合 ORC + vectorized reader 在 Hive 中加快查询。

---

## 5. 图数据库存储模型及优化（Neo4j）

### 节点与关系模型
- 节点： `(:Movie {id, title, year, genres...})`, `(:Actor {id, name})`, `(:Director {id, name})`, `(:User {id, profileName})`
- 关系： `(:Actor)-[:ACTED_IN {role, billing_order}]->(:Movie)`, `(:Director)-[:DIRECTED]->(:Movie)`, `(:User)-[:REVIEWED {score, time}]->(:Movie)`, `(:Actor)-[:CO_ACTED_WITH {count}]->(:Actor)`（后者可为动画/定期计算结果）

### node_definitions.cypher
```cypher
// node_definitions.cypher
CREATE CONSTRAINT IF NOT EXISTS movie_id_unique FOR (m:Movie) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS actor_name_unique FOR (a:Actor) REQUIRE a.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS director_name_unique FOR (d:Director) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS user_id_unique FOR (u:User) REQUIRE u.id IS UNIQUE;
```

### relationships.cypher
```cypher
// relationships.cypher (示例增量导入语句模板)
USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///import/actors.csv' AS row
MERGE (a:Actor {name: row.actor_name})
RETURN count(*);
```

### 优化策略
- 在 Neo4j 中建立唯一约束和索引（上面 constraints）。
- 对于大规模导入，使用 `neo4j-admin import`（离线、空DB导入）比 `LOAD CSV` 更快。
- 若使用 Aura（云实例），使用批量 HTTP API 或 Bolt 驱动分批写入。

---

## 6. 数据表 Test Case

在 `warehouse/relational/tests/` 下提供测试 SQL (unit tests)：

### `tests/01_insert_sample.sql`
```sql
-- 插入样例 dim_movies
INSERT INTO dim_movies(movie_id, title, release_year, genres, source_files)
VALUES ('B00006HAXW','Sample Movie',2001, ARRAY['Action','Adventure'], ARRAY['B00006HAXW.html']);

-- 插入样例 actor
INSERT INTO dim_actors(actor_id, actor_name, normalized_name) VALUES ('A1','Tom Hanks','tom hanks');

-- 插入事实
INSERT INTO fact_reviews(movie_id, user_id, profile_name, helpful_num, helpful_den, helpful_ratio, score, review_time, review_unix, summary, review_text, source_file)
VALUES ('B00006HAXW','U1','Alice',1,1,1.0,4.5, to_timestamp(1622505600),1622505600,'Great','Loved it','B00006HAXW.html');
```

### `tests/02_validation.sql`
```sql
-- 简单验证查询
SELECT COUNT(*) FROM fact_reviews;
SELECT movie_id, AVG(score) as avg_score FROM fact_reviews GROUP BY movie_id ORDER BY avg_score DESC LIMIT 10;
```

这些测试应在数据加载后运行，以验证表结构和索引是否按预期工作。

---

## 7. 查询和统计程序（示例）

- `warehouse/distributed/spark_jobs/movie_statistics.py`：计算每年上映电影数、每电影平均评分、每导演电影数等。
- `backend/services/pg_service.py` 将实现 SQL 查询并供 API 调用。

### movie_statistics.py (Spark SQL 示例)
```python
# movie_statistics.py (PySpark)
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('movie_statistics').getOrCreate()
reviews = spark.read.parquet('/warehouse/clean/reviews/')
movies = spark.read.parquet('/warehouse/clean/movies_meta/')

# 每年电影数量
movies.groupBy('release_year').count().orderBy('release_year').show()

# 每电影平均评分
reviews.groupBy('movie_id').avg('score').withColumnRenamed('avg(score)','avg_score').orderBy('avg_score',ascending=False).show(50)

spark.stop()
```

### lineage_analysis.py (PySpark 溯源示例)
```python
# lineage_analysis.py
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('lineage_analysis').getOrCreate()
reviews = spark.read.parquet('/warehouse/clean/reviews/')

# 统计哪些 review 的 source_file 属于多少不同的 html pages
reviews.groupBy('movie_id').agg({'source_file':'count'}).show()

spark.stop()
```

---

## 8. 部署脚本

将脚本放在 `warehouse/.../scripts/`。

### `warehouse/relational/scripts/deploy_opengauss.sh`
```bash
#!/bin/bash
# 部署 openGauss (假设使用 tar 包安装)
set -e

echo "Starting openGauss deployment..."

# 示例：使用 Docker 运行 openGauss 容器（快速）
docker run -d --name opengauss -e GS_PASSWORD=YourPassword -p 5432:5432 containers.opengauss.org/opengauss:latest

# 等待数据库启动
sleep 20

# 执行 DDL 文件
docker cp ../../ddl/. opengauss:/ddl
docker exec -i opengauss bash -c "psql -U gaussdb -d postgres -f /ddl/dim_movies.sql"
# Repeat for other DDL

echo "openGauss deployed and DDL applied."
```

### `warehouse/distributed/scripts/deploy_hive.sh`
```bash
#!/bin/bash
# 伪指令: 在单机上部署 Hive (需要 Java + Hadoop 安装)
set -e

echo "This script outlines steps for Hive setup. For production follow Apache official docs."
# Download Hive (example)
HIVE_VER=3.1.2
wget https://archive.apache.org/dist/hive/hive-${HIVE_VER}/apache-hive-${HIVE_VER}-bin.tar.gz
tar -xzf apache-hive-${HIVE_VER}-bin.tar.gz -C /opt/
ln -s /opt/apache-hive-${HIVE_VER}-bin /opt/hive

# Configure HIVE_HOME, add to PATH, configure hive-site.xml to point metastore DB

echo "Hive binaries installed. Configure hive-site.xml and start metastore and hive server2."
```

### `warehouse/graph/scripts/deploy_neo4j.sh`
```bash
#!/bin/bash
# 用于向远程 Neo4j Aura 实例提交约束和基础导入脚本（通过 HTTP Query API）
# 请替换 NEO4J_API_KEY 或 使用 Basic auth
CONNECTION_URL="neo4j+s://cce74607.databases.neo4j.io"
NEO4J_QUERY_URL="https://cce74607.databases.neo4j.io/db/neo4j/query/v2"
AUTH_USER="neo4j"
AUTH_PASS="<YOUR_PASSWORD>" # 你在 Neo4j Aura 控制台获得的密码

# 创建约束示例
curl -s -X POST ${NEO4J_QUERY_URL} \
  -H "Content-Type: application/json; charset=UTF-8" \
  -u ${AUTH_USER}:${AUTH_PASS} \
  -d '{"statements":[{"cypher":"CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE;"}]}'

echo "Neo4j constraints applied (response code: $?)."
```

> **注意**: 对于 Neo4j Aura，请使用控制台生成的用户名/密码并将敏感信息放入 `vault` 或 `.env`，避免明文存储。

---

## 9. 兼容性与迁移说明
- openGauss 与 PostgreSQL 在 SQL 层高度兼容，若需从 Postgres 迁移，SQL 语句多数可复用；但 openGauss 在企业版有自有功能，注意分区与并行语法差异。
- Hive 表 DDL 指向 HDFS 路径，ETL 应保证 Parquet 的 schema 与 Hive DDL 匹配。
- Neo4j 使用 Cypher，若使用 Aura 通过 HTTP Query API 执行语句；若使用自托管可用 `neo4j-admin import` 进行大数据导入。

---

## 10. 下一步建议（交付准备）
1. 将上述 DDL 文件放入仓库相应目录并提交。2. 在测试环境运行 `warehouse/relational/scripts/deploy_opengauss.sh`，执行 `warehouse/relational/tests/*.sql` 验证。3. 在 Hive 中创建外部表并将 Parquet 文件上载到 HDFS `warehouse/clean/` 路径。4. 通过 PySpark 运行 `movie_statistics.py` 生成样例统计并将常用聚合写入 openGauss。


---


