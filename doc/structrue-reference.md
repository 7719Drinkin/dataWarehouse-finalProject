```
movie-dw-project/
│
├── README.md                         # 项目说明（重要）
├── requirements.txt                  # Python依赖
├── .env.example                      # 数据库连接配置模板
│
├── data_source/                      # 原始数据
│   ├── movies.txt                    # SNAP reviews（原始 .txt / gzip）
│   ├── html_raw/                     # 253,059 个网站页面的 HTML 原始文件
│   ├── metadata/                     # 第三方电影数据 （可选）
│   └── sample/                       # 小样本数据用于调试 （可选）
│
├── etl/                              # ETL 主体
│   ├── extract/
│   │   ├── parse_snap.py             # 解析 movies.txt → raw_reviews.jsonl
│   │   └── parse_html.py             # 解析 html_raw → html_extracted.jsonl
│   │
│   ├── transform/
│   │   ├── normalize_fields.py       # 名称/日期/score/availability 标准化
│   │   ├── dedupe_and_match.py       # 电影实体合并 / ASIN/title fuzzy match
│   │   └── merge_reviews_meta.py     # 合并 SNAP reviews 与 HTML 提取结果（核心）
│   │
│   ├── load/
│   │    ├── load_postgres.py         # 加载到关系型数据库
│   │    ├── load_hive.py             # 加载到Hive（HDFS）
│   │    ├── load_neo4j.py            # 加载到图数据库
│   │    └── load_duckdb.py           # 可选：本地分析用
│   │
│   ├── pipeline.py                   # ETL 主入口（可一键运行）
│   └── etl_config.yaml               # ETL 配置文件
│
├── warehouse/docker/
|   ├── docker-compose.yml
|   ├── opengauss/
|   │   └── init.sql
|   ├── hive/
|   │   └── init.hql
|   ├── neo4j/
|   │   ├── init.cypher
|   │   └── import/   # 可放 CSV 导入文件（如需离线导入）
|   └── init_all.sh
│
├── backend/                          # 数据应用接口（FastAPI）
│   ├── main.py
│   ├── routers/
│   │    ├── movies.py                # 查询：电影
│   │    ├── actors.py                # 查询：演员
│   │    ├── directors.py             # 查询：导演
│   │    ├── stats.py                 # 三库性能测试接口
│   │    └── lineage.py               # 溯源查询接口
│   ├── services/
│   │    ├── pg_service.py
│   │    ├── hive_service.py
│   │    ├── neo4j_service.py
│   │    └── performance_service.py
│   └── db/                           # 数据库连接管理
│        ├── postgres_pool.py
│        ├── hive_conn.py
│        └── neo4j_conn.py
│
├── frontend/                         # React Web UI
│   ├── public/
│   ├── src/
│   │    ├── api/                     # 调用 FastAPI
│   │    ├── components/              # 图表、表格
│   │    ├── pages/
│   │    │    ├── QueryPage.jsx
│   │    │    ├── StatCompare.jsx     # 三库性能对比图表
│   │    │    └── Lineage.jsx
│   │    └── hooks/
│   └── package.json
│
├── governance/                       # 数据治理体系
│   ├── lineage/                      # 数据血缘
│   │    └── lineage_graph.json
│   ├── quality/                      # 数据质量验证
│   │    ├── dq_rules.yaml
│   │    └── dq_check.py
│   ├── metadata/                     # 元数据管理
│   │    └── movie_metadata.json
│   ├── logs/
│   └── governance_report.md
│
├── performance/                      # 性能测试
│   ├── benchmark_queries.sql
│   ├── run_benchmark.py
│   └── benchmark_results.json
│
└── report/                           # 最终提交内容
    ├── final_report.pdf
    ├── er_model.png
    ├── ppt/
    └── appendix/
```