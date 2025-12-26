CREATE DATABASE IF NOT EXISTS movie_dw;
USE movie_dw;

-- 电影评论表（外部表，按年月分区）
CREATE EXTERNAL TABLE reviews_clean_amazon (
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

-- ====================================
-- Staging表(必须创建!) - 用于接收PyHive上传的数据
-- ====================================
DROP TABLE IF EXISTS reviews_staging;
CREATE TABLE reviews_staging (
  asin STRING,
  user_id STRING,
  profile_name STRING,
  helpfulness STRING,
  score DOUBLE,
  review_unix BIGINT,
  review_summary STRING,
  review_text STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','  -- 如果你的数据是CSV,改成 ','
LINES TERMINATED BY '\n'
STORED AS TEXTFILE;        -- staging表用TEXTFILE,方便插入

-- 电影元数据表
CREATE EXTERNAL TABLE IF NOT EXISTS movies_meta (
  movie_id STRING,
  title STRING,
  release_date DATE,
  genres ARRAY<STRING>,
  director ARRAY<STRING>,
  actors ARRAY<STRING>,
  starring ARRAY<STRING>,
  versions ARRAY<STRING>,
  source_files ARRAY<STRING>   -- 多网页/多来源
)
STORED AS PARQUET
LOCATION '/warehouse/clean/movies_meta/';
