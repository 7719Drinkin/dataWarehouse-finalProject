"""
OpenGauss数据模型
-----------------
提供对 OpenGauss 数据库的电影数据查询功能，支持多维度统计与分析：
1. 时间维度查询/统计
2. 电影维度查询/统计
3. 用户评价相关查询
4. 演员-导演关系查询
注：溯源查询在应用中不实现
"""

from typing import Any, Dict, List, Optional
from app.models.base.base_model import BaseModel, QueryParams, QueryResult
from app.models.opengauss.connection import OpenGaussConnection
from app.models.opengauss.queries import OpenGaussQueries
from app.utils.database_utils import DatabaseUtils
from datetime import datetime


class OpenGaussModel(BaseModel):
    """
    OpenGauss 数据模型类
    ---------------------
    封装基于 OpenGauss 数据库的电影数据查询功能。
    支持 SQL 查询和事务管理，返回字典列表形式的数据。
    """

    def connect(self):
        """建立数据库连接。"""
        if not self.is_connected():
            self._connected = OpenGaussConnection.health_check()

    def disconnect(self):
        """断开数据库连接。"""
        self._connected = False

    def _validate_connection(self):
        """验证连接是否已建立。"""
        if not self.is_connected():
            raise ConnectionError("OpenGauss connection is not established")

    def execute_query(self, query: str, params: QueryParams = None) -> QueryResult:
        """执行查询并返回统一结构，同时记录性能日志。"""
        self._validate_connection()
        query_params = params if isinstance(params, (tuple, dict, type(None))) else ()
        query_id = DatabaseUtils.generate_query_id("opengauss_query", params if isinstance(params, dict) else {})
        start_time = datetime.now()

        try:
            with OpenGaussConnection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, query_params or ())
                    results = cursor.fetchall()
                    dict_results = [dict(row) for row in results]

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            DatabaseUtils.log_query_performance(
                query_id=query_id,
                db_type="OpenGauss",
                execution_time=execution_time,
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
            execution_time = (end_time - start_time).total_seconds()

            DatabaseUtils.log_query_performance(
                query_id=query_id,
                db_type="OpenGauss",
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            raise

    def execute_non_query(self, query: str, params: QueryParams = None) -> int:
        """执行非查询并提交事务。"""
        self._validate_connection()
        query_params = params if isinstance(params, (tuple, type(None))) else ()
        with OpenGaussConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, query_params or ())
                conn.commit()
                return cursor.rowcount

    # ===========================
    # 一、时间维度查询/统计
    # ===========================
    def get_movies_by_year(self, year: int) -> QueryResult:
        """按年份查询电影列表"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_YEAR, (year,))

    def get_movies_by_quarter(self, year: int) -> QueryResult:
        """按季度统计电影数量"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_QUARTER, (year,))

    def get_movies_by_month(self, year: int) -> QueryResult:
        """按月份统计电影数量"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_MONTH, (year,))

    def get_movies_by_week(self, year: int) -> QueryResult:
        """按周统计电影数量"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_WEEK, (year,))

    def get_movies_by_day(self, day: str) -> QueryResult:
        """查询指定日期上映的电影"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_DAY, (day,))

    def get_movies_by_time(
        self,
        year: Optional[int] = None,
        quarter: Optional[int] = None,
        month: Optional[int] = None,
        week: Optional[int] = None
    ) -> QueryResult:
        """时间维度动态查询：返回电影数量。"""
        if not any([year, quarter, month, week]):
            raise ValueError("至少提供 year / quarter / month / week 之一")

        where_conditions = []
        params: Dict[str, Any] = {}

        if year is not None:
            where_conditions.append("release_year = %(year)s")
            params["year"] = year
        if quarter is not None:
            where_conditions.append("release_quarter = %(quarter)s")
            params["quarter"] = quarter
        if month is not None:
            where_conditions.append("release_month = %(month)s")
            params["month"] = month
        if week is not None:
            where_conditions.append("release_week = %(week)s")
            params["week"] = week

        where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = f"""
            SELECT
                COUNT(*) AS movie_count
            FROM dim_movies
            {where_clause};
        """

        return self.execute_query(sql, params)

    def get_movies_by_time_dynamic(self, filters: Dict[str, Any]) -> QueryResult:
        """按时间维度动态查询电影列表，并包含评分和评论数。"""
        where_conditions = []
        params: Dict[str, Any] = {}

        time_filters = {
            'year': 'm.release_year = %(year)s',
            'quarter': 'm.release_quarter = %(quarter)s',
            'month': 'm.release_month = %(month)s',
            'week': 'm.release_week = %(week)s'
        }

        for key, value in filters.items():
            if value is not None and key in time_filters:
                where_conditions.append(time_filters[key])
                params[key] = value

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = OpenGaussQueries.MOVIES_BY_TIME_DYNAMIC_TEMPLATE.format(where_clause=where_clause)
        return self.execute_query(sql, params)

    def get_reviews_count_by_time(self, year: int) -> QueryResult:
        """按年份统计用户评价数量"""
        return self.execute_query(OpenGaussQueries.REVIEWS_COUNT_BY_TIME, (year,))

    def get_reviews_count_by_score(self, min_score: float) -> QueryResult:
        """统计评分高于指定分数的评价数量"""
        return self.execute_query(OpenGaussQueries.REVIEWS_COUNT_BY_SCORE, (min_score,))

    def get_movies_reviews_stats_by_time(self, start_date: str, end_date: str) -> QueryResult:
        """查询某时间段内电影及其评价统计信息（数量、平均分等）"""
        return self.execute_query(OpenGaussQueries.MOVIES_REVIEWS_STATS_BY_TIME, (start_date, end_date))

    # ===========================
    # 二、电影维度查询/统计
    # ===========================
    def get_movies_versions_by_title(self, title: str) -> QueryResult:
        """查询指定电影的所有版本信息"""
        return self.execute_query(OpenGaussQueries.MOVIES_VERSIONS_BY_TITLE, (title,))

    def get_movie_reviews_by_title(self, title: str) -> QueryResult:
        """查询指定电影的所有用户评价"""
        return self.execute_query(OpenGaussQueries.MOVIE_REVIEWS_BY_TITLE, (title,))

    def get_movies_by_director(self, director: str) -> QueryResult:
        """查询指定导演的电影列表"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_DIRECTOR, (director,))

    def get_director_movie_count(self, director: str) -> QueryResult:
        """统计指定导演拍摄的电影数量"""
        return self.execute_query(OpenGaussQueries.DIRECTOR_MOVIE_COUNT, (director,))

    def get_movies_by_actor_starring(self, actor_id: int) -> QueryResult:
        """查询指定演员主演的电影列表（按 actor_id）"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_STARRING, (actor_id,))

    def get_movies_by_actor_participated(self, actor_id: int) -> QueryResult:
        """查询指定演员参演的所有电影（按 actor_id）"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_PARTICIPATED, (actor_id,))

    def get_movies_by_actor_name_starring(self, actor_name: str) -> QueryResult:
        """查询指定演员主演的电影列表（按 actor_name）"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_NAME_STARRING, (actor_name,))

    def get_movies_by_actor_name_participated(self, actor_name: str) -> QueryResult:
        """查询指定演员参演的所有电影（按 actor_name）"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_NAME_PARTICIPATED, (actor_name,))

    def get_movies_by_person(
        self,
        director: Optional[str] = None,
        actor: Optional[str] = None,
        starring: Optional[str] = None
    ) -> QueryResult:
        """按人员查询电影（director/actor/starring 任意组合，但至少一个）"""
        if not any([director, actor, starring]):
            raise ValueError("至少提供 director / actor / starring 之一")

        where_conditions = []
        params: Dict[str, Any] = {}

        # 注意：dim_movies.director 是 TEXT[]，不能写成 m.director = 'xxx'
        # 正确写法：'%(director)s = ANY(m.director)'
        if director is not None:
            # 支持模糊匹配：director 是 TEXT[]，用 UNNEST 展开后 ILIKE
            where_conditions.append("EXISTS (SELECT 1 FROM UNNEST(m.director) AS d WHERE d ILIKE %(director)s)")
            params["director"] = f"%{director}%"

        # actor / starring 通过 movie_actor + dim_actors 关联来过滤（你没有把 actors/starring 存在 dim_movies 里）
        if actor is not None:
            where_conditions.append("a.actor_name ILIKE %(actor)s")
            params["actor"] = f"%{actor}%"

        if starring is not None:
            where_conditions.append("a.actor_name ILIKE %(starring)s AND ma.is_lead = TRUE")
            params["starring"] = f"%{starring}%"

        where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = OpenGaussQueries.MOVIES_BY_PERSON_TEMPLATE.format(where_clause=where_clause)
        return self.execute_query(sql, params)

    def get_movies_by_property(
        self,
        title: Optional[str] = None,
        genre: Optional[str] = None
    ) -> QueryResult:
        """按属性查询电影（title/genre 任意组合，但至少一个）"""
        if not any([title, genre]):
            raise ValueError("至少提供 title / genre 之一")

        where_conditions = []
        params: Dict[str, Any] = {}

        if title is not None:
            where_conditions.append("title ILIKE %(title)s")
            params["title"] = f"%{title}%"
        if genre is not None:
            where_conditions.append("%(genre)s = ANY(genres)")
            params["genre"] = genre

        where_clause = "WHERE " + " AND ".join(where_conditions)

        sql = f"""
            SELECT
                movie_id AS id,
                title,
                release_date,
                director,
                genres,
                0::numeric AS rating,
                0::int AS review_count
            FROM dim_movies
            {where_clause}
            LIMIT 200;
        """

        return self.execute_query(sql, params)

    # ===========================
    # 三、用户评价相关
    # ===========================
    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> QueryResult:
        """查询高评分电影（评分≥min_score 且评论数≥min_reviews）"""
        return self.execute_query(OpenGaussQueries.HIGH_RATED_MOVIES, (min_score, min_reviews))

    def get_high_rated_movies_dynamic(
        self,
        min_score: Optional[float] = None,
        min_reviews: Optional[int] = None
    ) -> QueryResult:
        """高评分电影动态查询（min_score / min_reviews 至少一个）

        重要：
        - 你的 OpenGauss 建表中没有 fact_movie_ratings。
        - 因此这里用 fact_reviews 聚合得到每部电影的 avg_score 与 review_count。
        - 用 dim_movies 拿 title。
        """
        if min_score is None and min_reviews is None:
            raise ValueError("至少提供 min_score / min_reviews 之一")

        having_conditions: List[str] = []
        params: Dict[str, Any] = {}

        if min_score is not None:
            having_conditions.append("AVG(r.score) >= %(min_score)s")
            params["min_score"] = min_score
        if min_reviews is not None:
            having_conditions.append("COUNT(*) >= %(min_reviews)s")
            params["min_reviews"] = min_reviews

        having_clause = ""
        if having_conditions:
            having_clause = "HAVING " + " AND ".join(having_conditions)

        sql = f"""
            SELECT
                m.movie_id AS movie_id,
                m.title AS title,
                AVG(r.score) AS avg_score,
                COUNT(*) AS review_count
            FROM dim_movies m
            JOIN fact_reviews r
              ON r.movie_id = m.movie_id
            GROUP BY m.movie_id, m.title
            {having_clause}
            ORDER BY avg_score DESC, review_count DESC
        """

        return self.execute_query(sql, params)

    def get_reviews_by_keyword(self, keyword: str) -> QueryResult:
        """按关键词查询用户评价文本"""
        return self.execute_query(OpenGaussQueries.REVIEWS_BY_KEYWORD, (f'%{keyword}%',))

    # ===========================
    # 四、演员-导演关系查询
    # ===========================
    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> QueryResult:
        """查询演员合作关系（合作次数≥min_collaborations）"""
        return self.execute_query(OpenGaussQueries.ACTOR_COLLABORATIONS, (min_collaborations, limit))

    def get_actor_actor_collaborations(
        self,
        min_collaborations: int,
        limit: int = 20
    ) -> QueryResult:
        """演员-演员合作关系（合作超过几次）"""
        return self.execute_query(
            OpenGaussQueries.ACTOR_COLLABORATIONS,
            (min_collaborations, limit)
        )

    def get_director_actor_collaborations_by_director(
        self,
        director: str,
        limit: int = 20
    ) -> QueryResult:
        """导演-演员合作关系（仅要求导演名称）"""
        if not director:
            raise ValueError("director 不能为空")

        return self.execute_query(
            OpenGaussQueries.DIRECTOR_ACTOR_COLLABORATIONS,
            (director, 1, limit)
        )

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> QueryResult:
        """查询导演与演员的合作关系"""
        return self.execute_query(OpenGaussQueries.DIRECTOR_ACTOR_COLLABORATIONS, (director, min_collaborations, limit))

    def get_popular_actor_combinations_by_genre(self, genre: str, limit: int = 10) -> QueryResult:
        """查询某类型电影中最受欢迎的演员组合"""
        return self.execute_query(OpenGaussQueries.POPULAR_ACTOR_COMBINATIONS_BY_GENRE, (genre, limit))
