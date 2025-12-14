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