"""
hive_queries.py
Hive 数据库查询语句集合（支持数据应用需求）

注意：本项目的 Hive 表结构以运行环境为准（HS2 上实际 DESCRIBE 结果）：
- movie_dw.movies_meta_dw 主键列为 movie_id（非 asin）
- movie_dw.reviews_clean_amazon 主键列为 product_id（非 asin）
"""

class HiveQueries:
    """Hive 数据库查询语句类"""

    # =======================
    # 一、时间维度查询/统计
    # =======================
    # 按年份查询电影
    MOVIES_BY_YEAR = """
        SELECT *
        FROM movie_dw.movies_meta_dw
        WHERE release_year = {year}
    """

    # 按季度查询电影数量
    MOVIES_BY_QUARTER = """
        SELECT release_quarter, COUNT(*) AS movie_count
        FROM movie_dw.movies_meta_dw
        WHERE release_year = {year}
        GROUP BY release_quarter
        ORDER BY release_quarter
    """

    # 按月份查询电影数量
    MOVIES_BY_MONTH = """
        SELECT release_month, COUNT(*) AS movie_count
        FROM movie_dw.movies_meta_dw
        WHERE release_year = {year}
        GROUP BY release_month
        ORDER BY release_month
    """

    # 按周查询电影数量
    MOVIES_BY_WEEK = """
        SELECT release_week, COUNT(*) AS movie_count
        FROM movie_dw.movies_meta_dw
        WHERE release_year = {year}
        GROUP BY release_week
        ORDER BY release_week
    """

    # 某天新增电影数量（按日期）
    MOVIES_BY_DAY = """
        SELECT COUNT(*) AS movie_count
        FROM movie_dw.movies_meta_dw
        WHERE release_date = '{date}'
    """

    # 某时间段电影及评价统计
    MOVIES_BY_TIME_RANGE = """
        SELECT m.movie_id AS movie_id, m.title,
               COUNT(1) AS review_count,
               AVG(r.score) AS avg_score
        FROM movie_dw.movies_meta_dw m
        LEFT JOIN movie_dw.reviews_clean_amazon r ON m.movie_id = r.product_id
        WHERE m.release_date >= '{start_date}' AND m.release_date <= '{end_date}'
        GROUP BY m.movie_id, m.title
        ORDER BY avg_score DESC
    """

    # 按时间动态查询电影
    MOVIES_BY_TIME_DYNAMIC_TEMPLATE = """
        WITH filtered_movies AS (
          SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres
          FROM movie_dw.movies_meta_dw m
          {where_clause}
        ),
        reviews_agg AS (
          SELECT
            r.product_id AS movie_id,
            COUNT(1) AS review_count,
            AVG(r.score) AS avg_score
          FROM movie_dw.reviews_clean_amazon r
          JOIN filtered_movies fm
            ON fm.movie_id = r.product_id
          GROUP BY r.product_id
        )
        SELECT
          fm.movie_id,
          fm.title,
          fm.director,
          fm.genres,
          NVL(ra.review_count, 0) AS review_count,
          NVL(ra.avg_score, 0) AS rating
        FROM filtered_movies fm
        LEFT JOIN reviews_agg ra
          ON fm.movie_id = ra.movie_id
        ORDER BY rating DESC
    """

    # =======================
    # 二、电影维度查询/统计
    # =======================
    MOVIES_BY_DIRECTOR = """
        SELECT *
        FROM movie_dw.movies_meta_dw
        WHERE array_contains(director, '{director}')
    """

    MOVIES_BY_ACTOR_STARRING = """
        SELECT *
        FROM movie_dw.movies_meta_dw
        WHERE array_contains(starring, '{actor}')
    """

    MOVIES_BY_ACTOR_PARTICIPATED = """
        SELECT *
        FROM movie_dw.movies_meta_dw
        WHERE array_contains(actors, '{actor}')
    """

    MOVIES_BY_GENRE = """
        SELECT *
        FROM movie_dw.movies_meta_dw
        WHERE array_contains(genres, '{genre}')
    """

    MOVIES_BY_PERSON_TEMPLATE = """
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres,
            COUNT(1) AS review_count,
            NVL(AVG(r.score), 0) AS rating
        FROM movie_dw.movies_meta_dw m
        LEFT JOIN movie_dw.reviews_clean_amazon r ON m.movie_id = r.product_id
        {where_clause}
        GROUP BY m.movie_id, m.title, m.director, m.genres
        ORDER BY rating DESC
    """

    MOVIES_BY_MULTI_CONDITION_TEMPLATE = """
        WITH filtered_movies AS (
          SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres
          FROM movie_dw.movies_meta_dw m
          {where_clause}
        ),
        reviews_agg AS (
          SELECT
            r.product_id AS movie_id,
            COUNT(1) AS review_count,
            AVG(r.score) AS avg_score
          FROM movie_dw.reviews_clean_amazon r
          JOIN filtered_movies fm
            ON fm.movie_id = r.product_id
          GROUP BY r.product_id
        ),
        joined AS (
          SELECT
            fm.movie_id,
            fm.title,
            fm.director,
            fm.genres,
            NVL(ra.avg_score, 0) AS rating,
            NVL(ra.review_count, 0) AS review_count
          FROM filtered_movies fm
          LEFT JOIN reviews_agg ra
            ON fm.movie_id = ra.movie_id
        )
        SELECT
          movie_id,
          title,
          director,
          genres,
          rating,
          review_count
        FROM joined
        {having_clause}
        ORDER BY rating DESC
    """

    # =======================
    # 三、用户评价相关
    # =======================
    HIGH_RATED_MOVIES = """
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres,
            AVG(r.score) AS rating,
            COUNT(1) AS review_count
        FROM movie_dw.movies_meta_dw m
        JOIN movie_dw.reviews_clean_amazon r ON m.movie_id = r.product_id
        GROUP BY m.movie_id, m.title, m.director, m.genres
        HAVING AVG(r.score) >= {min_score} AND COUNT(1) >= {min_reviews}
        ORDER BY rating DESC
    """

    REVIEWS_BY_SCORE_RANGE = """
        SELECT product_id AS movie_id, COUNT(*) AS review_count
        FROM movie_dw.reviews_clean_amazon
        WHERE score >= {min_score} AND score <= {max_score}
        GROUP BY product_id
        ORDER BY review_count DESC
    """

    REVIEWS_BY_KEYWORD = """
        SELECT *
        FROM movie_dw.reviews_clean_amazon
        WHERE review_text LIKE '%{keyword}%'
        ORDER BY review_unix DESC
    """

    # =======================
    # 四、演员-导演关系查询
    # =======================
    ACTOR_COLLABORATIONS = """
        WITH exploded AS (
          SELECT
            m.movie_id,
            pe.pos AS pos,
            pe.actor AS actor
          FROM movie_dw.movies_meta_dw m
          LATERAL VIEW posexplode(m.actors) pe AS pos, actor
        ),
        pairs AS (
          SELECT
            e1.movie_id,
            e1.actor AS a1,
            e2.actor AS a2
          FROM exploded e1
          JOIN exploded e2
            ON e1.movie_id = e2.movie_id
           AND e1.pos < e2.pos
        )
        SELECT
          a1 AS actor1,
          a2 AS actor2,
          COUNT(DISTINCT movie_id) AS collaborations
        FROM pairs
        GROUP BY a1, a2
        HAVING COUNT(DISTINCT movie_id) >= {min_collaborations}
        ORDER BY collaborations DESC
        LIMIT {limit}
    """

    # 导演-演员合作关系（仅 director 必填，不传 min_collaborations）
    DIRECTOR_ACTOR_COLLABORATIONS = """
        SELECT d AS director, a AS actor, COUNT(1) AS collaborations
        FROM movie_dw.movies_meta_dw
        LATERAL VIEW explode(director) dd AS d
        LATERAL VIEW explode(actors) aa AS a
        WHERE d = '{director}'
        GROUP BY d, a
        ORDER BY collaborations DESC
        LIMIT {limit}
    """

