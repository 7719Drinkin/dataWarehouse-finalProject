"""
OpenGauss数据模型
"""
from typing import Any, Dict, List, Optional
from app.models.base.base_model import BaseModel
from app.models.opengauss.connection import OpenGaussConnection
from app.models.opengauss.queries import OpenGaussQueries

class OpenGaussModel(BaseModel):
    """OpenGauss数据模型"""

    def connect(self):
        """建立数据库连接"""
        if not self.is_connected():
            # 使用连接池，不需要显式连接
            self._connected = OpenGaussConnection.health_check()

    def disconnect(self):
        """断开数据库连接"""
        # 连接池管理，不需要显式断开
        self._connected = False

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        self._validate_connection()

        with OpenGaussConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()

                # 转换为字典列表
                return [dict(row) for row in results]

    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """执行非查询操作"""
        self._validate_connection()

        with OpenGaussConnection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount

    # 查询方法
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_YEAR, (year,))

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_DIRECTOR, (f'%{director}%',))

    def get_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询主演电影"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_STARRING, (f'%{actor}%',))

    def get_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询参演电影"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_ACTOR_PARTICIPATED, (f'%{actor}%',))

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询统计"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_GENRE, (f'%{genre}%',))

    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影"""
        return self.execute_query(OpenGaussQueries.HIGH_RATED_MOVIES, (min_score, min_reviews))

    def get_movies_by_time_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """按时间范围查询电影"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_TIME_RANGE, (start_date, end_date))

    def get_movies_by_quarter(self, year: int) -> List[Dict[str, Any]]:
        """按季度查询电影统计"""
        return self.execute_query(OpenGaussQueries.MOVIES_BY_QUARTER, (year,))

    def get_movies_added_tuesday(self, year: int) -> List[Dict[str, Any]]:
        """查询周二新增电影"""
        return self.execute_query(OpenGaussQueries.MOVIES_ADDED_TUESDAY, (year,))

    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系"""
        return self.execute_query(OpenGaussQueries.ACTOR_COLLABORATIONS, (min_collaborations, limit))

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演演员合作关系"""
        return self.execute_query(OpenGaussQueries.DIRECTOR_ACTOR_COLLABORATIONS, (director, min_collaborations, limit))

