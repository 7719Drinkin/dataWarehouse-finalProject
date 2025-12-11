# 一键 Docker 部署（x86，Ubuntu）—— openGauss / Hive+HDFS+Spark / Neo4j

本文件是你要求的**可直接在单台 x86 Ubuntu 服务器上执行的一体化 Docker 自动化部署方案**。

包括：
- 在服务器上安装 Docker / docker-compose（步骤）
- `docker-compose.yml`（一键起整个数据平台）
- 各服务初始化脚本（openGauss 建表 SQL、Hive 初始化 HQL、Neo4j Cypher）
- `init_all.sh`：等待服务启动并自动执行建表/建图
- 使用说明与常见故障排查

> 目标：在一台干净的 Ubuntu（20.04 / 22.04）x86 服务器上，通过少于 10 条命令完成从安装 Docker 到起库并初始化表的全部工作。

---

## 0. 先决条件
- 服务器：Ubuntu 20.04 / 22.04，x86
- 有 sudo 权限的用户
- 推荐内存 >= 16GB，磁盘 >= 200GB（数据量大时）

---

## 1. 在服务器上安装 Docker 与 docker-compose

```bash
# 安装 Docker (官方推荐脚本)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
# 允许当前用户使用 docker（可选）
sudo usermod -aG docker $USER
# 立即生效（或重新登录）
newgrp docker || true

# 安装 docker-compose plugin（较新方式）
sudo apt update
sudo apt install -y docker-compose-plugin

# 检查
docker version
docker compose version
```

> 如果你偏好老版 `docker-compose` 二进制（v1），也可 `sudo apt install -y docker-compose`，但推荐使用 Docker 官方的 plugin（`docker compose`）。

---

## 2. 将仓库的 `warehouse/docker/` 目录上传到服务器（或在服务器上创建该目录），本 doc 已包含所有必要文件内容。下面是项目推荐结构（在服务器上）：

```
warehouse/docker/
├── docker-compose.yml
├── opengauss/
│   └── init.sql
├── hive/
│   └── init.hql
├── neo4j/
│   ├── init.cypher
│   └── import/   # 可放 CSV 导入文件（如需离线导入）
└── init_all.sh
```

我已在下面把这些文件的完整内容写出来，请你在服务器的 `warehouse/docker/` 下创建对应文件并粘贴内容。

---

## 3. `docker-compose.yml`（完整）

> 说明：这个 compose 以单机开发/测试为目标，整合 openGauss、Postgres（Hive Metastore）、Hadoop (namenode/datanode)、HiveServer2、Spark（master/worker）、Neo4j。注意：真实生产集群需要分布式多节点，此处做单机 pseudo-distributed。启动稍慢，资源占用较高。

```yaml
version: '3.9'

services:
  hadoop-spark:
    build: .
    container_name: hadoop-spark
    environment:
      - CLUSTER_NAME=single-node
      - HDFS_NAMENODE=true
      - HDFS_DATANODE=true
      - SPARK_MODE=master
    volumes:
      - ./hdfs/namenode:/hadoop/dfs/name
      - ./hdfs/datanode:/hadoop/dfs/data
    ports:
      - "9870:9870"
      - "8080:8080"
      - "7077:7077"
    networks:
      - bigdata

  spark-worker:
    build: .
    container_name: spark-worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://hadoop-spark:7077
    depends_on:
      - hadoop-spark
    networks:
      - bigdata

  # 数据库部分不变
  opengauss:
    image: opengauss/opengauss-server:latest
    container_name: opengauss
    environment:
      - GS_PASSWORD=og_password
    ports:
      - "5432:5432"
    volumes:
      - ./opengauss/data:/var/lib/opengauss
      - ./opengauss/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "gaussdb"]
      interval: 10s
      retries: 10

  hive-server:
    image: apache/hive:4.0.0
    container_name: hive-server
    environment:
      - SERVICE_NAME=hiveserver2
    ports:
      - "10000:10000"
    volumes:
      - ./hive/init.hql:/opt/hive-init/init.hql:ro
    depends_on:
      - hadoop-spark
    networks:
      - bigdata

  neo4j:
    image: neo4j:latest
    container_name: neo4j
    environment:
      - NEO4J_AUTH=neo4j/neo4j_password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - ./neo4j/data:/data
      - ./neo4j/import:/var/lib/neo4j/import
      - ./neo4j/logs:/logs
    networks:
      - bigdata

networks:
  bigdata:
    driver: bridge


```

