SET hive.execution.engine=mr;
SET hive.vectorized.execution.enabled=false;
SET hive.auto.convert.join=false;
SET hive.stats.autogather=false;

CREATE DATABASE IF NOT EXISTS movie_dw;
USE movie_dw;

-- 电影评论表（外部表，按年月分区）
CREATE EXTERNAL TABLE IF NOT EXISTS reviews_clean_amazon (
  asin STRING COMMENT 'product/productId',
  user_id STRING COMMENT 'review/userId',
  profile_name STRING COMMENT 'review/profileName',
  helpfulness STRING COMMENT 'review/helpfulness, e.g. 2/3',
  score DOUBLE COMMENT 'review/score',
  review_unix BIGINT COMMENT 'review/time (unix)',
  review_summary STRING COMMENT 'review/summary',
  review_text STRING COMMENT 'review/text'
)
PARTITIONED BY (year INT, month INT)
STORED AS PARQUET
LOCATION '/warehouse/clean/reviews_amazon/';

STORED AS PARQUET
LOCATION '/warehouse/clean/movies_meta/';

CREATE EXTERNAL TABLE IF NOT EXISTS movies_meta_dw (
  asin STRING,
  title STRING,
  release_date DATE,
  genres ARRAY<STRING>,
  director ARRAY<STRING>,
  actors ARRAY<STRING>,
  starring ARRAY<STRING>,
  versions ARRAY<STRING>,
  source_files ARRAY<STRING>,
  release_year INT,    -- 时间维度字段（用于统计）
  release_quarter INT,
  release_month INT,
  release_week INT
)
PARTITIONED BY (
  p_year INT,
  p_month INT
)
STORED AS PARQUET
LOCATION '/warehouse/clean/movies_meta_dw/';

