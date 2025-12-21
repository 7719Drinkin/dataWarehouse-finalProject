"""
Neo4j数据模型
"""
from typing import Any, Dict, List, Optional
from app.models.base.base_model import BaseModel
from app.models.neo4j.connection import Neo4jConnection
from app.models.neo4j.queries import Neo4jQueries

class Neo4jModel(BaseModel):
    """Neo4j图数据模型"""

    def connect(self):
        """建立数据库连接"""
        if not self.is_connected():
            self._connected = Neo4jConnection.health_check()

    def disconnect(self):
        """断开数据库连接"""
        Neo4jConnection.close_driver()
        self._connected = False

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        self._validate_connection()

        with Neo4jConnection.get_session() as session:
            result = session.run(query, params or {})
            records = result.data()
            return records

    def execute_non_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """执行非查询操作"""
        self._validate_connection()

        with Neo4jConnection.get_session() as session:
            result = session.run(query, params or {})
            # 返回影响的记录数
            return result.consume().counters.nodes_created + \
                   result.consume().counters.nodes_deleted + \
                   result.consume().counters.relationships_created + \
                   result.consume().counters.relationships_deleted

    # 查询方法
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_YEAR, {'year': year})

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询主演电影"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_STARRING, {'actor': actor})

    def get_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询参演电影"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor': actor})

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询统计"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影"""
        return self.execute_query(Neo4jQueries.HIGH_RATED_MOVIES, {
            'min_score': min_score,
            'min_reviews': min_reviews
        })

    def get_movies_by_time_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """按时间范围查询电影"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_TIME_RANGE, {
            'start_date': start_date,
            'end_date': end_date
        })

    def get_movies_by_quarter(self, year: int) -> List[Dict[str, Any]]:
        """按季度查询电影统计"""
        return self.execute_query(Neo4jQueries.MOVIES_BY_QUARTER, {'year': year})

    def get_movies_added_tuesday(self, year: int) -> List[Dict[str, Any]]:
        """查询周二新增电影"""
        return self.execute_query(Neo4jQueries.MOVIES_ADDED_TUESDAY, {'year': year})

    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系"""
        return self.execute_query(Neo4jQueries.ACTOR_COLLABORATIONS, {
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演演员合作关系"""
        return self.execute_query(Neo4jQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_popular_actor_combinations(self, genre: str) -> List[Dict[str, Any]]:
        """查询热门演员组合"""
        return self.execute_query(Neo4jQueries.POPULAR_ACTOR_COMBINATIONS, {'genre': genre})

