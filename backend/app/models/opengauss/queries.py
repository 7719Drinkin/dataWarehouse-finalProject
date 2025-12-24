"""
OpenGauss SQL 查询语句集合
"""

class OpenGaussQueries:
    """OpenGauss 数据库 SQL 查询语句类"""

    # 基础查询
    MOVIES_BY_YEAR = """
        SELECT * FROM movies WHERE year = %s
    """

    MOVIES_BY_DIRECTOR = """
        SELECT * FROM movies WHERE director LIKE %s
    """

    MOVIES_BY_ACTOR_STARRING = """
        SELECT * FROM movies WHERE starring LIKE %s
    """

    MOVIES_BY_ACTOR_PARTICIPATED = """
        SELECT * FROM movies WHERE actors LIKE %s
    """

    MOVIES_BY_GENRE = """
        SELECT * FROM movies WHERE genres LIKE %s
    """

    # 高级查询
    HIGH_RATED_MOVIES = """
        SELECT * FROM movies 
        WHERE rating >= %s AND reviews >= %s
        ORDER BY rating DESC
    """

    MOVIES_BY_TIME_RANGE = """
        SELECT * FROM movies 
        WHERE date_added >= %s AND date_added <= %s
        ORDER BY date_added DESC
    """

    MOVIES_BY_QUARTER = """
        SELECT 
            EXTRACT(QUARTER FROM date_added::date) AS quarter,
            COUNT(*) AS count
        FROM movies
        WHERE EXTRACT(YEAR FROM date_added::date) = %s
        GROUP BY EXTRACT(QUARTER FROM date_added::date)
        ORDER BY quarter
    """

    MOVIES_ADDED_TUESDAY = """
        SELECT * FROM movies
        WHERE EXTRACT(YEAR FROM date_added::date) = %s
        AND EXTRACT(DOW FROM date_added::date) = 2
        ORDER BY date_added DESC
    """

    # 关系查询
    ACTOR_COLLABORATIONS = """
        WITH actor_movies AS (
            SELECT DISTINCT 
                unnest(string_to_array(actors, ',')) AS actor,
                title
            FROM movies
        )
        SELECT 
            a1.actor,
            a2.actor,
            COUNT(DISTINCT a1.title) AS collaborations
        FROM actor_movies a1
        JOIN actor_movies a2 ON a1.title = a2.title
        WHERE a1.actor < a2.actor
        GROUP BY a1.actor, a2.actor
        HAVING COUNT(DISTINCT a1.title) >= %s
        ORDER BY collaborations DESC
        LIMIT %s
    """

    DIRECTOR_ACTOR_COLLABORATIONS = """
        WITH director_actors AS (
            SELECT DISTINCT 
                director,
                unnest(string_to_array(actors, ',')) AS actor,
                title
            FROM movies
        )
        SELECT 
            actor,
            COUNT(DISTINCT title) AS collaborations
        FROM director_actors
        WHERE director = %s
        GROUP BY actor
        HAVING COUNT(DISTINCT title) >= %s
        ORDER BY collaborations DESC
        LIMIT %s
    """
