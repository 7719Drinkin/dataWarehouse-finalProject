from typing import Dict, List, Any, Optional
from .opengauss_service import OpenGaussService
from .hive_service import HiveService
from .neo4j_service import Neo4jService

class QueryAggregator:
    """
    多数据库统一聚合查询服务

    可以在 OpenGauss、Hive 和 Neo4j 三类数据库上执行同名查询方法，
    返回统一字典结构的结果。支持多条件查询的可选参数。
    """

    def __init__(self):
        """初始化聚合服务，创建三个数据库的 Service 实例"""
        self.opengauss_service = OpenGaussService()
        self.hive_service = HiveService()
        self.neo4j_service = Neo4jService()

    def execute_on_all(
        self,
        method_name: str,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[int] = None,
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        在三类数据库上执行同名方法，并返回结果

        支持多条件查询参数：
            - director: 导演名称
            - genre: 类型
            - year: 上映年份
            - min_score: 最低平均评分
            - actor: 演员ID

        其他查询参数可通过 **kwargs 传递给各 Service 层

        返回:
            Dict[str, List[Dict]]: 各数据库查询结果
        """
        results: Dict[str, List[Dict[str, Any]]] = {}

        # 遍历三类数据库服务
        for db_name, service in [
            ("opengauss", self.opengauss_service),
            ("hive", self.hive_service),
            ("neo4j", self.neo4j_service)
        ]:
            try:
                with service as s:
                    func = getattr(s, method_name)
                    # 自动传递多条件查询参数 + 其他 kwargs
                    results[db_name] = func(
                        director=director,
                        genre=genre,
                        year=year,
                        min_score=min_score,
                        actor=actor,
                        **kwargs
                    )
            except Exception as e:
                print(f"Error querying {db_name}: {e}")
                results[db_name] = []

        return results
