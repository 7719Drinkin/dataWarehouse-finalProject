"""
OpenGauss SQL查询定义
"""

class OpenGaussQueries:
    """OpenGauss查询语句"""

    # 按年份查询电影统计
    MOVIES_BY_YEAR = """
    SELECT
        m.movie_id,
        m.title,
        m.release_date,
        m.genres,
        m.director,
        COUNT(r.review_id) as review_count,
        AVG(r.score) as avg_score
    FROM dim_movies m
    LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
    WHERE EXTRACT(YEAR FROM m.release_date) = %s
    GROUP BY m.movie_id, m.title, m.release_date, m.genres, m.director
    ORDER BY review_count DESC
    """

    # 按导演查询电影
    MOVIES_BY_DIRECTOR = """
    SELECT
        movie_id,
        title,
        release_date,
        genres,
        director,
        versions
    FROM dim_movies
    WHERE director ILIKE %s
    ORDER BY release_date DESC
    """

    # 按演员查询电影（主演）
    MOVIES_BY_ACTOR_STARRING = """
    SELECT DISTINCT
        m.movie_id,
        m.title,
        m.release_date,
        m.genres,
        m.director,
        m.starring
    FROM dim_movies m
    CROSS JOIN LATERAL unnest(m.starring) AS actor
    WHERE actor ILIKE %s
    ORDER BY m.release_date DESC
    """

    # 按演员查询电影（参演）
    MOVIES_BY_ACTOR_PARTICIPATED = """
    SELECT DISTINCT
        m.movie_id,
        m.title,
        m.release_date,
        m.genres,
        m.director,
        m.actors
    FROM dim_movies m
    CROSS JOIN LATERAL unnest(m.actors) AS actor
    WHERE actor ILIKE %s
    ORDER BY m.release_date DESC
    """

    # 按电影类型查询统计
    MOVIES_BY_GENRE = """
    SELECT
        genre,
        COUNT(*) as movie_count,
        AVG(review_count) as avg_reviews,
        AVG(avg_score) as avg_rating
    FROM (
        SELECT
            m.movie_id,
            m.title,
            unnest(m.genres) as genre,
            COUNT(r.review_id) as review_count,
            AVG(r.score) as avg_score
        FROM dim_movies m
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        GROUP BY m.movie_id, m.title, m.genres
    ) genre_stats
    WHERE genre ILIKE %s
    GROUP BY genre
    """

    # 高评分电影查询
    HIGH_RATED_MOVIES = """
    SELECT
        m.movie_id,
        m.title,
        m.release_date,
        m.genres,
        m.director,
        COUNT(r.review_id) as review_count,
        AVG(r.score) as avg_score
    FROM dim_movies m
    JOIN fact_reviews r ON m.movie_id = r.movie_id
    GROUP BY m.movie_id, m.title, m.release_date, m.genres, m.director
    HAVING AVG(r.score) >= %s AND COUNT(r.review_id) >= %s
    ORDER BY avg_score DESC, review_count DESC
    """

    # 按时间范围查询电影
    MOVIES_BY_TIME_RANGE = """
    SELECT
        m.movie_id,
        m.title,
        m.release_date,
        m.genres,
        COUNT(r.review_id) as review_count,
        AVG(r.score) as avg_score
    FROM dim_movies m
    LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
    WHERE m.release_date >= %s AND m.release_date <= %s
    GROUP BY m.movie_id, m.title, m.release_date, m.genres
    ORDER BY m.release_date DESC
    """

    # 按季度查询电影统计
    MOVIES_BY_QUARTER = """
    SELECT
        EXTRACT(YEAR FROM release_date) as year,
        EXTRACT(QUARTER FROM release_date) as quarter,
        COUNT(*) as movie_count,
        SUM(review_count) as total_reviews
    FROM (
        SELECT
            m.release_date,
            COUNT(r.review_id) as review_count
        FROM dim_movies m
        LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
        WHERE EXTRACT(YEAR FROM m.release_date) = %s
        GROUP BY m.movie_id, m.release_date
    ) quarterly_stats
    GROUP BY year, quarter
    ORDER BY year, quarter
    """

    # 周二新增电影查询
    MOVIES_ADDED_TUESDAY = """
    SELECT
        movie_id,
        title,
        release_date,
        genres,
        director
    FROM dim_movies
    WHERE EXTRACT(DOW FROM release_date) = 2  -- PostgreSQL: 0=周日, 1=周一, 2=周二
    AND EXTRACT(YEAR FROM release_date) = %s
    ORDER BY release_date
    """

    # 演员合作关系查询（通过共同电影）
    ACTOR_COLLABORATIONS = """
    SELECT
        a1.actor_name as actor1,
        a2.actor_name as actor2,
        COUNT(DISTINCT m.movie_id) as collaborations,
        array_agg(DISTINCT m.title ORDER BY m.title) as movies
    FROM movie_actor ma1
    JOIN movie_actor ma2 ON ma1.movie_id = ma2.movie_id AND ma1.actor_id < ma2.actor_id
    JOIN dim_actors a1 ON ma1.actor_id = a1.actor_id
    JOIN dim_actors a2 ON ma2.actor_id = a2.actor_id
    JOIN dim_movies m ON ma1.movie_id = m.movie_id
    GROUP BY a1.actor_name, a2.actor_name
    HAVING COUNT(DISTINCT m.movie_id) >= %s
    ORDER BY collaborations DESC
    LIMIT %s
    """

    # 导演演员合作关系查询
    DIRECTOR_ACTOR_COLLABORATIONS = """
    SELECT
        m.director,
        a.actor_name,
        COUNT(DISTINCT m.movie_id) as collaborations,
        AVG(r.score) as avg_rating,
        COUNT(r.review_id) as total_reviews
    FROM dim_movies m
    CROSS JOIN LATERAL unnest(m.actors) AS actor_name
    JOIN dim_actors a ON a.actor_name = actor_name
    LEFT JOIN fact_reviews r ON m.movie_id = r.movie_id
    WHERE m.director = %s
    GROUP BY m.director, a.actor_name
    HAVING COUNT(DISTINCT m.movie_id) >= %s
    ORDER BY collaborations DESC
    LIMIT %s
    """

