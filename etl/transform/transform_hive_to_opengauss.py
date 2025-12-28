#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
from pymysql.cursors import SSCursor

SRC_DB = 'amazon_movies'
MYSQL_CFG = dict(
    host='localhost', user='root', password='zd205428',
    charset='utf8mb4', cursorclass=SSCursor
)

SQLS = {
    'create_dim_movies': """
        CREATE TABLE IF NOT EXISTS dim_movies (
            title VARCHAR(512) PRIMARY KEY, movie_id VARCHAR(64) UNIQUE,
            release_quarter DATETIME, release_date DATE,
            release_year SMALLINT, release_month TINYINT, release_week TINYINT,
            genres JSON, director JSON, versions JSON
        )
    """,
    # 重点：指定 COLLATE
    'create_dim_actors': """
        CREATE TABLE IF NOT EXISTS dim_actors (
            actor_id INT AUTO_INCREMENT PRIMARY KEY,
            actor_name VARCHAR(255) NOT NULL COLLATE utf8mb4_0900_ai_ci,
            UNIQUE KEY uk_name (actor_name)
        )
    """,
    'create_movie_actor': """
        CREATE TABLE IF NOT EXISTS movie_actor (
            movie_id VARCHAR(64), actor_id INT, is_lead TINYINT(1),
            PRIMARY KEY (movie_id, actor_id)
        )
    """,
    'create_fact_reviews': """
        CREATE TABLE IF NOT EXISTS fact_reviews (
            review_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            movie_id VARCHAR(64), user_id TEXT, profile_name TEXT, helpfulness TEXT,
            score DECIMAL(3,1), review_time DATETIME,
            review_year SMALLINT, review_quarter TINYINT, review_month TINYINT, review_week TINYINT,
            review_summary TEXT, review_text TEXT, INDEX (movie_id)
        )
    """,

    'ins_dim_actors': """
        INSERT IGNORE INTO dim_actors (actor_name)
        WITH RECURSIVE seq AS (SELECT 0 n UNION ALL SELECT n+1 FROM seq WHERE n<19),
        actors_json AS (
            SELECT TRIM(REPLACE(REPLACE(REPLACE(REPLACE(
                JSON_UNQUOTE(JSON_EXTRACT(actors, CONCAT('$[', n, ']'))), '\\'', ''), '"', ''), '\n', ' '), '\t', ' ')) AS name
            FROM movies_clean, seq WHERE JSON_EXTRACT(actors, CONCAT('$[', n, ']')) IS NOT NULL
        ),
        starring_all AS (
            SELECT CASE WHEN starring LIKE '[%' THEN
                TRIM(REPLACE(REPLACE(REPLACE(REPLACE(
                    JSON_UNQUOTE(JSON_EXTRACT(starring, CONCAT('$[', n, ']'))), '\\'', ''), '"', ''), '\n', ' '), '\t', ' '))
            ELSE
                TRIM(REPLACE(REPLACE(REPLACE(REPLACE(
                    SUBSTRING_INDEX(SUBSTRING_INDEX(starring, ',', n+1), ',', -1), '\\'', ''), '"', ''), '\n', ' '), '\t', ' '))
            END AS name
            FROM movies_clean, seq
            WHERE starring IS NOT NULL AND TRIM(starring)!=''
              AND ((starring LIKE '[%' AND JSON_EXTRACT(starring, CONCAT('$[', n, ']')) IS NOT NULL)
                OR (starring NOT LIKE '[%' AND n< (LENGTH(starring)-LENGTH(REPLACE(starring,',',''))+1)))
        )
        SELECT DISTINCT name FROM (SELECT * FROM actors_json UNION ALL SELECT * FROM starring_all) t WHERE name!=''
    """,

    'ins_dim_movies': """
        INSERT IGNORE INTO dim_movies (title, movie_id, release_date, release_year,
            release_month, release_week, release_quarter, genres, director, versions)
        SELECT title, movie_id, release_date, YEAR(release_date), MONTH(release_date),
            WEEK(release_date, 3), STR_TO_DATE(DATE_FORMAT(release_date, '%Y-%m-01'), '%Y-%m-%d'),
            genres, director, versions
        FROM movies_clean
    """,

    # 重点：JOIN 时添加 COLLATE
    'ins_movie_actor_lead': """
        INSERT INTO movie_actor (movie_id, actor_id, is_lead)
        WITH RECURSIVE seq AS (SELECT 0 n UNION ALL SELECT n+1 FROM seq WHERE n<19)
        SELECT m.movie_id, a.actor_id, 1 FROM (
            SELECT movie_id, CASE WHEN starring LIKE '[%' THEN
                TRIM(REPLACE(REPLACE(REPLACE(REPLACE(
                    JSON_UNQUOTE(JSON_EXTRACT(starring, CONCAT('$[', n, ']'))), '\\'', ''), '"', ''), '\n', ' '), '\t', ' '))
            ELSE
                TRIM(REPLACE(REPLACE(REPLACE(REPLACE(
                    SUBSTRING_INDEX(SUBSTRING_INDEX(starring, ',', n+1), ',', -1), '\\'', ''), '"', ''), '\n', ' '), '\t', ' '))
            END AS name
            FROM movies_clean, seq
            WHERE starring IS NOT NULL AND TRIM(starring)!=''
              AND ((starring LIKE '[%' AND JSON_EXTRACT(starring, CONCAT('$[', n, ']')) IS NOT NULL)
                OR (starring NOT LIKE '[%' AND n< (LENGTH(starring)-LENGTH(REPLACE(starring,',',''))+1)))
        ) t
        JOIN movies_clean m ON m.movie_id=t.movie_id
        JOIN dim_actors a ON a.actor_name COLLATE utf8mb4_0900_ai_ci = t.name COLLATE utf8mb4_0900_ai_ci
        ON DUPLICATE KEY UPDATE is_lead=1
    """,

    'ins_movie_actor_notlead': """
        INSERT INTO movie_actor (movie_id, actor_id, is_lead)
        WITH RECURSIVE seq AS (SELECT 0 n UNION ALL SELECT n+1 FROM seq WHERE n<19)
        SELECT m.movie_id, a.actor_id, 0 FROM (
            SELECT movie_id, TRIM(REPLACE(REPLACE(REPLACE(REPLACE(
                JSON_UNQUOTE(JSON_EXTRACT(actors, CONCAT('$[', n, ']'))), '\\'', ''), '"', ''), '\n', ' '), '\t', ' ')) AS name
            FROM movies_clean, seq
            WHERE JSON_EXTRACT(actors, CONCAT('$[', n, ']')) IS NOT NULL
        ) t
        JOIN movies_clean m ON m.movie_id=t.movie_id
        JOIN dim_actors a ON a.actor_name COLLATE utf8mb4_0900_ai_ci = t.name COLLATE utf8mb4_0900_ai_ci
        ON DUPLICATE KEY UPDATE is_lead=VALUES(is_lead)
    """,

    'ins_fact_reviews': """
        INSERT INTO fact_reviews (movie_id, user_id, profile_name, helpfulness,
            score, review_time, review_year, review_quarter, review_month, review_week, review_summary, review_text)
        SELECT productid, userid, profilename, helpfulness, CAST(score AS DECIMAL(3,1)),
            FROM_UNIXTIME(CAST(`time` AS UNSIGNED)), YEAR(FROM_UNIXTIME(CAST(`time` AS UNSIGNED))),
            QUARTER(FROM_UNIXTIME(CAST(`time` AS UNSIGNED))), MONTH(FROM_UNIXTIME(CAST(`time` AS UNSIGNED))),
            WEEK(FROM_UNIXTIME(CAST(`time` AS UNSIGNED)), 3), summary, text
        FROM reviews
    """
}


