"""
Hive数据模型
"""
from typing import Any, Dict, List, cast
from app.models.base.base_model import BaseModel, QueryParams
from app.models.hive.connection import HiveConnection
from app.models.hive.queries import HiveQueries

class HiveModel(BaseModel):
    """Hive数据模型
    
    实现基于 Hive 数据仓库的数据模型，提供电影数据的多种查询功能。
    """

    def connect(self):
        """建立与 Hive 数据库的连接
        
        通过健康检查来验证连接是否成功。
        """
        if not self.is_connected():
            self._connected = HiveConnection.health_check()

    def disconnect(self):
        """断开与 Hive 数据库的连接"""
        HiveConnection.close_connection()
        self._connected = False

    def execute_query(self, query: str, params: QueryParams = None) -> List[Dict[str, Any]]:
        """执行 Hive 查询操作
        
        参数:
            query (str): HiveQL 查询语句
            params (QueryParams): 查询参数，仅支持字典格式 Dict[str, Any]
        
        返回:
            List[Dict[str, Any]]: 查询结果列表
        
        异常:
            TypeError: 当参数不是字典格式时抛出
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        self._validate_connection()

        # 格式化查询字符串（仅支持字典参数）
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

                # 获取列名
                description = cursor.description
                if description:
                    # 使用 cast 告诉类型检查器 description 的类型
                    columns = [cast(str, desc[0]) for desc in cast(List[Any], description)]
                    results = cast(List[Any], cursor.fetchall())

                    # 转换为字典列表
                    result_list: List[Dict[str, Any]] = []
                    for row in results:
                        result_list.append(dict(zip(columns, row)))
                    return result_list
                else:
                    return []

            except Exception as e:
                print(f"Hive query error: {e}")
                print(f"Query: {formatted_query}")
                raise e

    def execute_non_query(self, query: str, params: QueryParams = None) -> int:
        """执行 Hive 非查询操作（INSERT, UPDATE, DELETE 等）
        
        参数:
            query (str): HiveQL 操作语句
            params (QueryParams): 操作参数，仅支持字典格式 Dict[str, Any]
        
        返回:
            int: 受影响的行数（Hive 中通常返回 0）
        
        异常:
            TypeError: 当参数不是字典格式时抛出
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
            # Hive中没有直接的rowcount，返回0
            return 0

    # 查询方法
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影
        
        参数:
            year (int): 电影年份
        
        返回:
            List[Dict[str, Any]]: 匹配年份的电影列表
        """
        return self.execute_query(HiveQueries.MOVIES_BY_YEAR, {'year': year})

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影
        
        参数:
            director (str): 导演名字
        
        返回:
            List[Dict[str, Any]]: 该导演执导的电影列表
        """
        return self.execute_query(HiveQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询主演电影
        
        参数:
            actor (str): 演员名字
        
        返回:
            List[Dict[str, Any]]: 该演员主演的电影列表
        """
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_STARRING, {'actor': actor})

    def get_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询参演电影
        
        参数:
            actor (str): 演员名字
        
        返回:
            List[Dict[str, Any]]: 该演员参演的所有电影列表
        """
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor': actor})

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询统计
        
        参数:
            genre (str): 电影类型
        
        返回:
            List[Dict[str, Any]]: 该类型的电影统计信息
        """
        return self.execute_query(HiveQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影
        
        参数:
            min_score (float): 最低评分阈值，默认 4.0
            min_reviews (int): 最少评论数，默认 10
        
        返回:
            List[Dict[str, Any]]: 满足条件的高评分电影列表
        """
        return self.execute_query(HiveQueries.HIGH_RATED_MOVIES, {
            'min_score': min_score,
            'min_reviews': min_reviews
        })

    def get_movies_by_time_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """按时间范围查询电影
        
        参数:
            start_date (str): 开始日期（格式：YYYY-MM-DD）
            end_date (str): 结束日期（格式：YYYY-MM-DD）
        
        返回:
            List[Dict[str, Any]]: 在指定时间范围内的电影列表
        """
        return self.execute_query(HiveQueries.MOVIES_BY_TIME_RANGE, {
            'start_date': start_date,
            'end_date': end_date
        })

    def get_movies_by_quarter(self, year: int) -> List[Dict[str, Any]]:
        """按季度查询电影统计
        
        参数:
            year (int): 年份
        
        返回:
            List[Dict[str, Any]]: 按季度统计的电影数据
        """
        return self.execute_query(HiveQueries.MOVIES_BY_QUARTER, {'year': year})

    def get_movies_added_tuesday(self, year: int) -> List[Dict[str, Any]]:
        """查询周二新增电影
        
        参数:
            year (int): 年份
        
        返回:
            List[Dict[str, Any]]: 指定年份周二新增的电影列表
        """
        return self.execute_query(HiveQueries.MOVIES_ADDED_TUESDAY, {'year': year})

    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系
        
        参数:
            min_collaborations (int): 最少合作次数，默认 2
            limit (int): 返回结果数上限，默认 20
        
        返回:
            List[Dict[str, Any]]: 演员合作关系列表
        """
        return self.execute_query(HiveQueries.ACTOR_COLLABORATIONS, {
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演演员合作关系
        
        参数:
            director (str): 导演名字
            min_collaborations (int): 最少合作次数，默认 1
            limit (int): 返回结果数上限，默认 10
        
        返回:
            List[Dict[str, Any]]: 该导演与演员的合作关系列表
        """
        return self.execute_query(HiveQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': min_collaborations,
            'limit': limit
        })