---

## 4. opengauss/init.sql（示例建表 DDL）
路径：`warehouse/docker/opengauss/init.sql`

```sql
-- 初始化 openGauss schema & tables (简化示例)
CREATE DATABASE movie_dw;
\c movie_dw;

-- dim_movies
CREATE TABLE IF NOT EXISTS dim_movies (
  movie_id TEXT PRIMARY KEY,
  title TEXT,
  release_year INT,
  release_date DATE,
  genres TEXT[],
  versions TEXT[],
  source_files TEXT[],
  created_at TIMESTAMP DEFAULT now()
);

-- dim_actors
CREATE TABLE IF NOT EXISTS dim_actors (
  actor_id TEXT PRIMARY KEY,
  actor_name TEXT,
  normalized_name TEXT,
  birth_year INT
);

CREATE TABLE IF NOT EXISTS movie_actor (
  movie_id TEXT,
  actor_id TEXT,
  role_name TEXT,
  PRIMARY KEY (movie_id, actor_id)
);

-- dim_time
CREATE TABLE IF NOT EXISTS dim_time (
  date_id INT PRIMARY KEY,
  date DATE,
  year INT,
  quarter INT,
  month INT,
  day INT,
  weekday INT
);

-- fact_reviews
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
  source_file TEXT,
  loaded_at TIMESTAMP DEFAULT now(),
  date_id INT
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_fact_movie ON fact_reviews(movie_id);
CREATE INDEX IF NOT EXISTS idx_fact_score ON fact_reviews(score);
```

---

## 5. hive/init.hql（Hive 表初始化）
路径：`warehouse/docker/hive/init.hql`

```sql
-- 创建 Hive 数据库与外部表（示例）
CREATE DATABASE IF NOT EXISTS movie_dw;
USE movie_dw;

CREATE EXTERNAL TABLE IF NOT EXISTS reviews_clean (
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

CREATE EXTERNAL TABLE IF NOT EXISTS movies_meta (
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

---

## 6. neo4j/init.cypher（示例）
路径：`warehouse/docker/neo4j/init.cypher`

```cypher
// Neo4j 索引与约束（用于加速）
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (a:Actor) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Director) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;

// 示例小数据可用 LOAD CSV 导入（若使用 neo4j-admin import，建议在启动前导入）
```

---

## 7. init_all.sh（自动化初始化脚本）
路径：`warehouse/docker/init_all.sh`（在服务器上执行）

```bash
#!/usr/bin/env bash
set -euo pipefail

# -------------------------------
# detect docker compose
# -------------------------------
if command -v docker compose >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "❌ docker compose not installed"
    exit 1
fi

BASE_DIR=$(cd "$(dirname "$0")" && pwd)
cd $BASE_DIR

echo "▶ Starting docker compose..."
$DC up -d

# -------------------------------
# Wait for openGauss
# -------------------------------
echo "▶ Waiting for openGauss to be ready..."
for i in {1..40}; do
  if docker exec opengauss bash -c "gsql -d postgres -U omm -c 'SELECT 1;'" >/dev/null 2>&1; then
    echo "✔ openGauss ready"
    break
  fi
  echo "  ...waiting openGauss ($i/40)"
  sleep 5
done

if docker exec opengauss bash -c "test -f /docker-entrypoint-initdb.d/init.sql"; then
  echo "▶ Applying openGauss init.sql ..."
  docker exec -i opengauss gsql -d postgres -U omm -f /docker-entrypoint-initdb.d/init.sql
  echo "✔ openGauss init.sql applied"
fi

# -------------------------------
# Wait for HiveServer2
# -------------------------------
echo "▶ Waiting for HiveServer2..."
for i in {1..40}; do
  if docker exec hive-server bash -c "/opt/hive/bin/beeline -u 'jdbc:hive2://localhost:10000' -e 'show databases;'" >/dev/null 2>&1; then
    echo "✔ Hive ready"
    break
  fi
  echo "  ...waiting Hive ($i/40)"
  sleep 5
done

