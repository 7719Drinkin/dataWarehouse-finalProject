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
        MATCH (u:User)-[rt:RATED]->(m:Movie)
        RETURN rt.review_year AS year, COUNT(rt) AS review_count
        ORDER BY year
    """

    REVIEWS_COUNT_BY_SCORE = """
        MATCH (u:User)-[rt:RATED]->(m:Movie)
        WHERE rt.score >= $min_score
        RETURN COUNT(rt) AS review_count
    """

    MOVIES_REVIEWS_STATS_BY_TIME = """
        MATCH (m:Movie)
        WHERE m.release_date >= $start_date AND m.release_date <= $end_date
        OPTIONAL MATCH (u:User)-[rt:RATED]->(m)
        RETURN m.title AS movie, COUNT(rt) AS review_count, AVG(rt.score) AS avg_score
    """

    # 按时间动态查询电影
    MOVIES_BY_TIME_DYNAMIC_TEMPLATE = """
        MATCH (m:Movie)
        {where_clause}
        OPTIONAL MATCH (u:User)-[rt:RATED]->(m)
        OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)
        WITH
          m,
          COUNT(rt) AS review_count,
          COALESCE(AVG(rt.score), 0) AS rating,
          COLLECT(DISTINCT d.name) AS director
        RETURN
          m.id AS movie_id,
          m.title AS title,
          director AS director,
          COALESCE(m.genres, []) AS genres,
          review_count,
          rating
        ORDER BY rating DESC
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
        MATCH (m:Movie)
        WHERE m.title = $title
        OPTIONAL MATCH (u:User)-[rt:RATED]->(m)
        RETURN COUNT(rt) AS review_count, AVG(rt.score) AS avg_score
    """

    # 导演相关
    MOVIES_BY_DIRECTOR = """
        MATCH (d:Director)-[:DIRECTED]->(m:Movie)
        WHERE d.name = $director
        RETURN m
    """

    DIRECTOR_MOVIE_COUNT = """
        MATCH (d:Director)-[:DIRECTED]->(m:Movie)
        WHERE d.name = $director
        RETURN COUNT(m) AS movie_count
    """

    DIRECTOR_ACTOR_COLLABORATIONS = """
        MATCH (d:Director)-[:COLLABORATED_WITH]->(a:Actor)
        WHERE d.name = $director
        RETURN a.name AS actor, COALESCE(sum(1), 0) AS collaborations
        ORDER BY collaborations DESC
        LIMIT $limit
    """

    # 演员相关
    MOVIES_BY_ACTOR_STARRING = """
        MATCH (a:Actor)-[ai:ACTED_IN]->(m:Movie)
        WHERE a.id = $actor_id AND ai.is_lead = true
        RETURN m
    """

    MOVIES_BY_ACTOR_PARTICIPATED = """
        MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
        WHERE a.id = $actor_id
        RETURN m
    """

    # 按演员名查询（前端传 name）
    MOVIES_BY_ACTOR_NAME_STARRING = """
        MATCH (a:Actor)-[ai:ACTED_IN]->(m:Movie)
        WHERE a.name = $actor_name AND ai.is_lead = true
        RETURN m
    """

    MOVIES_BY_ACTOR_NAME_PARTICIPATED = """
        MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
        WHERE a.name = $actor_name
        RETURN m
    """

    # 按人员查询（可选参数：director / actor / starring；至少一个）
    MOVIES_BY_PERSON_TEMPLATE = """
        MATCH (m:Movie)
        OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)
        OPTIONAL MATCH (a:Actor)-[ai:ACTED_IN]->(m)
        {where_clause}
        WITH DISTINCT m
        OPTIONAL MATCH (u:User)-[rt:RATED]->(m)
        OPTIONAL MATCH (d2:Director)-[:DIRECTED]->(m)
        WITH
          m,
          COUNT(rt) AS review_count,
          COALESCE(AVG(rt.score), 0) AS rating,
          COLLECT(DISTINCT d2.name) AS director
        RETURN
          m.id AS movie_id,
          m.title AS title,
          director AS director,
          COALESCE(m.genres, []) AS genres,
          review_count,
          rating
        ORDER BY rating DESC
    """

    # 类别相关
    MOVIES_BY_GENRE = """
        MATCH (m:Movie)
        WHERE $genre IN m.genres
        RETURN m
    """

    # 多条件组合查询
    MOVIES_BY_MULTI_CONDITION_TEMPLATE = """
        MATCH (m:Movie)
        OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)
        OPTIONAL MATCH (a:Actor)-[:ACTED_IN]->(m)
        {where_clause}
        WITH DISTINCT m
        OPTIONAL MATCH (u:User)-[rt:RATED]->(m)
        WITH m, COUNT(rt) AS review_count, COALESCE(AVG(rt.score), 0) AS rating
        {having_clause}
        OPTIONAL MATCH (d2:Director)-[:DIRECTED]->(m)
        WITH m, review_count, rating, COLLECT(DISTINCT d2.name) AS director
        RETURN
          m.id AS movie_id,
          m.title AS title,
          director AS director,
          COALESCE(m.genres, []) AS genres,
          review_count,
          rating
        ORDER BY rating DESC
    """

    # ===========================
    # 三、用户评价相关
    # ===========================
    HIGH_RATED_MOVIES = """
        MATCH (m:Movie)
        OPTIONAL MATCH (u:User)-[rt:RATED]->(m)
        WITH m, COUNT(rt) AS review_count, COALESCE(AVG(rt.score), 0) AS rating
        WHERE rating >= $min_score AND review_count >= $min_reviews
        OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)
        WITH m, review_count, rating, COLLECT(DISTINCT d.name) AS director
        RETURN
          m.id AS movie_id,
          m.title AS title,
          director AS director,
          COALESCE(m.genres, []) AS genres,
          review_count,
          rating
        ORDER BY rating DESC
    """

    REVIEWS_BY_KEYWORD = """
        MATCH (u:User)-[rt:RATED]->(m:Movie)
        WHERE rt.review_text CONTAINS $keyword
        RETURN rt, m
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
