"""
Hive数据模型
-----------------
提供对 Hive 数据仓库的电影数据查询功能，支持多维度统计与分析：
1. 时间维度查询/统计
2. 电影维度查询/统计
3. 用户评价相关查询
4. 演员-导演关系查询
"""

from typing import Any, Dict, List, cast
from app.models.base.base_model import BaseModel, QueryParams
from app.models.hive.connection import HiveConnection
from app.models.hive.queries import HiveQueries


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

    def execute_query(self, query: str, params: QueryParams = None) -> List[Dict[str, Any]]:
        """
        执行 Hive 查询操作，并返回字典列表。

        参数:
            query (str): HiveQL 查询语句
            params (QueryParams): 查询参数，仅支持字典格式

        返回:
            List[Dict[str, Any]]: 查询结果列表，每行数据以字典形式表示

        异常:
            TypeError: 参数格式不正确
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        self._validate_connection()

        # 格式化查询字符串
        formatted_query = query
        if params:
            if isinstance(params, dict):
                formatted_query = query.format(**params)
            else:
                raise TypeError("Hive model only supports dict-style parameters")

        with HiveConnection.get_connection() as conn:
            cursor = cast(Any, conn.cursor())
            try:
                cursor.execute(formatted_query)
                description = cursor.description
                if description:
                    columns = [cast(str, desc[0]) for desc in cast(List[Any], description)]
                    results = cast(List[Any], cursor.fetchall())
                    return [dict(zip(columns, row)) for row in results]
                else:
                    return []
            except Exception as e:
                print(f"Hive query error: {e}")
                print(f"Query: {formatted_query}")
                raise e

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
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_YEAR, {'year': year})

    def get_movies_by_quarter(self, year: int) -> List[Dict[str, Any]]:
        """按季度统计电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_QUARTER, {'year': year})

    def get_movies_by_month(self, year: int) -> List[Dict[str, Any]]:
        """按月份统计电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_MONTH, {'year': year})

    def get_movies_by_week(self, year: int) -> List[Dict[str, Any]]:
        """按周统计电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_WEEK, {'year': year})

    def get_movies_by_day(self, date: str) -> List[Dict[str, Any]]:
        """查询某天新增电影数量"""
        return self.execute_query(HiveQueries.MOVIES_BY_DAY, {'date': date})

    def get_movies_by_time_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """查询某时间段内上映的电影及评价统计"""
        return self.execute_query(HiveQueries.MOVIES_BY_TIME_RANGE, {'start_date': start_date, 'end_date': end_date})

    # =======================
    # 二、电影维度查询/统计
    # =======================
    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """查询某演员主演的电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_STARRING, {'actor': actor})

    def get_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """查询某演员参演的所有电影列表"""
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor': actor})

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询电影统计"""
        return self.execute_query(HiveQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_movies_by_multi_condition(
        self,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Hive 多条件组合查询

        可选参数：
            - director: 导演名称
            - genre: 类型名称
            - year: 上映年份
            - min_score: 最低平均评分
            - actor: 演员ID（主演或参演）

        返回：
            List[Dict[str, Any]]: 满足条件的电影列表
        """
        where_conditions = []
        params: Dict[str, Any] = {}

        if director:
            where_conditions.append("m.director = '{director}'")
            params["director"] = director
        if genre:
            where_conditions.append("'{genre}' = ANY(m.genres)")
            params["genre"] = genre
        if year:
            where_conditions.append(f"m.release_year = {year}")
            params["year"] = year
        if actor:
            where_conditions.append(f"ma.actor_id = {actor}")
            params["actor"] = actor

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        having_clause = ""
        if min_score is not None:
            having_clause = f"HAVING AVG(r.score) >= {min_score}"
            params["min_score"] = min_score

        sql = HiveQueries.MOVIES_BY_MULTI_CONDITION_TEMPLATE.format(
            where_clause=where_clause,
            having_clause=having_clause
        )

        return self.execute_query(sql, params)
    # =======================
    # 三、用户评价相关
    # =======================
    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影"""
        return self.execute_query(HiveQueries.HIGH_RATED_MOVIES, {'min_score': min_score, 'min_reviews': min_reviews})

    def get_reviews_by_score_range(self, min_score: float, max_score: float) -> List[Dict[str, Any]]:
        """按评分区间查询评价"""
        return self.execute_query(HiveQueries.REVIEWS_BY_SCORE_RANGE, {'min_score': min_score, 'max_score': max_score})

    def get_reviews_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """按关键词查询评价文本"""
        return self.execute_query(HiveQueries.REVIEWS_BY_KEYWORD, {'keyword': keyword})

    # =======================
    # 四、演员-导演关系查询
    # =======================
    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系（演员组合出现次数大于 min_collaborations）"""
        return self.execute_query(HiveQueries.ACTOR_COLLABORATIONS, {'min_collaborations': min_collaborations,
                                                                     'limit': limit})

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演与演员的合作关系"""
        return self.execute_query(HiveQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': min_collaborations,
            'limit': limit
        })
