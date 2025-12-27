"""
hive_queries.py
Hive 数据库查询语句集合（支持数据应用需求）
"""

class HiveQueries:
    """Hive 数据库查询语句类"""

    # =======================
    # 一、时间维度查询/统计
    # =======================
    # 按年份查询电影
    MOVIES_BY_YEAR = """
        SELECT *
        FROM movies_meta_dw
        WHERE release_year = {year}
    """

    # 按季度查询电影数量
    MOVIES_BY_QUARTER = """
        SELECT release_quarter, COUNT(*) AS movie_count
        FROM movies_meta_dw
        WHERE release_year = {year}
        GROUP BY release_quarter
        ORDER BY release_quarter
    """

    # 按月份查询电影数量
    MOVIES_BY_MONTH = """
        SELECT release_month, COUNT(*) AS movie_count
        FROM movies_meta_dw
        WHERE release_year = {year}
        GROUP BY release_month
        ORDER BY release_month
    """

    # 按周查询电影数量
    MOVIES_BY_WEEK = """
        SELECT release_week, COUNT(*) AS movie_count
        FROM movies_meta_dw
        WHERE release_year = {year}
        GROUP BY release_week
        ORDER BY release_week
    """

    # 某天新增电影数量（按日期）
    MOVIES_BY_DAY = """
        SELECT COUNT(*) AS movie_count
        FROM movies_meta_dw
        WHERE release_date = '{date}'
    """

    # 某时间段电影及评价统计
    MOVIES_BY_TIME_RANGE = """
        SELECT m.asin AS movie_id, m.title,
               COUNT(r.review_id) AS review_count,
               AVG(r.score) AS avg_score
        FROM movies_meta_dw m
        LEFT JOIN fact_reviews r ON m.asin = r.movie_id
        WHERE m.release_date >= '{start_date}' AND m.release_date <= '{end_date}'
        GROUP BY m.asin, m.title
        ORDER BY avg_score DESC
    """

    # =======================
    # 二、电影维度查询/统计
    # =======================
    # 按导演查询电影
    MOVIES_BY_DIRECTOR = """
        SELECT *
        FROM movies_meta_dw
        WHERE array_contains(director, '{director}')
    """

    # 按演员主演查询
    MOVIES_BY_ACTOR_STARRING = """
        SELECT *
        FROM movies_meta_dw
        WHERE array_contains(starring, '{actor}')
    """

    # 按演员参演查询
    MOVIES_BY_ACTOR_PARTICIPATED = """
        SELECT *
        FROM movies_meta_dw
        WHERE array_contains(actors, '{actor}')
    """

    # 按电影类型查询
    MOVIES_BY_GENRE = """
        SELECT *
        FROM movies_meta_dw
        WHERE array_contains(genres, '{genre}')
    """

    MOVIES_BY_MULTI_CONDITION_TEMPLATE = """
        SELECT m.movie_id, m.title, m.release_date, AVG(r.score) AS avg_score, COUNT(r.review_id) AS review_count
        FROM dim_movies m
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        LEFT JOIN movie_actor ma ON m.movie_id = ma.movie_id
        {where_clause}
        GROUP BY m.movie_id, m.title, m.release_date
        {having_clause}
        ORDER BY avg_score DESC
    """

    # =======================
    # 三、用户评价相关
    # =======================
    # 高评分电影查询
    HIGH_RATED_MOVIES = """
        SELECT m.asin AS movie_id, m.title,
               COUNT(r.review_id) AS review_count,
               AVG(r.score) AS avg_score
        FROM movies_meta_dw m
        JOIN fact_reviews r ON m.asin = r.movie_id
        GROUP BY m.asin, m.title
        HAVING AVG(r.score) >= {min_score} AND COUNT(r.review_id) >= {min_reviews}
        ORDER BY avg_score DESC
    """

    # 按评分区间统计
    REVIEWS_BY_SCORE_RANGE = """
        SELECT movie_id, COUNT(*) AS review_count
        FROM fact_reviews
        WHERE score >= {min_score} AND score <= {max_score}
        GROUP BY movie_id
        ORDER BY review_count DESC
    """

    # 按关键词搜索评论
    REVIEWS_BY_KEYWORD = """
        SELECT *
        FROM fact_reviews
        WHERE review_text LIKE '%{keyword}%'
        ORDER BY review_time DESC
    """

    # =======================
    # 四、演员-导演关系查询
    # =======================
    # 演员合作关系
    ACTOR_COLLABORATIONS = """
        SELECT a1, a2, COUNT(*) AS collaborations
        FROM (
            SELECT EXPLODE(actors) AS a1
            FROM movies_meta_dw
        ) t1
        LATERAL VIEW EXPLODE(actors) AS a2
        WHERE a1 < a2
        GROUP BY a1, a2
        HAVING COUNT(*) >= {min_collaborations}
        ORDER BY collaborations DESC
        LIMIT {limit}
    """

    # 导演-演员合作关系
    DIRECTOR_ACTOR_COLLABORATIONS = """
        SELECT director, actor, COUNT(*) AS collaborations
        FROM (
            SELECT director, EXPLODE(actors) AS actor
            FROM movies_meta_dw
        ) t
        WHERE director = '{director}'
        GROUP BY director, actor
        HAVING COUNT(*) >= {min_collaborations}
        ORDER BY collaborations DESC
        LIMIT {limit}
    """



