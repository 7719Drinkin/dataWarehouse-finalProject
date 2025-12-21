"""
Hive SQL查询定义
"""

class HiveQueries:
    """Hive查询语句"""

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
    FROM reviews_clean r
    RIGHT JOIN movies_meta m ON r.movie_id = m.movie_id
    WHERE year = {year}
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
    FROM movies_meta
    WHERE lower(director) LIKE lower('%{director}%')
    ORDER BY release_date DESC
    """

    # 按演员查询主演电影
    MOVIES_BY_ACTOR_STARRING = """
    SELECT DISTINCT
        m.movie_id,
        m.title,
        m.release_date,
        m.genres,
        m.director,
        m.starring
    FROM movies_meta m
    LATERAL VIEW explode(m.starring) starring_table AS actor
    WHERE lower(actor) LIKE lower('%{actor}%')
    ORDER BY m.release_date DESC
    """

    # 按演员查询参演电影
    MOVIES_BY_ACTOR_PARTICIPATED = """
    SELECT DISTINCT
        m.movie_id,
        m.title,
        m.release_date,
        m.genres,
        m.director,
        m.actors
    FROM movies_meta m
    LATERAL VIEW explode(m.actors) actors_table AS actor
    WHERE lower(actor) LIKE lower('%{actor}%')
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
            genre,
            COUNT(r.review_id) as review_count,
            AVG(r.score) as avg_score
        FROM movies_meta m
        LATERAL VIEW explode(m.genres) genres_table AS genre
        LEFT JOIN reviews_clean r ON m.movie_id = r.movie_id
        GROUP BY m.movie_id, m.title, genre
    ) genre_stats
    WHERE lower(genre) LIKE lower('%{genre}%')
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
    FROM movies_meta m
    JOIN reviews_clean r ON m.movie_id = r.movie_id
    GROUP BY m.movie_id, m.title, m.release_date, m.genres, m.director
    HAVING AVG(r.score) >= {min_score} AND COUNT(r.review_id) >= {min_reviews}
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
    FROM movies_meta m
    LEFT JOIN reviews_clean r ON m.movie_id = r.movie_id
    WHERE m.release_date >= '{start_date}' AND m.release_date <= '{end_date}'
    GROUP BY m.movie_id, m.title, m.release_date, m.genres
    ORDER BY m.release_date DESC
    """

    # 按季度查询电影统计
    MOVIES_BY_QUARTER = """
    SELECT
        year(release_date) as year,
        ceil(month(release_date)/3) as quarter,
        COUNT(*) as movie_count,
        SUM(review_count) as total_reviews
    FROM (
        SELECT
            m.release_date,
            COUNT(r.review_id) as review_count
        FROM movies_meta m
        LEFT JOIN reviews_clean r ON m.movie_id = r.movie_id
        WHERE year(m.release_date) = {year}
        GROUP BY m.movie_id, m.release_date
    ) quarterly_stats
    GROUP BY year(release_date), ceil(month(release_date)/3)
    ORDER BY year, quarter
    """

    # 周二新增电影查询（Hive中weekday从0开始，2表示周二）
    MOVIES_ADDED_TUESDAY = """
    SELECT
        movie_id,
        title,
        release_date,
        genres,
        director
    FROM movies_meta
    WHERE from_unixtime(unix_timestamp(release_date), 'u') = '2'
    AND year(release_date) = {year}
    ORDER BY release_date
    """

    # 演员合作关系查询（通过共同电影）
    ACTOR_COLLABORATIONS = """
    SELECT
        a1.actor_name as actor1,
        a2.actor_name as actor2,
        COUNT(DISTINCT m.movie_id) as collaborations,
        collect_list(m.title) as movies
    FROM (
        SELECT movie_id, actor_name
        FROM movies_meta m
        LATERAL VIEW explode(m.actors) actors_table AS actor_name
    ) a1
    JOIN (
        SELECT movie_id, actor_name
        FROM movies_meta m
        LATERAL VIEW explode(m.actors) actors_table AS actor_name
    ) a2 ON a1.movie_id = a2.movie_id AND a1.actor_name < a2.actor_name
    JOIN movies_meta m ON a1.movie_id = m.movie_id
    GROUP BY a1.actor_name, a2.actor_name
    HAVING COUNT(DISTINCT m.movie_id) >= {min_collaborations}
    ORDER BY collaborations DESC
    LIMIT {limit}
    """

    # 导演演员合作关系查询
    DIRECTOR_ACTOR_COLLABORATIONS = """
    SELECT
        m.director,
        actor_name,
        COUNT(DISTINCT m.movie_id) as collaborations,
        AVG(r.score) as avg_rating,
        COUNT(r.review_id) as total_reviews
    FROM movies_meta m
    LATERAL VIEW explode(m.actors) actors_table AS actor_name
    LEFT JOIN reviews_clean r ON m.movie_id = r.movie_id
    WHERE m.director = '{director}'
    GROUP BY m.director, actor_name
    HAVING COUNT(DISTINCT m.movie_id) >= {min_collaborations}
    ORDER BY collaborations DESC
    LIMIT {limit}
    """

