"""
Neo4j数据库连接管理
"""
from neo4j import GraphDatabase
from contextlib import contextmanager
from config.database import DatabaseConfig

class Neo4jConnection:
    """Neo4j连接管理器"""

    _driver = None

    @classmethod
    def get_driver(cls):
        """获取Neo4j驱动"""
        if cls._driver is None:
            config = DatabaseConfig()
            conn_params = config.get_neo4j_connection_params()
            cls._driver = GraphDatabase.driver(**conn_params)
        return cls._driver

    @classmethod
    @contextmanager
    def get_session(cls):
        """获取数据库会话的上下文管理器"""
        session = None
        try:
            session = cls.get_driver().session()
            yield session
        finally:
            if session:
                session.close()

    @classmethod
    def close_driver(cls):
        """关闭驱动"""
        if cls._driver:
            cls._driver.close()
            cls._driver = None

    @classmethod
    def health_check(cls) -> bool:
        """健康检查"""
        try:
            with cls.get_session() as session:
                result = session.run("RETURN 1 as health_check")
                record = result.single()
                return record and record['health_check'] == 1
        except Exception:
            return False

