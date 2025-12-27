"""
Neo4j数据模型（注释增强版）
"""
from typing import Any, Dict, List, Optional, cast
from neo4j import Query  # type: ignore
from app.models.base.base_model import BaseModel, QueryParams, QueryResult
from app.models.neo4j.connection import Neo4jConnection
from app.models.neo4j.queries import Neo4jQueries
from app.utils.database_utils import DatabaseUtils
from datetime import datetime

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

    def execute_query(self, query: str, params: QueryParams = None) -> QueryResult:
        """执行Cypher查询语句

        参数:
            query (str): Cypher 查询语句
            params (QueryParams): 查询参数，必须为字典格式，默认为None

        返回:
            QueryResult: 查询结果列表，每条记录为字典形式

        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        self._validate_connection()
        query_params = params if isinstance(params, dict) else {}
        query_id = DatabaseUtils.generate_query_id("neo4j_query", query_params)
        start_time = datetime.now()

        try:
            with Neo4jConnection.get_session() as session:
                result = session.run(query, query_params)
                dict_results = result.data()

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            DatabaseUtils.log_query_performance(
                query_id=query_id,
                db_type="Neo4j",
                execution_time=(end_time - start_time).total_seconds(),
                success=True
            )
            
            return {
                "data": dict_results,
                "execution_time": execution_time,
                "success": True,
                "error": None
            }

        except Exception as e:
            end_time = datetime.now()
            DatabaseUtils.log_query_performance(
                query_id=query_id,
                db_type="Neo4j",
                execution_time=(end_time - start_time).total_seconds(),
                success=False,
                error=str(e)
            )
            raise

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
    def get_movies_count_by_year(self) -> QueryResult:
        """按年份统计电影数量

        返回:
            QueryResult: 每年上映电影数量统计，包含年份和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_YEAR)

    def get_movies_count_by_quarter(self) -> QueryResult:
        """按季度统计电影数量

        返回:
            QueryResult: 每季度电影数量统计，包含季度(Q1/Q2/Q3/Q4)和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_QUARTER)

    def get_movies_count_by_month(self) -> QueryResult:
        """按月份统计电影数量

        返回:
            QueryResult: 每月电影数量统计，包含月份和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_MONTH)

    def get_movies_count_by_week(self) -> QueryResult:
        """按周统计电影数量

        返回:
            QueryResult: 每周电影数量统计，包含周号和电影数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_WEEK)


    def get_movies_by_time(
        self,
        year: Optional[int] = None,
        quarter: Optional[int] = None,
        month: Optional[int] = None,
        week: Optional[int] = None
    ) -> QueryResult:
        """时间维度动态查询
        参数:
            year: 年份
            quarter: 季度
            month: 月份
            week: 周

        返回:
            QueryResult: 查询结果，包含电影数量
        """
        if not any([year, quarter, month, week]):
            raise ValueError("至少提供 year / quarter / month / week 之一")

        where_conditions = []

        if year is not None:
            where_conditions.append("m.release_year = $year")
        if quarter is not None:
            where_conditions.append("m.release_quarter = $quarter")
        if month is not None:
            where_conditions.append("m.release_month = $month")
        if week is not None:
            where_conditions.append("m.release_week = $week")

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        cypher = f"""
            MATCH (m:Movie)
            {where_clause}
            RETURN count(m) AS movie_count
        """

        return self.execute_query(cypher, {
            "year": year,
            "quarter": quarter,
            "month": month,
            "week": week,
        })

    def get_movies_by_time_dynamic(self, filters: Dict[str, Any]) -> QueryResult:
        """按时间维度动态查询电影列表，并包含评分和评论数。"""
        where_conditions = []
        params: Dict[str, Any] = {}

        time_filters = {
            'year': 'm.release_year = $year',
            'quarter': 'm.release_quarter = $quarter',
            'month': 'm.release_month = $month',
            'week': 'm.release_week = $week'
        }

        for key, value in filters.items():
            if value is not None and key in time_filters:
                where_conditions.append(time_filters[key])
                params[key] = value

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        query = Neo4jQueries.MOVIES_BY_TIME_DYNAMIC_TEMPLATE.format(where_clause=where_clause)
        return self.execute_query(query, params)

    def get_movies_count_by_day(self, date: str) -> QueryResult:
        """按指定日期统计电影数量

        参数:
            date (str): 指定日期，格式 YYYY-MM-DD

        返回:
            QueryResult: 当天上映的电影列表及数量
        """
        return self.execute_query(Neo4jQueries.MOVIES_COUNT_BY_DAY, {'date': date})

    def get_reviews_count_by_year(self) -> QueryResult:
        """按年份统计用户评价数量

        返回:
            QueryResult: 每年用户评价数量统计
        """
        return self.execute_query(Neo4jQueries.REVIEWS_COUNT_BY_YEAR)

    def get_reviews_count_by_score(self, min_score: float) -> QueryResult:
        """按评分区间统计用户评价数量

        参数:
            min_score (float): 最低评分阈值

        返回:
            QueryResult: 满足评分条件的评价数量统计
        """
        return self.execute_query(Neo4jQueries.REVIEWS_COUNT_BY_SCORE, {'min_score': min_score})

    def get_movies_reviews_stats_by_time(self, start_date: str, end_date: str) -> QueryResult:
        """按时间段统计电影及其评价信息

        参数:
            start_date (str): 开始日期 YYYY-MM-DD
            end_date (str): 结束日期 YYYY-MM-DD

        返回:
            QueryResult: 每部电影在指定时间段内的评价数量、平均评分等统计信息
        """
        return self.execute_query(Neo4jQueries.MOVIES_REVIEWS_STATS_BY_TIME, {
            'start_date': start_date,
            'end_date': end_date
        })

    # ===========================
    # 二、电影维度查询/统计
    # ===========================
    def get_movies_versions_by_title(self, title: str) -> QueryResult:
        """查询指定电影的所有版本

        参数:
            title (str): 电影名称

        返回:
            QueryResult: 该电影的所有版本信息
        """
        return self.execute_query(Neo4jQueries.MOVIES_VERSIONS_BY_TITLE, {'title': title})

    def get_movie_reviews_by_title(self, title: str) -> QueryResult:
        """按电影名称查询对应的用户评价

        参数:
            title (str): 电影名称

        返回:
            QueryResult: 该电影的用户评价信息
        """
        return self.execute_query(Neo4jQueries.MOVIE_REVIEWS_BY_TITLE, {'title': title})

    def get_movies_by_director(self, director: str) -> QueryResult:
        """按导演查询电影

        参数:
            director (str): 导演名称

        返回:
            QueryResult: 该导演执导的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_director_movie_count(self, director: str) -> QueryResult:
        """统计导演作品数量

        参数:
            director (str): 导演名称

        返回:
            QueryResult: 导演作品数量统计
        """
        return self.execute_query(Neo4jQueries.DIRECTOR_MOVIE_COUNT, {'director': director})

    def get_movies_by_actor_starring(self, actor_id: int) -> QueryResult:
        """查询指定演员主演的电影（按 actor_id）

        参数:
            actor_id (int): 演员ID

        返回:
            QueryResult: 该演员主演的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_STARRING, {'actor_id': actor_id})

    def get_movies_by_actor_participated(self, actor_id: int) -> QueryResult:
        """查询指定演员参演的电影（按 actor_id）

        参数:
            actor_id (int): 演员ID

        返回:
            QueryResult: 该演员参演的所有电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor_id': actor_id})

    def get_movies_by_actor_name_starring(self, actor_name: str) -> QueryResult:
        """查询指定演员主演的电影（按 actor_name）"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_NAME_STARRING, {'actor_name': actor_name})

    def get_movies_by_actor_name_participated(self, actor_name: str) -> QueryResult:
        """查询指定演员参演的电影（按 actor_name）"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_NAME_PARTICIPATED, {'actor_name': actor_name})

    def get_movies_by_person(
        self,
        director: Optional[str] = None,
        actor: Optional[str] = None,
        starring: Optional[str] = None
    ) -> QueryResult:
        """按人员查询电影（director/actor/starring 任意组合，但至少一个）"""
        if not any([director, actor, starring]):
            raise ValueError("至少提供 director / actor / starring 之一")

        where_conditions: List[str] = []
        params: Dict[str, Any] = {}

        if director:
            where_conditions.append("d.name = $director")
            params["director"] = director

        if actor:
            where_conditions.append("a.name = $actor")
            params["actor"] = actor

        if starring:
            where_conditions.append("s.name = $starring")
            params["starring"] = starring

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        query = Neo4jQueries.MOVIES_BY_PERSON_TEMPLATE.format(where_clause=where_clause)
        return self.execute_query(query, params)

    def get_movies_by_genre(self, genre: str) -> QueryResult:
        """按电影类型查询电影

        参数:
            genre (str): 电影类型名称

        返回:
            QueryResult: 指定类型的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_movies_by_property(
        self,
        title: Optional[str] = None,
        genre: Optional[str] = None
    ) -> QueryResult:
        """按属性查询电影（title / genre 至少一个）"""
        if not any([title, genre]):
            raise ValueError("至少提供 title / genre 之一")

        where_clauses: List[str] = []
        params: Dict[str, Any] = {}

        if title:
            where_clauses.append("toLower(m.title) CONTAINS toLower($title)")
            params["title"] = title
        if genre:
            where_clauses.append("$genre IN m.genres")
            params["genre"] = genre

        where_cypher = ""
        if where_clauses:
            where_cypher = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            MATCH (m:Movie)
            {where_cypher}
            RETURN m.movie_id AS movie_id, m.title AS title, m.release_date AS release_date, m.release_year AS release_year, m.genres AS genres
            ORDER BY m.release_date DESC
        """

        return self.execute_query(query, params)

    def get_movies_by_multi_condition(
        self,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[str] = None
    ) -> QueryResult:
        """
        Neo4j 多条件组合查询

        可选参数：
            - director: 导演名称
            - genre: 类型名称
            - year: 上映年份
            - min_score: 最低平均评分
            - actor: 演员名

        返回：
            QueryResult: 电影列表
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
            where_clauses.append("EXISTS((m)<-[:ACTED_IN]-(a)) AND a.name = $actor")
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
    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> QueryResult:
        """查询高评分电影

        参数:
            min_score (float): 最低评分阈值，默认4.0
            min_reviews (int): 最少评论数，默认10

        返回:
            QueryResult: 满足条件的电影列表
        """
        return self.execute_query(Neo4jQueries.HIGH_RATED_MOVIES, {
            'min_score': min_score,
            'min_reviews': min_reviews
        })

    def get_high_rated_movies_dynamic(
        self,
        min_score: Optional[float] = None,
        min_reviews: Optional[int] = None
    ) -> QueryResult:
        """高评分电影动态查询（min_score / min_reviews 至少一个）"""
        if min_score is None and min_reviews is None:
            raise ValueError("至少提供 min_score / min_reviews 之一")

        where_clauses: List[str] = []
        params: Dict[str, Any] = {}

        if min_score is not None:
            where_clauses.append("avg_score >= $min_score")
            params["min_score"] = min_score
        if min_reviews is not None:
            where_clauses.append("review_count >= $min_reviews")
            params["min_reviews"] = min_reviews

        where_cypher = ""
        if where_clauses:
            where_cypher = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            MATCH (m:Movie)
            OPTIONAL MATCH (m)<-[:REVIEWED]-(r:Review)
            WITH m, AVG(r.score) AS avg_score, COUNT(r) AS review_count
            {where_cypher}
            RETURN m.movie_id AS movie_id, m.title AS title, avg_score, review_count
            ORDER BY avg_score DESC, review_count DESC
        """

        return self.execute_query(query, params)

    def get_reviews_by_keyword(self, keyword: str) -> QueryResult:
        """按关键词查询评论

        参数:
            keyword (str): 评论关键词

        返回:
            QueryResult: 包含关键词的评论列表
        """
        return self.execute_query(Neo4jQueries.REVIEWS_BY_KEYWORD, {'keyword': keyword})

    # ===========================
    # 四、演员-导演关系查询
    # ===========================
    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> QueryResult:
        """查询演员合作关系

        参数:
            min_collaborations (int): 最少合作次数
            limit (int): 返回结果数上限

        返回:
            QueryResult: 演员合作关系列表
        """
        return self.execute_query(Neo4jQueries.ACTOR_COLLABORATIONS, {
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_actor_actor_collaborations(
        self,
        min_collaborations: int,
        limit: int = 20
    ) -> QueryResult:
        """演员-演员合作关系（合作超过几次）

        说明：基于 Neo4jQueries.ACTOR_COLLABORATIONS。
        前端只要求传 min_collaborations；limit 为后端可选参数（默认20）。
        """
        return self.execute_query(Neo4jQueries.ACTOR_COLLABORATIONS, {
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> QueryResult:
        """查询导演与演员合作关系

        参数:
            director (str): 导演名称
            min_collaborations (int): 最少合作次数
            limit (int): 返回结果数上限

        返回:
            QueryResult: 导演与演员合作关系列表
        """
        return self.execute_query(Neo4jQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_director_actor_collaborations_by_director(
        self,
        director: str,
        limit: int = 20
    ) -> QueryResult:
        """导演-演员合作关系（仅要求导演名称）

        说明：前端只要求 director 必填；合作次数阈值在后端固定为 1。
        """
        if not director:
            raise ValueError("director 不能为空")

        return self.execute_query(Neo4jQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': 1,
            'limit': limit
        })

    def get_popular_actor_combinations_by_genre(self, genre: str, limit: int = 10) -> QueryResult:
        """查询指定类型中热门演员组合

        参数:
            genre (str): 类型名称
            limit (int): 返回结果数上限

        返回:
            QueryResult: 演员组合及合作电影数量
        """
        return self.execute_query(Neo4jQueries.POPULAR_ACTOR_COMBINATIONS_BY_GENRE, {
            'genre': genre,
            'limit': limit
        })


