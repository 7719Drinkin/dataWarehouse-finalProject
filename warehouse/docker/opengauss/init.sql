-- 初始化 openGauss schema & tables (简化示例)
CREATE DATABASE movie_dw;
\c movie_dw;

-- dim_movies
DROP TABLE IF EXISTS dim_movies;
CREATE TABLE IF NOT EXISTS dim_movies (
  movie_id TEXT PRIMARY KEY,
  title TEXT,
  release_date DATE,
  genres TEXT[],
  director TEXT,
  versions TEXT[]
);

-- dim_actors
DROP TABLE IF EXISTS dim_actors;
CREATE TABLE IF NOT EXISTS dim_actors (
  actor_id TEXT PRIMARY KEY,
  actor_name TEXT
);

-- movie_actor
DROP TABLE IF EXISTS movie_actor;
CREATE TABLE IF NOT EXISTS movie_actor (
  movie_id TEXT,
  actor_id TEXT,
  PRIMARY KEY (movie_id, actor_id)
);

-- fact_reviews
DROP TABLE IF EXISTS fact_reviews;
CREATE TABLE IF NOT EXISTS fact_reviews (
  review_id BIGSERIAL PRIMARY KEY,
  movie_id TEXT NOT NULL,
  user_id TEXT,
  score NUMERIC(3,1),
  review_time TIMESTAMP,
  review_text TEXT
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_fact_movie ON fact_reviews(movie_id);
CREATE INDEX IF NOT EXISTS idx_fact_score ON fact_reviews(score);