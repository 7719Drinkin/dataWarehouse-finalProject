"""
OpenGauss SQL 查询语句集合
"""

class OpenGaussQueries:
    """OpenGauss 数据库 SQL 查询语句类"""

    # ===========================
    # 时间维度查询/统计
    # ===========================

    # 按年份统计电影数量
    MOVIES_BY_YEAR = """
        SELECT release_year, COUNT(*) AS movie_count
        FROM dim_movies
        WHERE release_year = %s
        GROUP BY release_year
        ORDER BY release_year;
    """

    # 按季度统计电影数量
    MOVIES_BY_QUARTER = """
        SELECT release_quarter, COUNT(*) AS movie_count
        FROM dim_movies
        WHERE release_year = %s
        GROUP BY release_quarter
        ORDER BY release_quarter;
    """

    # 按月份统计电影数量
    MOVIES_BY_MONTH = """
        SELECT release_month, COUNT(*) AS movie_count
        FROM dim_movies
        WHERE release_year = %s
        GROUP BY release_month
        ORDER BY release_month;
    """

    # 按周统计电影数量
    MOVIES_BY_WEEK = """
        SELECT release_week, COUNT(*) AS movie_count
        FROM dim_movies
        WHERE release_year = %s
        GROUP BY release_week
        ORDER BY release_week;
    """

    # 某天新增电影数量
    MOVIES_BY_DAY = """
        SELECT release_date, COUNT(*) AS movie_count
        FROM dim_movies
        WHERE release_date = %s
        GROUP BY release_date;
    """

    # 用户评价数量统计（按年份/季度/月份/周）
    REVIEWS_COUNT_BY_TIME = """
        SELECT review_year, review_quarter, review_month, review_week, COUNT(*) AS review_count
        FROM fact_reviews
        WHERE review_year = %s
        GROUP BY review_year, review_quarter, review_month, review_week
        ORDER BY review_year, review_quarter, review_month, review_week;
    """

    # 按评分区间统计评价数量
    REVIEWS_COUNT_BY_SCORE = """
        SELECT COUNT(*) AS review_count
        FROM fact_reviews
        WHERE score >= %s;
    """

    # 时间段内电影及评价统计（电影数量、平均评分、评论数）
    MOVIES_REVIEWS_STATS_BY_TIME = """
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres,
            COUNT(r.review_id) AS review_count,
            COALESCE(AVG(r.score), 0) AS rating
        FROM dim_movies m
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        WHERE m.release_date >= %s AND m.release_date <= %s
        GROUP BY m.movie_id, m.title, m.director, m.genres
        ORDER BY rating DESC;
    """

    # 按时间动态查询电影
    MOVIES_BY_TIME_DYNAMIC_TEMPLATE = """
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres,
            COUNT(r.review_id) AS review_count,
            COALESCE(AVG(r.score), 0) AS rating
        FROM dim_movies m
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        {where_clause}
        GROUP BY m.movie_id, m.title, m.director, m.genres
        ORDER BY rating DESC;
    """

    # ===========================
    # 电影维度查询/统计
    # ===========================

    # 查询电影所有版本
    MOVIES_VERSIONS_BY_TITLE = """
        SELECT movie_id, title, versions
        FROM dim_movies
        WHERE title = %s;
    """

    # 按电影名统计评论数量、平均分
    MOVIE_REVIEWS_BY_TITLE = """
        SELECT m.movie_id, m.title, COUNT(r.review_id) AS review_count, AVG(r.score) AS avg_score
        FROM dim_movies m
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        WHERE m.title = %s
        GROUP BY m.movie_id, m.title;
    """

    # 查询某导演的所有电影
    # 注意：dim_movies.director 是 TEXT[]（数组），不能直接用 "director = %s" 比较。
    # 若要按导演名过滤，应使用：%s = ANY(director)
    MOVIES_BY_DIRECTOR = """
        SELECT movie_id, title, release_date
        FROM dim_movies
        WHERE %s = ANY(director);
    """

    # 统计导演作品数量
    # 注意：dim_movies.director 是 TEXT[]，这里返回 director 数组本身。
    # 若要按“某个导演名”统计其作品数，应使用 %s = ANY(director)
    DIRECTOR_MOVIE_COUNT = """
        SELECT COUNT(*) AS movie_count
        FROM dim_movies
        WHERE %s = ANY(director);
    """

    # 某演员主演电影数量（按 "\ufeffactor_id"）
    MOVIES_BY_ACTOR_STARRING = """
        SELECT m.movie_id, m.title, m.release_date
        FROM dim_movies m
        JOIN movie_actor ma ON m.movie_id = ma.movie_id
        WHERE ma.actor_id = %s AND ma.is_lead = TRUE;
    """

    # 某演员参演电影数量（按 actor_id）
    MOVIES_BY_ACTOR_PARTICIPATED = """
        SELECT m.movie_id, m.title, m.release_date
        FROM dim_movies m
        JOIN movie_actor ma ON m.movie_id = ma.movie_id
        WHERE ma.actor_id = %s;
    """

    # 某演员主演电影数量（按 actor_name）
    MOVIES_BY_ACTOR_NAME_STARRING = """
        SELECT m.movie_id, m.title, m.release_date
        FROM dim_movies m
        JOIN movie_actor ma ON m.movie_id = ma.movie_id
        JOIN dim_actors a ON ma.actor_id = a.actor_id
        WHERE a.actor_name = %s AND ma.is_lead = TRUE;
    """

    # 某演员参演电影数量（按 actor_name）
    MOVIES_BY_ACTOR_NAME_PARTICIPATED = """
        SELECT m.movie_id, m.title, m.release_date
        FROM dim_movies m
        JOIN movie_actor ma ON m.movie_id = ma.movie_id
        JOIN dim_actors a ON ma.actor_id = a.actor_id
        WHERE a.actor_name = %s;
    """

    # 按电影类型统计电影数量
    MOVIES_BY_GENRE = """
        SELECT COUNT(*) AS movie_count
        FROM dim_movies
        WHERE %s = ANY(genres);
    """

    # 多条件组合查询（可选参数：director, genre, year, min_score, actor_name）
    MOVIES_BY_MULTI_CONDITION_TEMPLATE = """
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres,
            COALESCE(AVG(r.score), 0) AS rating,
            COUNT(r.review_id) AS review_count
        FROM dim_movies m
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        LEFT JOIN movie_actor ma ON m.movie_id = ma.movie_id
        LEFT JOIN dim_actors a ON ma.actor_id = a.actor_id
        {where_clause}
        GROUP BY m.movie_id, m.title, m.director, m.genres
        {having_clause}
        ORDER BY rating DESC;
    """

    # 按人员查询电影（可选参数：director, actor_name, starring_name）
    MOVIES_BY_PERSON_TEMPLATE = """
        WITH FilteredMovies AS (
            SELECT DISTINCT m.movie_id
            FROM dim_movies m
            LEFT JOIN movie_actor ma ON m.movie_id = ma.movie_id
            LEFT JOIN dim_actors a ON ma.actor_id = a.actor_id
            {where_clause}
        )
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres,
            COUNT(r.review_id) AS review_count,
            COALESCE(AVG(r.score), 0) AS rating
        FROM dim_movies m
        JOIN FilteredMovies fm ON m.movie_id = fm.movie_id
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        GROUP BY m.movie_id, m.title, m.director, m.genres
        ORDER BY rating DESC;
    """

    # ===========================
    # 用户评价相关
    # ===========================

    # 高评分电影（评分+评论数）
    HIGH_RATED_MOVIES = """
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.genres,
            AVG(r.score) AS rating,
            COUNT(r.review_id) AS review_count
        FROM dim_movies m
        JOIN fact_reviews r ON m.movie_id = r.movie_id
        GROUP BY m.movie_id, m.title, m.director, m.genres
        HAVING AVG(r.score) >= %s AND COUNT(r.review_id) >= %s
        ORDER BY rating DESC;
    """

    # 包含关键词的评论
    REVIEWS_BY_KEYWORD = """
        SELECT review_id, movie_id, user_id, review_text, score
        FROM fact_reviews
        WHERE review_text ILIKE %s;
    """

    # ===========================
    # Reviews by movie_id（用于前端评论区分页）
    # ===========================

    REVIEWS_COUNT_BY_MOVIE_ID = """
        SELECT COUNT(*) AS total
        FROM fact_reviews
        WHERE movie_id = %s;
    """

    REVIEWS_BY_MOVIE_ID = """
        SELECT
            review_id,
            movie_id,
            user_id,
            profile_name,
            helpfulness,
            score,
            review_time,
            review_summary,
            review_text
        FROM fact_reviews
        WHERE movie_id = %s
        ORDER BY review_time DESC
        LIMIT %s OFFSET %s;
    """

    # ===========================
    # 演员-导演关系查询
    # ===========================

    # 演员合作统计
    ACTOR_COLLABORATIONS = """
        SELECT ma1.actor_id AS actor1, ma2.actor_id AS actor2, COUNT(*) AS collaborations
        FROM movie_actor ma1
        JOIN movie_actor ma2 ON ma1.movie_id = ma2.movie_id
        WHERE ma1.actor_id < ma2.actor_id
        GROUP BY ma1.actor_id, ma2.actor_id
        ORDER BY collaborations DESC
        LIMIT %s;
    """

    # 导演与演员合作次数
    DIRECTOR_ACTOR_COLLABORATIONS = """
        SELECT ma.actor_id, COUNT(*) AS collaborations
        FROM movie_actor ma
        JOIN dim_movies m ON ma.movie_id = m.movie_id
        WHERE %s = ANY(m.director)
        GROUP BY ma.actor_id
        HAVING COUNT(*) >= %s
        ORDER BY collaborations DESC
        LIMIT %s;
    """

    # 某类型电影最受欢迎的演员组合（按评论数统计）
    POPULAR_ACTOR_COMBINATIONS_BY_GENRE = """
        SELECT ma1.actor_id AS actor1, ma2.actor_id AS actor2, COUNT(r.review_id) AS review_count
        FROM movie_actor ma1
        JOIN movie_actor ma2 ON ma1.movie_id = ma2.movie_id
        JOIN dim_movies m ON ma1.movie_id = m.movie_id
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        WHERE ma1.actor_id < ma2.actor_id AND %s = ANY(m.genres)
        GROUP BY ma1.actor_id, ma2.actor_id
        ORDER BY review_count DESC
        LIMIT %s;
    """
