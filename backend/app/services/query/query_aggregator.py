from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, cast
from app.models.base.base_model import AggregatedQueryResult
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

    额外：
    - 提供 execute_on_one 用于单库查询（供单库 Controller 复用）
    """

    def __init__(self):
        """初始化三个数据库的 Service 实例"""
        self.opengauss_service = OpenGaussService()
        self.hive_service = HiveService()
        self.neo4j_service = Neo4jService()

    def execute_on_one(self, db_name: str, method_name: str, **params) -> Dict[str, Any]:
        """在指定的单个数据库上执行查询。

        返回结构与 execute_on_all 中各库的 value 一致：
        { "data": [...], "execution_time": 0.12, "success": True, "error"?: str }
        """
        db = db_name.lower()

        if db == 'opengauss':
            service = self.opengauss_service
        elif db == 'hive':
            service = self.hive_service
        elif db == 'neo4j':
            service = self.neo4j_service
        else:
            raise ValueError(f'Unknown database: {db_name}')

        res = self._execute_single(db, service, method_name, **params)
        res.pop('db', None)
        return res

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
        actor: Optional[str] = None,
        **kwargs
    ) -> AggregatedQueryResult:
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

        # 允许 controller 通过 kwargs 透传更多参数（如 starring、month、quarter、week、title、min_reviews 等）
        # 关键：只传非 None 参数，避免 Service 方法收到不支持的关键字参数
        params: Dict[str, Any] = {
            **{k: v for k, v in kwargs.items() if v is not None}
        }

        for k, v in {
            "director": director,
            "genre": genre,
            "year": year,
            "min_score": min_score,
            "actor": actor,
        }.items():
            if v is not None:
                params[k] = v

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

        return cast(AggregatedQueryResult, results)
