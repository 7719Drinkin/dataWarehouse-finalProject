"""
Neo4j数据模型（注释增强版）
"""
from typing import Any, Dict, List, cast
from neo4j import Query  # type: ignore
from app.models.base.base_model import BaseModel, QueryParams
from app.models.neo4j.connection import Neo4jConnection
from app.models.neo4j.queries import Neo4jQueries

class Neo4jModel(BaseModel):
    """Neo4j图数据模型

    提供基于Neo4j图数据库的电影数据查询与分析接口。
    支持以下功能：
        1. 时间维度查询：按年、季度、月、周、日统计电影数量和用户评价数量
        2. 电影维度查询：按导演、演员、类型、多条件组合查询电影及统计信息
        3. 用户评价分析：高评分电影查询、关键字评论查询
        4. 演员-导演关系分析：演员合作次数、导演与演员合作次数、热门演员组合
    """

    def connect(self):
        """建立Neo4j数据库连接

        当模型尚未连接时，通过Neo4jConnection进行健康检查并建立连接。
        """
        if not self.is_connected():
            self._connected = Neo4jConnection.health_check()

    def disconnect(self):
        """断开Neo4j数据库连接

        调用Neo4jConnection关闭驱动并更新连接状态。
        """
        Neo4jConnection.close_driver()
        self._connected = False

    def execute_query(self, query: str, params: QueryParams = None) -> List[Dict[str, Any]]:
        """执行Cypher查询语句

        参数:
            query (str): Cypher 查询语句
            params (QueryParams): 查询参数，必须为字典格式，默认为None

        返回:
            List[Dict[str, Any]]: 查询结果列表，每条记录为字典形式

        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        self._validate_connection()
        query_params = params if isinstance(params, dict) else {}

        with Neo4jConnection.get_session() as session:
            query_obj = cast(Any, Query(cast(Any, query)))
            result = cast(Any, session.run(query_obj, query_params))
            return result.data()

    def execute_non_query(self, query: str, params: QueryParams = None) -> int:
        """执行非查询操作（CREATE, UPDATE, DELETE 等）

        参数:
            query (str): Cypher 操作语句
            params (QueryParams): 操作参数，必须为字典格式，默认为None

        返回:
            int: 受影响的节点和关系总数（nodes_created + nodes_deleted + relationships_created + relationships_deleted）

        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 操作执行失败时抛出
        """
        self._validate_connection()
        query_params = params if isinstance(params, dict) else {}

        with Neo4jConnection.get_session() as session:
            query_obj = cast(Any, Query(cast(Any, query)))
            result = cast(Any, session.run(query_obj, query_params))
            summary = result.consume()
            counters = summary.counters
            return (
                counters.nodes_created +
                counters.nodes_deleted +
                counters.relationships_created +
                counters.relationships_deleted
            )

    # ===========================
    # 一、时间维度查询/统计
    # ===========================
    def get_movies_count_by_year(self) -> List[Dict[str, Any]]:
        """按年份统计电影数量

        返回:
            List[Dict[str, Any]]: 每年上映电影数量统计，包含年份和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_YEAR)

    def get_movies_count_by_quarter(self) -> List[Dict[str, Any]]:
        """按季度统计电影数量

        返回:
            List[Dict[str, Any]]: 每季度电影数量统计，包含季度(Q1/Q2/Q3/Q4)和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_QUARTER)

    def get_movies_count_by_month(self) -> List[Dict[str, Any]]:
        """按月份统计电影数量

        返回:
            List[Dict[str, Any]]: 每月电影数量统计，包含月份和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_MONTH)

    def get_movies_count_by_week(self) -> List[Dict[str, Any]]:
        """按周统计电影数量

        返回:
            List[Dict[str, Any]]: 每周电影数量统计，包含周号和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_WEEK)

    def get_movies_count_by_day(self, date: str) -> List[Dict[str, Any]]:
        """按指定日期统计电影数量

        参数:
            date (str): 指定日期，格式 YYYY-MM-DD

        返回:
            List[Dict[str, Any]]: 当天上映的电影列表及数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_DAY, {'date': date})

    def get_reviews_count_by_year(self) -> List[Dict[str, Any]]:
        """按年份统计用户评价数量

        返回:
            List[Dict[str, Any]]: 每年用户评价数量统计
        """
        return self.execute_query(Neo4jQueries.REVIEWS_COUNT_BY_YEAR)

    def get_reviews_count_by_score(self, min_score: float) -> List[Dict[str, Any]]:
        """按评分区间统计用户评价数量

        参数:
            min_score (float): 最低评分阈值

        返回:
            List[Dict[str, Any]]: 满足评分条件的评价数量统计
        """
        return self.execute_query(Neo4jQueries.REVIEWS_COUNT_BY_SCORE, {'min_score': min_score})

    def get_movies_reviews_stats_by_time(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """按时间段统计电影及其评价信息

        参数:
            start_date (str): 开始日期 YYYY-MM-DD
            end_date (str): 结束日期 YYYY-MM-DD

        返回:
            List[Dict[str, Any]]: 每部电影在指定时间段内的评价数量、平均评分等统计信息
        """
        return self.execute_query(Neo4jQueries.MOVIES_REVIEWS_STATS_BY_TIME, {
            'start_date': start_date,
            'end_date': end_date
        })

    # ===========================
    # 二、电影维度查询/统计
    # ===========================
    def get_movies_versions_by_title(self, title: str) -> List[Dict[str, Any]]:
        """查询指定电影的所有版本

        参数:
            title (str): 电影名称

        返回:
            List[Dict[str, Any]]: 该电影的所有版本信息
        """
        return self.execute_query(Neo4jQueries.MOVIES_VERSIONS_BY_TITLE, {'title': title})

    def get_movie_reviews_by_title(self, title: str) -> List[Dict[str, Any]]:
        """按电影名称查询对应的用户评价

        参数:
            title (str): 电影名称

        返回:
            List[Dict[str, Any]]: 该电影的用户评价信息
        """
        return self.execute_query(Neo4jQueries.MOVIE_REVIEWS_BY_TITLE, {'title': title})

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影

        参数:
            director (str): 导演名称

        返回:
            List[Dict[str, Any]]: 该导演执导的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_director_movie_count(self, director: str) -> List[Dict[str, Any]]:
        """统计导演作品数量

        参数:
            director (str): 导演名称

        返回:
            List[Dict[str, Any]]: 导演作品数量统计
        """
        return self.execute_query(Neo4jQueries.DIRECTOR_MOVIE_COUNT, {'director': director})

    def get_movies_by_actor_starring(self, actor_id: int) -> List[Dict[str, Any]]:
        """查询指定演员主演的电影

        参数:
            actor_id (int): 演员ID

        返回:
            List[Dict[str, Any]]: 该演员主演的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_STARRING, {'actor_id': actor_id})

    def get_movies_by_actor_participated(self, actor_id: int) -> List[Dict[str, Any]]:
        """查询指定演员参演的电影

        参数:
            actor_id (int): 演员ID

        返回:
            List[Dict[str, Any]]: 该演员参演的所有电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor_id': actor_id})

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询电影

        参数:
            genre (str): 电影类型名称

        返回:
            List[Dict[str, Any]]: 指定类型的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_movies_by_multi_condition(
        self,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Neo4j 多条件组合查询

        可选参数：
            - director: 导演名称
            - genre: 类型名称
            - year: 上映年份
            - min_score: 最低平均评分
            - actor: 演员ID

        返回：
            List[Dict[str, Any]]: 电影列表
        """
        where_clauses = []
        params: Dict[str, Any] = {}

        if director:
            where_clauses.append("m.director = $director")
            params["director"] = director
        if genre:
            where_clauses.append("$genre IN m.genres")
            params["genre"] = genre
        if year:
            where_clauses.append("m.release_year = $year")
            params["year"] = year
        if actor:
            where_clauses.append("EXISTS((m)<-[:ACTED_IN]-(a)) AND a.actor_id = $actor")
            params["actor"] = actor

        where_cypher = ""
        if where_clauses:
            where_cypher = "WHERE " + " AND ".join(where_clauses)

        having_cypher = ""
        if min_score is not None:
            having_cypher = "WITH m, AVG(r.score) AS avg_score, COUNT(r) AS review_count WHERE avg_score >= $min_score"
            params["min_score"] = min_score
        else:
            having_cypher = "WITH m, AVG(r.score) AS avg_score, COUNT(r) AS review_count"

        query = f"""
            MATCH (m:Movie)
            OPTIONAL MATCH (m)<-[:REVIEWED]-(r:Review)
            OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Actor)
            {where_cypher}
            {having_cypher}
            RETURN m.movie_id AS movie_id, m.title AS title, m.release_date AS release_date, avg_score, review_count
            ORDER BY avg_score DESC
        """

        return self.execute_query(query, params)

    # ===========================
    # 三、用户评价相关
    # ===========================
    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影

        参数:
            min_score (float): 最低评分阈值，默认4.0
            min_reviews (int): 最少评论数，默认10

        返回:
            List[Dict[str, Any]]: 满足条件的电影列表
        """
        return self.execute_query(Neo4jQueries.HIGH_RATED_MOVIES, {
            'min_score': min_score,
            'min_reviews': min_reviews
        })

    def get_reviews_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """按关键词查询评论

        参数:
            keyword (str): 评论关键词

        返回:
            List[Dict[str, Any]]: 包含关键词的评论列表
        """
        return self.execute_query(Neo4jQueries.REVIEWS_BY_KEYWORD, {'keyword': keyword})

    # ===========================
    # 四、演员-导演关系查询
    # ===========================
    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系

        参数:
            min_collaborations (int): 最少合作次数
            limit (int): 返回结果数上限

        返回:
            List[Dict[str, Any]]: 演员合作关系列表
        """
        return self.execute_query(Neo4jQueries.ACTOR_COLLABORATIONS, {
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演与演员合作关系

        参数:
            director (str): 导演名称
            min_collaborations (int): 最少合作次数
            limit (int): 返回结果数上限

        返回:
            List[Dict[str, Any]]: 导演与演员合作关系列表
        """
        return self.execute_query(Neo4jQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_popular_actor_combinations_by_genre(self, genre: str, limit: int = 10) -> List[Dict[str, Any]]:
        """查询指定类型中热门演员组合

        参数:
            genre (str): 类型名称
            limit (int): 返回结果数上限

        返回:
            List[Dict[str, Any]]: 演员组合及合作电影数量
        """
        return self.execute_query(Neo4jQueries.POPULAR_ACTOR_COMBINATIONS_BY_GENRE, {
            'genre': genre,
            'limit': limit
        })
