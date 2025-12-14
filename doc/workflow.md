# Movie Data Warehouse Project - 单机 Docker 全栈部署工作流程

---

## 1. 数据仓库准备

### 使用到的数据库

* **关系型数据库**: 华为 openGauss，用于存储电影事实表和维度表，适合高效执行结构化查询，如统计电影数量、评分分布等。
* **分布式存储与计算**: Hive + HDFS + SparkSQL，适合大数据量的批处理和复杂分析，例如全量评论统计、时间序列分析。
* **图数据存储**: Neo4j，用于存储电影与演员、导演的关系图，适合执行复杂关系查询，如协作关系和最受关注演员组合。

* **下载参考网站**: 
  openGauss: `https://opengauss.org/zh/download/`
  Hive: `https://www.apache.org/dyn/closer.cgi/hive/`
  Neo4j: `https://neo4j.com/docs/operations-manual/current/installation/linux/`

* **Neo4j免费实例连接**
  ID: `cce74607`
  Connection URI: `neo4j+s://cce74607.databases.neo4j.io`
  Query API URL:  `https://cce74607.databases.neo4j.io/db/{databaseName}/query/v2`



### 部署方式

本项目采用 Docker Compose 方式在单台服务器上部署全套环境。

#### 1. 安装 Docker 与 Docker Compose

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
docker --version
docker-compose --version
```

#### 2. Docker Compose 配置示例

```yaml
version: '3.8'
services:
  opengauss:
    image: containers.opengauss.org/opengauss:latest
    container_name: opengauss
    environment:
      GS_PASSWORD: "YourStrongPassword"
    ports:
      - "5432:5432"
    volumes:
      - ./warehouse/relational/data:/var/lib/opengauss/data

  hive:
    image: bde2020/hive:2.3.2-postgresql-metastore
    container_name: hive
    environment:
      - HIVE_METASTORE_USER=hive
      - HIVE_METASTORE_PASSWORD=hive
    ports:
      - "10000:10000"
    depends_on:
      - opengauss

  neo4j:
    image: neo4j:5
    container_name: neo4j
    environment:
      - NEO4J_AUTH=neo4j/test
    ports:
      - "7474:7474"
      - "7687:7687"
```

#### 3. 启动容器

```bash
docker-compose up -d
docker ps
docker logs opengauss
```

### 工作内容

* 配置和部署数据库容器
* 建立数据库及初始模式（DDL）
* 输出数据库访问地址、端口和连接配置文件（.env.example）

### 产出

* `warehouse/relational/ddl/` 中的 SQL 脚本
* 运行中的 openGauss、Hive/HDFS、Neo4j 容器

---

## 2. ETL 流程

### 数据源

```
├── data_source/
│   ├── movies.txt          # SNAP 原始文本数据
│   ├── html_raw/           # 253,059 个网页 HTML
│   ├── metadata/           # 第三方电影数据（可选）
│   └── sample/             # 调试用小样本
```

**注意**: `data_source/` 数据过大，**不上传至 GitHub**，在 `.gitignore` 中添加 `data_source/`。

### 处理策略

1. **本地 ETL**: 在本地机器进行 Extract、Transform 处理，将中间结果输出为较小的 JSONL 文件，例如 `etl/output/merged_reviews.jsonl`。
2. **本地 Load 到服务器数据库**: 通过本地连接服务器上的数据库，将 JSONL 文件直接写入容器内数据库。无需在服务器上上传原始数据。

## 本地 ETL 直接连接并 Load
首先，先在数据库的`root`目录下进入`dataWarehouse-finalProject/warehouse/docker`目录，运行`./start_container.sh`，启动所有服务（数据库 + Hadoop + Spark）

然后，在本地运行的 ETL 程序，可以直接连接服务器上通过 Docker 启动的数据库：

示例 Python 连接 openGauss（psycopg2）:

```python
from pygs_connector import connect

conn = connect(
    host="SERVER_IP",
    port=5432,
    user="omm",
    password="GaussDB@2025",
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
说明：
- Hive 表数据存储在容器内 HDFS
- 本地仅通过 HiveServer2 执行 SQL，不直接操作 HDFS

示例 Neo4j Bolt:
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://SERVER_IP:7687",
    auth=("neo4j", "neo4j_password")
)

```

### Extract

**文件位置**: `etl/extract/`

* `parse_snap.py`: 解析 `movies.txt` → `raw_reviews.jsonl`
* `parse_html.py`: 解析 `html_raw/` HTML → `html_extracted.jsonl`

### Transform

**文件位置**: `etl/transform/`

* `normalize_fields.py`: 标准化电影名称、日期、评分、演员字段
* `dedupe_and_match.py`: 实体去重与模糊匹配
* `merge_reviews_meta.py`: 合并 SNAP 评论和 HTML 提取数据

### Load

**文件位置**: `etl/load/`

* `load_postgres.py`: 本地 Load JSONL → 服务器 openGauss
* `load_hive.py`: 本地 Load JSONL → 服务器 Hive/HDFS
* `load_neo4j.py`: 本地 Load JSONL → 服务器 Neo4j

**操作方法**:

```bash
python etl/load/load_postgres.py --host SERVER_IP --port 5432
python etl/load/load_hive.py --host SERVER_IP --port 10000
python etl/load/load_neo4j.py --host SERVER_IP --port 7687
```

### 产出

* 服务器数据库中存储完整数据，可直接供后端 API 调用

---

## 3. 后端

**文件位置**: `backend/`

* FastAPI 提供 API 接口查询、统计和血缘
* 调用已加载的 openGauss/Hive/Neo4j
* 支持性能测试接口

**技术栈**: Python + FastAPI + asyncpg + PyHive + neo4j.Driver

**运行**:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 4. 前端

**文件位置**: `frontend/`

* React 页面展示查询结果、统计图表、性能对比、血缘可视化
* 调用 FastAPI 接口获取数据

**运行**:

```bash
npm install
npm start
```

---

## 5. 数据流与协同说明

```
# 数据流示意
本地 data_source/ --> ETL/extract --> ETL/transform --> merged_reviews.jsonl --> 本地 Load --> 服务器 openGauss/Hive/Neo4j --> backend API --> frontend React UI
```

* 本地生成 JSONL，减少上传数据量
* 本地直接连接服务器 Load 数据，避免上传巨量原始数据
* 数据治理、血缘、性能测试与提交内容保持一致

---

## 6. 提交内容映射

* ETL 脚本: `etl/`
* 数据存储设计: `warehouse/`
* 数据表测试用例: `warehouse/.../tests/`
* 查询统计程序: `backend/routers/` 和 `backend/services/`
* 项目报告与答辩: `report/`
* 数据治理与血缘: `governance/`
* 性能测试: `performance/`
* `.gitignore` 配置: 忽略 `data_source/`
