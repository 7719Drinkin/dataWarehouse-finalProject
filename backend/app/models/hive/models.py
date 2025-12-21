"""
Hive数据模型
"""
from typing import Any, Dict, List, Optional
import pandas as pd
from app.models.base.base_model import BaseModel
from app.models.hive.connection import HiveConnection
from app.models.hive.queries import HiveQueries

class HiveModel(BaseModel):
    """Hive数据模型"""

    def connect(self):
        """建立数据库连接"""
        if not self.is_connected():
            self._connected = HiveConnection.health_check()

    def disconnect(self):
        """断开数据库连接"""
        HiveConnection.close_connection()
        self._connected = False

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        self._validate_connection()

        # 格式化查询字符串
        formatted_query = query
        if params:
            formatted_query = query.format(**params)

        with HiveConnection.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(formatted_query)

                # 获取列名
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()

                    # 转换为字典列表
                    return [dict(zip(columns, row)) for row in results]
                else:
                    return []

            except Exception as e:
                print(f"Hive query error: {e}")
                print(f"Query: {formatted_query}")
                raise e

    def execute_non_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """执行非查询操作"""
        self._validate_connection()

        formatted_query = query
        if params:
            formatted_query = query.format(**params)

        with HiveConnection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(formatted_query)
            # Hive中没有直接的rowcount，返回0
            return 0

    # 查询方法
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影"""
        return self.execute_query(HiveQueries.MOVIES_BY_YEAR, {'year': year})

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影"""
        return self.execute_query(HiveQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询主演电影"""
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_STARRING, {'actor': actor})

    def get_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询参演电影"""
        return self.execute_query(HiveQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor': actor})

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询统计"""
        return self.execute_query(HiveQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影"""
        return self.execute_query(HiveQueries.HIGH_RATED_MOVIES, {
            'min_score': min_score,
            'min_reviews': min_reviews
        })

    def get_movies_by_time_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """按时间范围查询电影"""
        return self.execute_query(HiveQueries.MOVIES_BY_TIME_RANGE, {
            'start_date': start_date,
            'end_date': end_date
        })

    def get_movies_by_quarter(self, year: int) -> List[Dict[str, Any]]:
        """按季度查询电影统计"""
        return self.execute_query(HiveQueries.MOVIES_BY_QUARTER, {'year': year})

    def get_movies_added_tuesday(self, year: int) -> List[Dict[str, Any]]:
        """查询周二新增电影"""
        return self.execute_query(HiveQueries.MOVIES_ADDED_TUESDAY, {'year': year})

    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系"""
        return self.execute_query(HiveQueries.ACTOR_COLLABORATIONS, {
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演演员合作关系"""
        return self.execute_query(HiveQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': min_collaborations,
            'limit': limit
        })

