"""
Neo4j数据模型
"""
from typing import Any, Dict, List, cast
from neo4j import Query  # type: ignore
from app.models.base.base_model import BaseModel, QueryParams
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

    def execute_query(self, query: str, params: QueryParams = None) -> List[Dict[str, Any]]:
        """执行查询
        
        参数:
            query (str): Cypher 查询语句
            params (QueryParams): 查询参数，支持字典格式
        
        返回:
            List[Dict[str, Any]]: 查询结果列表
        
        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        self._validate_connection()

        # 确保 params 是字典
        query_params = params if isinstance(params, dict) else {}
        
        with Neo4jConnection.get_session() as session:
            # 使用 Query 对象包装查询字符串以满足类型要求
            # cast 用于处理 Neo4j 严格的 LiteralString 类型检查
            query_obj = cast(Any, Query(cast(Any, query)))
            result = cast(Any, session.run(query_obj, query_params))
            records = result.data()
            return records

    def execute_non_query(self, query: str, params: QueryParams = None) -> int:
        """执行非查询操作（CREATE, UPDATE, DELETE 等）
        
        参数:
            query (str): Cypher 操作语句
            params (QueryParams): 操作参数，支持字典格式
        
        返回:
            int: 受影响的节点和关系总数
        
        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 操作执行失败时抛出
        """
        self._validate_connection()

        # 确保 params 是字典
        query_params = params if isinstance(params, dict) else {}

        with Neo4jConnection.get_session() as session:
            # 使用 Query 对象包装查询字符串以满足类型要求
            # cast 用于处理 Neo4j 严格的 LiteralString 类型检查
            query_obj = cast(Any, Query(cast(Any, query)))
            result = cast(Any, session.run(query_obj, query_params))
            summary = result.consume()
            # 返回影响的记录数
            counters = summary.counters
            return (counters.nodes_created + 
                   counters.nodes_deleted + 
                   counters.relationships_created + 
                   counters.relationships_deleted)

    # 查询方法
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影
        
        参数:
            year (int): 电影年份
        
        返回:
            List[Dict[str, Any]]: 匹配年份的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_YEAR, {'year': year})

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影
        
        参数:
            director (str): 导演名字
        
        返回:
            List[Dict[str, Any]]: 该导演执导的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_DIRECTOR, {'director': director})

    def get_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询主演电影
        
        参数:
            actor (str): 演员名字
        
        返回:
            List[Dict[str, Any]]: 该演员主演的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_STARRING, {'actor': actor})

    def get_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """按演员查询参演电影
        
        参数:
            actor (str): 演员名字
        
        返回:
            List[Dict[str, Any]]: 该演员参演的所有电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_ACTOR_PARTICIPATED, {'actor': actor})

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询统计
        
        参数:
            genre (str): 电影类型
        
        返回:
            List[Dict[str, Any]]: 该类型的电影统计信息
        """
        return self.execute_query(Neo4jQueries.MOVIES_BY_GENRE, {'genre': genre})

    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影
        
        参数:
            min_score (float): 最低评分阈值，默认 4.0
            min_reviews (int): 最少评论数，默认 10
        
        返回:
            List[Dict[str, Any]]: 满足条件的高评分电影列表
        """
        return self.execute_query(Neo4jQueries.HIGH_RATED_MOVIES, {
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
        return self.execute_query(Neo4jQueries.MOVIES_BY_TIME_RANGE, {
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
        return self.execute_query(Neo4jQueries.MOVIES_BY_QUARTER, {'year': year})

    def get_movies_added_tuesday(self, year: int) -> List[Dict[str, Any]]:
        """查询周二新增电影
        
        参数:
            year (int): 年份
        
        返回:
            List[Dict[str, Any]]: 指定年份周二新增的电影列表
        """
        return self.execute_query(Neo4jQueries.MOVIES_ADDED_TUESDAY, {'year': year})

    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系
        
        参数:
            min_collaborations (int): 最少合作次数，默认 2
            limit (int): 返回结果数上限，默认 20
        
        返回:
            List[Dict[str, Any]]: 演员合作关系列表
        """
        return self.execute_query(Neo4jQueries.ACTOR_COLLABORATIONS, {
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
        return self.execute_query(Neo4jQueries.DIRECTOR_ACTOR_COLLABORATIONS, {
            'director': director,
            'min_collaborations': min_collaborations,
            'limit': limit
        })

    def get_popular_actor_combinations(self, genre: str) -> List[Dict[str, Any]]:
        """查询热门演员组合
        
        参数:
            genre (str): 电影类型
        
        返回:
            List[Dict[str, Any]]: 该类型中的热门演员组合
        """
        return self.execute_query(Neo4jQueries.POPULAR_ACTOR_COMBINATIONS, {'genre': genre})

