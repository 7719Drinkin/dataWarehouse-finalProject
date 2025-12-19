CREATE DATABASE IF NOT EXISTS movie_dw;
USE movie_dw;

-- 电影评论表（外部表，按年月分区）
DROP TABLE IF EXISTS reviews_clean;
CREATE EXTERNAL TABLE IF NOT EXISTS reviews_clean (
  review_id STRING,
  movie_id STRING,
  user_id STRING,
  profile_name STRING,
  score DOUBLE,
  review_time TIMESTAMP,
  review_unix BIGINT,
  review_text STRING,
  source STRING,           -- snap / amazon
  source_file STRING       -- 原始文本文件或网页URL
)
PARTITIONED BY (year INT, month INT)
STORED AS PARQUET
LOCATION '/warehouse/clean/reviews/';

-- 电影元数据表
DROP TABLE IF EXISTS movies_meta;
CREATE EXTERNAL TABLE IF NOT EXISTS movies_meta (
  movie_id STRING,
  title STRING,
  release_date DATE,
  genres ARRAY<STRING>,
  director STRING,
  actors ARRAY<STRING>,
  starring ARRAY<STRING>,
  versions ARRAY<STRING>,
  source_files ARRAY<STRING>   -- 多网页/多来源
)
STORED AS PARQUET
LOCATION '/warehouse/clean/movies_meta/';
