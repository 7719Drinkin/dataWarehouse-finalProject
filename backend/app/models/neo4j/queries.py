"""
Neo4j Cypher查询定义
"""

class Neo4jQueries:
    """Neo4j查询语句"""

    # 按年份查询电影统计
    MOVIES_BY_YEAR = """
    MATCH (m:Movie)
    WHERE m.release_year = $year
    OPTIONAL MATCH (m)<-[:REVIEWED]-(u:User)
    RETURN m.movie_id as movie_id,
           m.title as title,
           m.release_date as release_date,
           m.genres as genres,
           m.director as director,
           count(u) as review_count,
           avg(u.score) as avg_score
    ORDER BY review_count DESC
    """

    # 按导演查询电影
    MOVIES_BY_DIRECTOR = """
    MATCH (m:Movie)<-[:DIRECTED]-(d:Director)
    WHERE toLower(d.name) CONTAINS toLower($director)
    RETURN m.movie_id as movie_id,
           m.title as title,
           m.release_date as release_date,
           m.genres as genres,
           d.name as director,
           m.versions as versions
    ORDER BY m.release_date DESC
    """

    # 按演员查询主演电影
    MOVIES_BY_ACTOR_STARRING = """
    MATCH (m:Movie)<-[:STARRED_IN]-(a:Actor)
    WHERE toLower(a.name) CONTAINS toLower($actor)
    RETURN DISTINCT m.movie_id as movie_id,
                    m.title as title,
                    m.release_date as release_date,
                    m.genres as genres,
                    m.director as director,
                    m.starring as starring
    ORDER BY m.release_date DESC
    """

    # 按演员查询参演电影
    MOVIES_BY_ACTOR_PARTICIPATED = """
    MATCH (m:Movie)<-[:ACTED_IN]-(a:Actor)
    WHERE toLower(a.name) CONTAINS toLower($actor)
    RETURN DISTINCT m.movie_id as movie_id,
                    m.title as title,
                    m.release_date as release_date,
                    m.genres as genres,
                    m.director as director,
                    m.actors as actors
    ORDER BY m.release_date DESC
    """

    # 按电影类型查询统计
    MOVIES_BY_GENRE = """
    MATCH (m:Movie)
    WHERE any(genre IN m.genres WHERE toLower(genre) CONTAINS toLower($genre))
    OPTIONAL MATCH (m)<-[:REVIEWED]-(u:User)
    WITH m.genres as all_genres, count(u) as review_count, avg(u.score) as avg_score
    UNWIND all_genres as genre
    WITH genre, count(*) as movie_count, avg(review_count) as avg_reviews, avg(avg_score) as avg_rating
    WHERE toLower(genre) CONTAINS toLower($genre)
    RETURN genre, movie_count, avg_reviews, avg_rating
    """

    # 高评分电影查询
    HIGH_RATED_MOVIES = """
    MATCH (m:Movie)<-[r:REVIEWED]-(:User)
    WITH m, count(r) as review_count, avg(r.score) as avg_score
    WHERE avg_score >= $min_score AND review_count >= $min_reviews
    RETURN m.movie_id as movie_id,
           m.title as title,
           m.release_date as release_date,
           m.genres as genres,
           m.director as director,
           review_count,
           avg_score
    ORDER BY avg_score DESC, review_count DESC
    """

    # 按时间范围查询电影
    MOVIES_BY_TIME_RANGE = """
    MATCH (m:Movie)
    WHERE date(m.release_date) >= date($start_date) AND date(m.release_date) <= date($end_date)
    OPTIONAL MATCH (m)<-[:REVIEWED]-(u:User)
    RETURN m.movie_id as movie_id,
           m.title as title,
           m.release_date as release_date,
           m.genres as genres,
           count(u) as review_count,
           avg(u.score) as avg_score
    ORDER BY m.release_date DESC
    """

    # 按季度查询电影统计
    MOVIES_BY_QUARTER = """
    MATCH (m:Movie)
    WHERE m.release_year = $year
    WITH m,
         CASE
           WHEN m.release_month <= 3 THEN 1
           WHEN m.release_month <= 6 THEN 2
           WHEN m.release_month <= 9 THEN 3
           ELSE 4
         END as quarter
    OPTIONAL MATCH (m)<-[:REVIEWED]-(u:User)
    RETURN m.release_year as year,
           quarter,
           count(DISTINCT m) as movie_count,
           count(u) as total_reviews
    ORDER BY year, quarter
    """

    # 周二新增电影查询
    MOVIES_ADDED_TUESDAY = """
    MATCH (m:Movie)
    WHERE m.release_year = $year AND m.release_weekday = 2
    RETURN m.movie_id as movie_id,
           m.title as title,
           m.release_date as release_date,
           m.genres as genres,
           m.director as director
    ORDER BY m.release_date
    """

    # 演员合作关系查询
    ACTOR_COLLABORATIONS = """
    MATCH (a1:Actor)-[:ACTED_IN|STARRED_IN]->(m:Movie)<-[:ACTED_IN|STARRED_IN]-(a2:Actor)
    WHERE a1 <> a2 AND id(a1) < id(a2)
    WITH a1, a2, count(DISTINCT m) as collaborations, collect(DISTINCT m.title) as movies
    WHERE collaborations >= $min_collaborations
    RETURN a1.name as actor1,
           a2.name as actor2,
           collaborations,
           movies
    ORDER BY collaborations DESC
    LIMIT $limit
    """

    # 导演演员合作关系查询
    DIRECTOR_ACTOR_COLLABORATIONS = """
    MATCH (d:Director)-[:DIRECTED]->(m:Movie)<-[:ACTED_IN|STARRED_IN]-(a:Actor)
    WHERE d.name = $director
    OPTIONAL MATCH (m)<-[:REVIEWED]-(u:User)
    WITH d, a, count(DISTINCT m) as collaborations, avg(u.score) as avg_rating, count(u) as total_reviews
    WHERE collaborations >= $min_collaborations
    RETURN d.name as director,
           a.name as actor,
           collaborations,
           avg_rating,
           total_reviews
    ORDER BY collaborations DESC
    LIMIT $limit
    """

    # 热门演员组合查询（基于评论数量）
    POPULAR_ACTOR_COMBINATIONS = """
    MATCH (m:Movie)<-[:ACTED_IN|STARRED_IN]-(a1:Actor),
          (m:Movie)<-[:ACTED_IN|STARRED_IN]-(a2:Actor),
          (m:Movie)<-[:ACTED_IN|STARRED_IN]-(a3:Actor)
    WHERE a1 <> a2 AND a2 <> a3 AND a1 <> a3
      AND id(a1) < id(a2) AND id(a2) < id(a3)
      AND any(genre IN m.genres WHERE toLower(genre) CONTAINS toLower($genre))
    WITH [a1.name, a2.name, a3.name] as actor_combo,
         m.genres as genres,
         count(DISTINCT m) as movies_count,
         sum(size([u IN [] WHERE exists((m)<-[:REVIEWED]-(u:User)) | 1])) as total_reviews
    RETURN actor_combo,
           genres,
           movies_count,
           total_reviews
    ORDER BY total_reviews DESC
    LIMIT 10
    """

