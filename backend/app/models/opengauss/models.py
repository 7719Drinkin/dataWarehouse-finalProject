"""
OpenGauss数据模型
"""
from typing import Any, Dict, List, cast, Tuple
from app.models.base.base_model import BaseModel, QueryParams
from app.models.opengauss.connection import OpenGaussConnection
from app.models.opengauss.queries import OpenGaussQueries

class OpenGaussModel(BaseModel):
    """OpenGauss数据模型
    
    实现基于 OpenGauss 数据库的数据模型，支持 SQL 查询和事务管理。
    """

    def connect(self):
        """建立数据库连接
        
        OpenGauss 使用连接池管理，通过健康检查验证连接。
        """
        if not self.is_connected():
            # 使用连接池，不需要显式连接
            self._connected = OpenGaussConnection.health_check()

    def disconnect(self):
        """断开数据库连接
        
        连接池管理，不需要显式断开，直接更新状态标记。
        """
        # 连接池管理，不需要显式断开
        self._connected = False

    def execute_query(self, query: str, params: QueryParams = None) -> List[Dict[str, Any]]:
        """执行查询操作
        
        参数:
            query (str): SQL 查询语句
            params (QueryParams): 查询参数，支持元组格式的位置参数
        
        返回:
            List[Dict[str, Any]]: 查询结果列表，每个元素是一条记录的字典表示
        
        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        self._validate_connection()

        # 确保 params 是元组或 None
        query_params = params if isinstance(params, (tuple, type(None))) else ()

        with OpenGaussConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, query_params or ())
                results = cursor.fetchall()

                # 转换为字典列表
                return [dict(row) for row in results]

    def execute_non_query(self, query: str, params: QueryParams = None) -> int:
        """执行非查询操作（INSERT, UPDATE, DELETE）
        
        参数:
            query (str): SQL 操作语句
            params (QueryParams): 操作参数，支持元组格式的位置参数
        
        返回:
            int: 受影响的行数
        
        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 操作执行失败时抛出
        """
        self._validate_connection()

        # 确保 params 是元组或 None
        query_params = params if isinstance(params, (tuple, type(None))) else ()

        with OpenGaussConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, query_params or ())
                conn.commit()
                return cursor.rowcount

    # 查询方法
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影
        
        参数:
            year (int): 电影年份
        
        返回:
            List[Dict[str, Any]]: 匹配年份的电影列表
        """
        return self.execute_query(OpenGaussQueries.MOVIES_BY_YEAR, (year,))

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影
        
        参数:
            director (str): 导演名字
        
        返回:
            List[Dict[str, Any]]: 该导演执导的电影列表
        """
        return self.execute_query(OpenGaussQueries.MOVIES_BY_DIRECTOR, (f'%{director}%',))

    def get_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询主演电影
        
        参数:
            actor (str): 演员名字
        
        返回:
            List[Dict[str, Any]]: 该演员主演的电影列表
        """
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_STARRING, (f'%{actor}%',))

    def get_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询参演电影
        
        参数:
            actor (str): 演员名字
        
        返回:
            List[Dict[str, Any]]: 该演员参演的所有电影列表
        """
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_PARTICIPATED, (f'%{actor}%',))

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询统计
        
        参数:
            genre (str): 电影类型
        
        返回:
            List[Dict[str, Any]]: 该类型的电影统计信息
        """
        return self.execute_query(OpenGaussQueries.MOVIES_BY_GENRE, (f'%{genre}%',))

    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影
        
        参数:
            min_score (float): 最低评分阈值，默认 4.0
            min_reviews (int): 最少评论数，默认 10
        
        返回:
            List[Dict[str, Any]]: 满足条件的高评分电影列表
        """
        return self.execute_query(OpenGaussQueries.HIGH_RATED_MOVIES, (min_score, min_reviews))

    def get_movies_by_time_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """按时间范围查询电影
        
        参数:
            start_date (str): 开始日期（格式：YYYY-MM-DD）
            end_date (str): 结束日期（格式：YYYY-MM-DD）
        
        返回:
            List[Dict[str, Any]]: 在指定时间范围内的电影列表
        """
        return self.execute_query(OpenGaussQueries.MOVIES_BY_TIME_RANGE, (start_date, end_date))

    def get_movies_by_quarter(self, year: int) -> List[Dict[str, Any]]:
        """按季度查询电影统计
        
        参数:
            year (int): 年份
        
        返回:
            List[Dict[str, Any]]: 按季度统计的电影数据
        """
        return self.execute_query(OpenGaussQueries.MOVIES_BY_QUARTER, (year,))

    def get_movies_added_tuesday(self, year: int) -> List[Dict[str, Any]]:
        """查询周二新增电影
        
        参数:
            year (int): 年份
        
        返回:
            List[Dict[str, Any]]: 指定年份周二新增的电影列表
        """
        return self.execute_query(OpenGaussQueries.MOVIES_ADDED_TUESDAY, (year,))

    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系
        
        参数:
            min_collaborations (int): 最少合作次数，默认 2
            limit (int): 返回结果数上限，默认 20
        
        返回:
            List[Dict[str, Any]]: 演员合作关系列表
        """
        return self.execute_query(OpenGaussQueries.ACTOR_COLLABORATIONS, (min_collaborations, limit))

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演演员合作关系
        
        参数:
            director (str): 导演名字
            min_collaborations (int): 最少合作次数，默认 1
            limit (int): 返回结果数上限，默认 10
        
        返回:
            List[Dict[str, Any]]: 该导演与演员的合作关系列表
        """
        return self.execute_query(OpenGaussQueries.DIRECTOR_ACTOR_COLLABORATIONS, (director, min_collaborations, limit))