def run_sql(sql, conn, msg):
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        print(f'[OK] {msg}  affected: {cur.rowcount}')


def main():
    with pymysql.connect(**MYSQL_CFG) as conn:
        conn.select_db(SRC_DB)
        # 先清理旧表（如果存在）
        for tbl in ['movie_actor', 'fact_reviews', 'dim_actors', 'dim_movies']:
            try:
                with conn.cursor() as cur:
                    cur.execute(f"DROP TABLE IF EXISTS {tbl}")
                conn.commit()
                print(f'[DROP] {tbl}')
            except:
                pass

        # 重建表并导数据
        for k in ['create_dim_movies', 'create_dim_actors', 'create_movie_actor', 'create_fact_reviews']:
            run_sql(SQLS[k], conn, k)
        run_sql(SQLS['ins_dim_actors'], conn, 'ins_dim_actors')
        run_sql(SQLS['ins_dim_movies'], conn, 'ins_dim_movies')
        run_sql(SQLS['ins_movie_actor_lead'], conn, 'ins_movie_actor_lead')
        run_sql(SQLS['ins_movie_actor_notlead'], conn, 'ins_movie_actor_notlead')
        run_sql(SQLS['ins_fact_reviews'], conn, 'ins_fact_reviews')
        print('=== All done! 4 new tables ready in', SRC_DB)


if __name__ == '__main__':
    main()