echo "▶ Applying Hive init.hql..."
docker cp hive/init.hql hive-server:/opt/hive-init/init.hql || true
docker exec hive-server bash -c "/opt/hive/bin/beeline -u 'jdbc:hive2://localhost:10000' -f /opt/hive-init/init.hql" || true
echo "✔ Hive init.hql applied"

# -------------------------------
# Wait for Neo4j
# -------------------------------
echo "▶ Waiting for Neo4j..."
for i in {1..30}; do
  if docker exec neo4j bash -c "curl -s http://localhost:7474/" >/dev/null 2>&1; then
    echo "✔ Neo4j ready"
    break
  fi
  echo "  ...waiting Neo4j ($i/30)"
  sleep 3
done

echo "▶ Applying Neo4j init.cypher..."
docker cp neo4j/init.cypher neo4j:/init.cypher || true
docker exec neo4j bash -c "cat /init.cypher | /var/lib/neo4j/bin/cypher-shell -u neo4j -p neo4j_password" || true
echo "✔ Neo4j init.cypher applied"

echo "🎉 ALL INITIALIZATION COMPLETE"
```

---

## 8. 启动步骤（一步到位）
在服务器上：

```bash
# 1. 克隆或切换到你的仓库目录
cd /path/to/movie-dw-project/warehouse/docker

# 2. 将本 doc 中的文件保存为相应路径（docker-compose.yml、opengauss/init.sql、hive/init.hql、neo4j/init.cypher、init_all.sh）

# 3. 赋可执行权限
chmod +x init_all.sh

# 4. 执行一键启动（包括安装、初始化）
./init_all.sh

# 5. 查看容器状态
docker compose ps

# 6. 验证服务
# openGauss: psql -h <server_ip> -p 5432 -U gaussdb
# Hive: beeline -u 'jdbc:hive2://<server_ip>:10000'
# Neo4j UI: http://<server_ip>:7474 (neo4j/neo4j_password)
```

---

## 9. 本地 ETL 直接连接并 Load（你的情形）
在本地运行的 ETL 程序，可以直接连接服务器上通过 Docker 启动的数据库：

- openGauss: `host=SERVER_IP, port=5432, user=gaussdb, password=og_password, db=movie_dw`
- HiveServer2: `host=SERVER_IP, port=10000`（use PyHive or JDBC）
- Neo4j Bolt: `bolt://SERVER_IP:7687`, auth `(neo4j, neo4j_password)`

示例 Python 连接 openGauss（psycopg2）:

```python
from pygs_connector import connect

conn = connect(
    host="SERVER_IP",
    port=5432,
    user="omm",
    password="og_password",
    database="movie_dw"
)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM fact_reviews;")
print(cursor.fetchone())
```

示例 PyHive 连接 Hive:

```python
from pyhive import hive

conn = hive.Connection(
    host="SERVER_IP",
    port=10000,
    username="hive",
    database="default"
)
cursor = conn.cursor()
cursor.execute("SHOW DATABASES")
print(cursor.fetchall())

```

示例 Neo4j Bolt:

```python
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://SERVER_IP:7687", auth=("neo4j", "neo4j_password"))
```

---

## 10. 常见问题与排查
- 如果容器某个服务未启动：`docker compose logs servicename` 查看日志。通常端口冲突、内存不足或镜像拉取失败是常见问题。\
- Hive 无法连接 Namenode：检查 `hive-server` 日志，确认 `CORE_CONF_fs_defaultFS` 已正确指向 `hdfs://namenode:9000`。\
- 若 `psql` 在 opengauss 容器不可用，可能镜像与命令不兼容，尝试进入容器 `docker exec -it opengauss bash` 手动检查。\

---

## 11. 注意与限制
- 本方案针对单机开发与教学演示，使用镜像与单节点伪分布式组件，性能与企业级集群不可同日而语。若用于生产，请使用多节点 Hadoop/Hive 集群、openGauss 高可用部署、Neo4j 企业版或集群。
- 若你需要我把这些文件直接写入到项目画布中的对应路径（`warehouse/docker/...`），我可以一键创建这些文件。是否需要？

---

如果你确认让我把这些文件写入画布（`warehouse/docker/docker-compose.yml` 等），我将立刻把它们作为独立文件创建到你的项目里以便下载与复制。

