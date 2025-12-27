"""
Hive数据模型
-----------------
提供对 Hive 数据仓库的电影数据查询功能，支持多维度统计与分析：
1. 时间维度查询/统计
2. 电影维度查询/统计
3. 用户评价相关查询
4. 演员-导演关系查询
"""

from typing import Any, Dict, List, Optional, cast
from app.models.base.base_model import BaseModel, QueryParams, QueryResult
from app.models.hive.connection import HiveConnection
from app.models.hive.queries import HiveQueries
from app.utils.database_utils import DatabaseUtils
from datetime import datetime


class HiveModel(BaseModel):
    """
    Hive 数据模型类
    -----------------
    提供多种电影数据查询功能，封装 Hive SQL 执行逻辑。
    通过 HiveConnection 建立与 Hive 数据仓库的连接。
    """

    def connect(self):
        """
        建立与 Hive 数据库的连接。
        如果未连接，则通过 HiveConnection 的 health_check 方法检查连接是否正常。
        """
        if not self.is_connected():
            self._connected = HiveConnection.health_check()

    def disconnect(self):
        """
        断开与 Hive 数据库的连接。
        调用 HiveConnection 的 close_connection 方法释放资源。
        """
        HiveConnection.close_connection()
        self._connected = False

    def _validate_connection(self):
        """
        内部方法：验证连接是否已建立。
        如果未连接，则抛出 ConnectionError。
        """
        if not self.is_connected():
            raise ConnectionError("Hive connection is not established")

    def execute_query(self, query: str, params: QueryParams = None) -> QueryResult:
        """
        执行 Hive 查询操作，并返回字典列表。

        参数:
            query (str): HiveQL 查询语句
            params (QueryParams): 查询参数，仅支持字典格式

        返回:
            QueryResult: 查询结果列表，每行数据以字典形式表示

        异常:
            TypeError: 参数格式不正确
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        self._validate_connection()
        formatted_query = query
        query_params = params if isinstance(params, dict) else {}
        query_id = DatabaseUtils.generate_query_id("hive_query", query_params)
        start_time = datetime.now()

        try:
            if params:
                if isinstance(params, dict):
                    formatted_query = query.format(**params)
                else:
                    raise TypeError("Hive model only supports dict-style parameters")

            with HiveConnection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(formatted_query)
                results = cursor.fetchall()

                # PyHive 默认返回 tuple，直接 dict(row) 会报：cannot convert dictionary update sequence...
                # 这里将结果映射为 {col: value} 的 dict
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                dict_results = [dict(zip(columns, row)) for row in results]

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            DatabaseUtils.log_query_performance(
                query_id=query_id,
                db_type="Hive",
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
                db_type="Hive",
                execution_time=(end_time - start_time).total_seconds(),
                success=False,
                error=str(e)
            )
            raise

    def execute_non_query(self, query: str, params: QueryParams = None) -> int:
        """
        执行 Hive 非查询操作（INSERT, UPDATE, DELETE 等）。

        参数:
            query (str): HiveQL 操作语句
            params (QueryParams): 操作参数，仅支持字典格式

        返回:
            int: 受影响的行数（Hive中通常返回0）

        异常:
            TypeError: 参数格式不正确
            ConnectionError: 未建立连接时抛出
            Exception: 操作执行失败时抛出
        """
        self._validate_connection()
        formatted_query = query
        if params:
            if isinstance(params, dict):
                formatted_query = query.format(**params)
            else:
                raise TypeError("Hive model only supports dict-style parameters")

        with HiveConnection.get_connection() as conn:
            cursor = cast(Any, conn.cursor())
            cursor.execute(formatted_query)
            return 0

    # =======================
    # 一、时间维度查询/统计
    # =======================
    def get_movies_by_year(self, year: int) -> QueryResult:
        """按年份查询电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_YEAR, {'year': year})

    def get_movies_by_quarter(self, year: int) -> QueryResult:
        """按季度统计电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_QUARTER, {'year': year})

    def get_movies_by_month(self, year: int) -> QueryResult:
        """按月份统计电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_MONTH, {'year': year})

    def get_movies_by_week(self, year: int) -> QueryResult:
        """按周统计电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_WEEK, {'year': year})

        # -------- 新增：统一时间维度查询 --------
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

        where_conditions: List[str] = []
        params: Dict[str, Any] = {}

        if year is not None:
            where_conditions.append("release_year = {year}")
            params["year"] = year
        if quarter is not None:
            where_conditions.append("release_quarter = {quarter}")
            params["quarter"] = quarter
        if month is not None:
            where_conditions.append("release_month = {month}")
            params["month"] = month
        if week is not None:
            where_conditions.append("release_week = {week}")
            params["week"] = week

        where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = f"""
            SELECT COUNT(*) AS movie_count
            FROM movie_dw.movies_meta_dw
            {where_clause}
        """

        # HiveModel.execute_query 只接受 dict 参数→字符串替换
        return self.execute_query(sql, params)

    def get_movies_by_day(self, date: str) -> QueryResult:
        """查询某天新增电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_DAY, {'date': date})

    def get_movies_by_time_range(self, start_date: str, end_date: str) -> QueryResult:
        """查询某时间段内上映的电影及评价统计"""
        return self.execute_query(HiveQueries.MOVIES_BY_TIME_RANGE, {'start_date': start_date, 'end_date': end_date})

    # =======================
    # 二、电影维度查询/统计
    # =======================
    def get_movies_by_director(self, director: str) -> QueryResult:
        """按导演查询电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_movies_by_actor_starring(self, actor: str) -> QueryResult:
        """查询某演员主演的电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_STARRING, {'actor': actor})

    def get_movies_by_actor_participated(self, actor: str) -> QueryResult:
        """查询某演员参演的所有电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor': actor})

    def get_movies_by_person(
        self,
        director: Optional[str] = None,
        actor: Optional[str] = None,
        starring: Optional[str] = None
    ) -> QueryResult:
        """按人员查询电影（director/actor/starring 任意组合，但至少一个）"""
        if not any([director, actor, starring]):
            return {
                "data": [],
                "execution_time": -1,
                "success": False,
                "error": "至少提供 director / actor / starring 之一"
            }

        where_conditions: List[str] = []
        params: Dict[str, Any] = {}

        if director:
            # movies_meta_dw.director 当前 queries 用 array_contains(director, ...) 写法
            where_conditions.append("array_contains(director, '{director}')")
            params["director"] = director

        if starring:
            where_conditions.append("array_contains(starring, '{starring}')")
            params["starring"] = starring

        if actor:
            where_conditions.append("array_contains(actors, '{actor}')")
            params["actor"] = actor

        where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = HiveQueries.MOVIES_BY_PERSON_TEMPLATE.format(where_clause=where_clause)
        return self.execute_query(sql, params)

    def get_movies_by_genre(self, genre: str) -> QueryResult:
        """按电影类型查询电影统计"""
        return self.execute_query(HiveQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_movies_by_property(
        self,
        title: Optional[str] = None,
        genre: Optional[str] = None
    ) -> QueryResult:
        """按属性查询电影（title / genre 至少一个）"""
        if not any([title, genre]):
            return {
                "data": [],
                "execution_time": -1,
                "success": False,
                "error": "至少提供 title / genre 之一"
            }

        where_conditions: List[str] = []
        params: Dict[str, Any] = {}

        if title:
            # Hive 用字符串格式化，必须自行加引号并做模糊匹配
            where_conditions.append("m.title LIKE '{title}'")
            params["title"] = f"%{title}%"
        if genre:
            where_conditions.append("'{genre}' = ANY(m.genres)")
            params["genre"] = genre

        where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = f"""
            SELECT
                m.movie_id,
                m.title,
                m.release_date,
                m.release_year,
                m.genres
            FROM movie_dw.movies_meta_dw m
            {where_clause}
            ORDER BY m.release_date DESC
        """

        return self.execute_query(sql, params)

    def get_movies_by_multi_condition(
        self,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[str] = None
    ) -> QueryResult:
        """
        Hive 多条件组合查询

        可选参数：
            - director: 导演名称
            - genre: 类型名称
            - year: 上映年份
            - min_score: 最低平均评分
            - actor: 演员名

        返回：
            QueryResult: 满足条件的电影列表
        """
        where_conditions = []
        params: Dict[str, Any] = {}

        if director:
            where_conditions.append("array_contains(m.director, '{director}')")
            params["director"] = director
        if genre:
            where_conditions.append("array_contains(m.genres, '{genre}')")
            params["genre"] = genre
        if year:
            where_conditions.append("m.release_year = {year}")
            params["year"] = year
        if actor:
            # 组合查询 actor 语义：不区分主演/参演，按参演演员集合过滤
            where_conditions.append("array_contains(m.actors, '{actor}')")
            params["actor"] = actor

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        having_clause = ""
        if min_score is not None:
            having_clause = "HAVING AVG(r.score) >= {min_score}"
            params["min_score"] = min_score

        sql = HiveQueries.MOVIES_BY_MULTI_CONDITION_TEMPLATE.format(
            where_clause=where_clause,
            having_clause=having_clause
        )

        return self.execute_query(sql, params)
    # =======================
    # 三、用户评价相关
    # =======================
    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> QueryResult:
        """查询高评分电影"""
        return self.execute_query(HiveQueries.HIGH_RATED_MOVIES, {'min_score': min_score, 'min_reviews': min_reviews})

    def get_high_rated_movies_dynamic(
        self,
        min_score: Optional[float] = None,
        min_reviews: Optional[int] = None
    ) -> QueryResult:
        """高评分电影动态查询（min_score / min_reviews 至少一个）"""
        if min_score is None and min_reviews is None:
            return {
                "data": [],
                "execution_time": -1,
                "success": False,
                "error": "至少提供 min_score / min_reviews 之一"
            }

        where_conditions: List[str] = []
        params: Dict[str, Any] = {}

        if min_score is not None:
            where_conditions.append("avg_score >= {min_score}")
            params["min_score"] = min_score
        if min_reviews is not None:
            where_conditions.append("review_count >= {min_reviews}")
            params["min_reviews"] = min_reviews

        where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = f"""
            SELECT
                movie_id,
                title,
                avg_score,
                review_count
            FROM fact_movie_ratings
            {where_clause}
            ORDER BY avg_score DESC, review_count DESC
        """

        return self.execute_query(sql, params)

    def get_reviews_by_score_range(self, min_score: float, max_score: float) ->QueryResult:
        """按评分区间查询评价"""
        return self.execute_query(HiveQueries.REVIEWS_BY_SCORE_RANGE, {'min_score': min_score, 'max_score': max_score})

    def get_reviews_by_keyword(self, keyword: str) ->QueryResult:
        """按关键词查询评价文本"""
        return self.execute_query(HiveQueries.REVIEWS_BY_KEYWORD, {'keyword': keyword})

    # =======================
    # 四、演员-导演关系查询
    # =======================
    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> QueryResult:
        """查询演员合作关系（演员组合出现次数大于 min_collaborations）"""
        return self.execute_query(HiveQueries.ACTOR_COLLABORATIONS, {'min_collaborations': min_collaborations,
                                                                     'limit': limit})

    def get_actor_actor_collaborations(
        self,
        min_collaborations: int,
        limit: int = 20
    ) -> QueryResult:
        """演员-演员合作关系（合作超过几次）

        说明：基于 HiveQueries.ACTOR_COLLABORATIONS。
        前端只要求传 min_collaborations；limit 为后端可选参数（默认20）。
        """
        return self.execute_query(HiveQueries.ACTOR_COLLABORATIONS, {
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> QueryResult:
        """查询导演与演员的合作关系"""
        return self.execute_query(HiveQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
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
            return {
                "data": [],
                "execution_time": -1,
                "success": False,
                "error": "director 不能为空"
            }

        return self.execute_query(HiveQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': 1,
            'limit': limit
        })


