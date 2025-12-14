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