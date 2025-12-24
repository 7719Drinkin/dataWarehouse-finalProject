"""
Neo4j Cypher 查询语句集合
"""

class Neo4jQueries:
    """Neo4j 数据库 Cypher 查询语句类"""

    # 基础查询
    MOVIES_BY_YEAR = """
        MATCH (m:Movie) WHERE m.year = $year RETURN m
    """

    MOVIES_BY_DIRECTOR = """
        MATCH (m:Movie)-[:DIRECTED_BY]->(d:Director) 
        WHERE d.name CONTAINS $director 
        RETURN m
    """

    MOVIES_BY_ACTOR_STARRING = """
        MATCH (m:Movie)-[:STARRING]->(a:Actor) 
        WHERE a.name CONTAINS $actor 
        RETURN m
    """

    MOVIES_BY_ACTOR_PARTICIPATED = """
        MATCH (m:Movie)-[:ACTED_IN]->(a:Actor) 
        WHERE a.name CONTAINS $actor 
        RETURN m
    """

    MOVIES_BY_GENRE = """
        MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre) 
        WHERE g.name CONTAINS $genre 
        RETURN m
    """

    # 高级查询
    HIGH_RATED_MOVIES = """
        MATCH (m:Movie) 
        WHERE m.rating >= $min_score AND m.reviews >= $min_reviews
        RETURN m
        ORDER BY m.rating DESC
    """

    MOVIES_BY_TIME_RANGE = """
        MATCH (m:Movie) 
        WHERE m.date_added >= $start_date AND m.date_added <= $end_date
        RETURN m
        ORDER BY m.date_added DESC
    """

    MOVIES_BY_QUARTER = """
        MATCH (m:Movie)
        WHERE split(split(m.date_added, '-')[0], '.')[0] = $year
        WITH m,
             toInteger(split(m.date_added, '-')[1]) AS month
        WITH m,
             CASE 
                 WHEN month >= 1 AND month <= 3 THEN 'Q1'
                 WHEN month >= 4 AND month <= 6 THEN 'Q2'
                 WHEN month >= 7 AND month <= 9 THEN 'Q3'
                 ELSE 'Q4'
             END AS quarter
        RETURN quarter, COUNT(m) AS count
        ORDER BY quarter
    """

    MOVIES_ADDED_TUESDAY = """
        MATCH (m:Movie)
        WHERE split(m.date_added, '-')[0] = $year
        AND dayOfWeek(date(m.date_added)) = 3
        RETURN m
        ORDER BY m.date_added DESC
    """

    # 关系查询
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

    # Neo4j 特有查询
    POPULAR_ACTOR_COMBINATIONS = """
        MATCH (g:Genre {name: $genre})<-[:HAS_GENRE]-(m:Movie)<-[:ACTED_IN]-(a1:Actor),
              (m:Movie)<-[:ACTED_IN]-(a2:Actor)
        WHERE a1.id < a2.id
        WITH a1, a2, COUNT(DISTINCT m) AS movies
        ORDER BY movies DESC
        RETURN a1.name AS actor1, a2.name AS actor2, movies
        LIMIT 20
    """
