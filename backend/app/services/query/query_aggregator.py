from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional
from .opengauss_service import OpenGaussService
from .hive_service import HiveService
from .neo4j_service import Neo4jService


class QueryAggregator:
    """
    多数据库统一聚合查询服务（并发执行）

    设计原则：
    - 不在 Aggregator 层做时间统计
    - execution_time 完全来自 Model 层
    - 结果结构直接返回给前端
    """

    def __init__(self):
        """初始化三个数据库的 Service 实例"""
        self.opengauss_service = OpenGaussService()
        self.hive_service = HiveService()
        self.neo4j_service = Neo4jService()

    def _execute_single(
        self,
        db_name: str,
        service,
        method_name: str,
        **params
    ) -> Dict[str, Any]:
        """
        执行单个数据库查询（供线程池调用）

        返回结构示例：
        {
            "db": "opengauss",
            "data": [...],
            "execution_time": 0.123,
            "success": True
        }
        """
        try:
            with service as s:
                func = getattr(s, method_name)

                # ⚠️ 这里直接接收 Model 返回的 dict
                result = func(**params)

                return {
                    "db": db_name,
                    **result
                }

        except Exception as e:
            # 如果 Service / Model 抛异常，这里兜底
            return {
                "db": db_name,
                "data": [],
                "execution_time": None,
                "success": False,
                "error": str(e)
            }

    def execute_on_all(
        self,
        method_name: str,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        在三个数据库上并发执行同名查询方法

        返回给前端的最终结构：
        {
            "opengauss": {
                "data": [...],
                "execution_time": 0.12,
                "success": True
            },
            "hive": {
                "data": [...],
                "execution_time": 0.98,
                "success": True
            },
            "neo4j": {
                "data": [...],
                "execution_time": 0.31,
                "success": True
            }
        }
        """

        params = dict(
            director=director,
            genre=genre,
            year=year,
            min_score=min_score,
            actor=actor,
            **kwargs
        )

        services = [
            ("opengauss", self.opengauss_service),
            ("hive", self.hive_service),
            ("neo4j", self.neo4j_service)
        ]

        results: Dict[str, Dict[str, Any]] = {}

        # 并发执行三个数据库查询
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    self._execute_single,
                    db_name,
                    service,
                    method_name,
                    **params
                )
                for db_name, service in services
            ]

            for future in as_completed(futures):
                res = future.result()
                db_name = res.pop("db")
                results[db_name] = res

        return results
