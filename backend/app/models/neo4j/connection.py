"""
Neo4j数据库连接管理
"""
from typing import Any, cast
from neo4j import GraphDatabase  # type: ignore
from contextlib import contextmanager
from config.database import DatabaseConfig

class Neo4jConnection:
    """Neo4j连接管理器
    
    提供 Neo4j 连接的统一管理，支持连接池和会话管理。
    """

    _driver: Any = None

    @classmethod
    def get_driver(cls) -> Any:
        """获取Neo4j驱动
        
        返回:
            Neo4j Driver 对象，如果未初始化则先初始化
        """
        if cls._driver is None:
            config = DatabaseConfig()
            conn_params = config.get_neo4j_connection_params()
            cls._driver = GraphDatabase.driver(**conn_params)  # type: ignore
        return cls._driver

    @classmethod
    @contextmanager
    def get_session(cls):  # type: ignore
        """获取数据库会话的上下文管理器
        
        返回:
            Neo4j Session 对象
        
        用法:
            with Neo4jConnection.get_session() as session:
                result = session.run("MATCH (n) RETURN n LIMIT 5")
        """
        session = None
        try:
            session = cls.get_driver().session()  # type: ignore
            yield session
        finally:
            if session:
                session.close()

    @classmethod
    def close_driver(cls) -> None:
        """关闭驱动
        
        关闭 Neo4j 驱动连接，释放所有资源。
        """
        if cls._driver:
            cls._driver.close()
            cls._driver = None

    @classmethod
    def health_check(cls) -> bool:
        """健康检查
        
        通过执行简单查询检查 Neo4j 连接是否正常。
        
        返回:
            bool: 连接正常返回 True，否则返回 False
        
        异常:
            不抛出异常，所有异常均捕获并返回 False。
        """
        try:
            with cls.get_session() as session:
                result = cast(Any, session.run("RETURN 1 as health_check"))
                record = result.single()
                # 检查 record 不为 None 且包含正确的值
                if record is None:
                    return False
                # 使用 cast 明确类型以通过类型检查
                record_dict = cast(Any, record)
                health_value = record_dict.get('health_check') if hasattr(record_dict, 'get') else None
                return health_value == 1
        except Exception:
            return False

