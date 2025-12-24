"""
Hive HiveQL 查询语句集合
"""

class HiveQueries:
    """Hive 数据库查询语句类"""

    # 基础查询
    MOVIES_BY_YEAR = """
        SELECT * FROM movies WHERE year = {year}
    """

    MOVIES_BY_DIRECTOR = """
        SELECT * FROM movies WHERE director LIKE '%{director}%'
    """

    MOVIES_BY_ACTOR_STARRING = """
        SELECT * FROM movies WHERE starring LIKE '%{actor}%'
    """

    MOVIES_BY_ACTOR_PARTICIPATED = """
        SELECT * FROM movies WHERE actors LIKE '%{actor}%'
    """

    MOVIES_BY_GENRE = """
        SELECT * FROM movies WHERE genres LIKE '%{genre}%'
    """

    # 高级查询
    HIGH_RATED_MOVIES = """
        SELECT * FROM movies 
        WHERE rating >= {min_score} AND reviews >= {min_reviews}
        ORDER BY rating DESC
    """

    MOVIES_BY_TIME_RANGE = """
        SELECT * FROM movies 
        WHERE date_added >= '{start_date}' AND date_added <= '{end_date}'
        ORDER BY date_added DESC
    """

    MOVIES_BY_QUARTER = """
        SELECT 
            quarter(from_unixtime(unix_timestamp(date_added, 'yyyy-MM-dd'))) AS quarter,
            COUNT(*) AS count
        FROM movies
        WHERE year(from_unixtime(unix_timestamp(date_added, 'yyyy-MM-dd'))) = {year}
        GROUP BY quarter(from_unixtime(unix_timestamp(date_added, 'yyyy-MM-dd')))
        ORDER BY quarter
    """

    MOVIES_ADDED_TUESDAY = """
        SELECT * FROM movies
        WHERE year(from_unixtime(unix_timestamp(date_added, 'yyyy-MM-dd'))) = {year}
        AND dayname(from_unixtime(unix_timestamp(date_added, 'yyyy-MM-dd'))) = 'Tuesday'
        ORDER BY date_added DESC
    """

    # 关系查询
    ACTOR_COLLABORATIONS = """
        SELECT a1, a2, COUNT(*) AS collaborations
        FROM (
            SELECT LATERAL VIEW EXPLODE(split(actors, ',')) AS a1 a1 FROM movies
        ) t1
        LATERAL VIEW EXPLODE(split(actors, ',')) AS a2 a2
        WHERE a1 < a2
        GROUP BY a1, a2
        HAVING COUNT(*) >= {min_collaborations}
        ORDER BY collaborations DESC
        LIMIT {limit}
    """

    DIRECTOR_ACTOR_COLLABORATIONS = """
        SELECT 
            director,
            actor,
            COUNT(*) AS collaborations
        FROM (
            SELECT director, LATERAL VIEW EXPLODE(split(actors, ',')) AS actor actor FROM movies
        ) t
        WHERE director = '{director}'
        GROUP BY director, actor
        HAVING COUNT(*) >= {min_collaborations}
        ORDER BY collaborations DESC
        LIMIT {limit}
    """
