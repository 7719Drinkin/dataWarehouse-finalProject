"""
Neo4j Cypher 查询语句集合（改进版）
"""
class Neo4jQueries:
    """Neo4j 数据库 Cypher 查询语句类，按数据分析维度整理"""

    # ===========================
    # 一、时间维度查询/统计
    # ===========================

    # 1. 按年份统计电影数量
    MOVIES_COUNT_BY_YEAR = """
        MATCH (m:Movie)
        RETURN m.release_year AS year, COUNT(m) AS movie_count
        ORDER BY year
    """

    # 2. 按季度统计电影数量
    MOVIES_COUNT_BY_QUARTER = """
        MATCH (m:Movie)
        RETURN m.release_year AS year, m.release_quarter AS quarter, COUNT(m) AS movie_count
        ORDER BY year, quarter
    """

    # 3. 按月份统计电影数量
    MOVIES_COUNT_BY_MONTH = """
        MATCH (m:Movie)
        RETURN m.release_year AS year, m.release_month AS month, COUNT(m) AS movie_count
        ORDER BY year, month
    """

    # 4. 按周统计电影数量
    MOVIES_COUNT_BY_WEEK = """
        MATCH (m:Movie)
        RETURN m.release_year AS year, m.release_week AS week, COUNT(m) AS movie_count
        ORDER BY year, week
    """

    # 5. 某天新增电影数量
    MOVIES_COUNT_BY_DAY = """
        MATCH (m:Movie)
        WHERE m.release_date = $date
        RETURN COUNT(m) AS movie_count
    """

    # 用户评价数量统计
    REVIEWS_COUNT_BY_YEAR = """
        MATCH (r:Review)
        RETURN r.review_year AS year, COUNT(r) AS review_count
        ORDER BY year
    """

    REVIEWS_COUNT_BY_SCORE = """
        MATCH (r:Review)
        WHERE r.score >= $min_score
        RETURN COUNT(r) AS review_count
    """

    MOVIES_REVIEWS_STATS_BY_TIME = """
        MATCH (m:Movie)<-[:REVIEWS]-(r:Review)
        WHERE m.release_date >= $start_date AND m.release_date <= $end_date
        RETURN m.title AS movie, COUNT(r) AS review_count, AVG(r.score) AS avg_score
    """

    # ===========================
    # 二、电影维度查询/统计
    # ===========================

    # 电影名称相关
    MOVIES_VERSIONS_BY_TITLE = """
        MATCH (m:Movie)
        WHERE m.title = $title
        RETURN m.versions AS versions
    """

    MOVIE_REVIEWS_BY_TITLE = """
        MATCH (m:Movie)<-[:REVIEWS]-(r:Review)
        WHERE m.title = $title
        RETURN COUNT(r) AS review_count, AVG(r.score) AS avg_score
    """

    # 导演相关
    MOVIES_BY_DIRECTOR = """
        MATCH (m:Movie)-[:DIRECTED_BY]->(d:Director)
        WHERE d.name = $director
        RETURN m
    """

    DIRECTOR_MOVIE_COUNT = """
        MATCH (m:Movie)-[:DIRECTED_BY]->(d:Director)
        WHERE d.name = $director
        RETURN COUNT(m) AS movie_count
    """

    DIRECTOR_ACTOR_COLLABORATIONS = """
        MATCH (d:Director)-[:DIRECTED_BY]->(m:Movie)<-[:ACTED_IN]-(a:Actor)
        WHERE d.name = $director
        RETURN a.name AS actor, COUNT(m) AS collaborations
        ORDER BY collaborations DESC
        LIMIT $limit
    """

    # 演员相关
    MOVIES_BY_ACTOR_STARRING = """
        MATCH (a:Actor)-[:STARRING]->(m:Movie)
        WHERE a.id = $actor_id
        RETURN m
    """

    MOVIES_BY_ACTOR_PARTICIPATED = """
        MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
        WHERE a.id = $actor_id
        RETURN m
    """

    # 类别相关
    MOVIES_BY_GENRE = """
        MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
        WHERE g.name = $genre
        RETURN m
    """

    # 多条件组合查询
    MOVIES_BY_MULTI_CONDITION = """
        MATCH (m:Movie)-[:DIRECTED_BY]->(d:Director)-[:HAS_GENRE]->(g:Genre)
        WHERE d.name = $director AND g.name = $genre AND m.release_year = $year AND m.rating >= $min_score
        RETURN m
    """

    # ===========================
    # 三、用户评价相关
    # ===========================
    HIGH_RATED_MOVIES = """
        MATCH (m:Movie)<-[:REVIEWS]-(r:Review)
        WHERE r.score >= $min_score
        WITH m, COUNT(r) AS review_count, AVG(r.score) AS avg_score
        WHERE review_count >= $min_reviews
        RETURN m, avg_score, review_count
        ORDER BY avg_score DESC
    """

    REVIEWS_BY_KEYWORD = """
        MATCH (r:Review)-[:REVIEWS]->(m:Movie)
        WHERE r.comment CONTAINS $keyword
        RETURN r, m
    """

    # ===========================
    # 四、演员-导演关系查询
    # ===========================
    ACTOR_COLLABORATIONS = """
        MATCH (a1:Actor)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(a2:Actor)
        WHERE a1.id < a2.id
        WITH a1, a2, COUNT(DISTINCT m) AS collaborations
        WHERE collaborations >= $min_collaborations
        RETURN a1.name AS actor1, a2.name AS actor2, collaborations
        ORDER BY collaborations DESC
        LIMIT $limit
    """

    DIRECTOR_ACTOR_COLLABORATIONS = """
        MATCH (d:Director)-[:DIRECTED]->(m:Movie)<-[:ACTED_IN]-(a:Actor)
        WHERE d.name = $director
        WITH a, COUNT(DISTINCT m) AS collaborations
        WHERE collaborations >= $min_collaborations
        RETURN a.name AS actor, collaborations
        ORDER BY collaborations DESC
        LIMIT $limit
    """

    POPULAR_ACTOR_COMBINATIONS_BY_GENRE = """
        MATCH (g:Genre {name: $genre})<-[:HAS_GENRE]-(m:Movie)<-[:ACTED_IN]-(a1:Actor),
              (m)<-[:ACTED_IN]-(a2:Actor)
        WHERE a1.id < a2.id
        WITH a1, a2, COUNT(DISTINCT m) AS movies
        RETURN a1.name AS actor1, a2.name AS actor2, movies
        ORDER BY movies DESC
        LIMIT $limit
    """
