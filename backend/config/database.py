"""
数据库配置
"""
import os
from typing import Tuple, TypedDict

class HiveConnectionParams(TypedDict):
    """Hive连接参数类型"""
    host: str
    port: int
    username: str
    database: str

class Neo4jConnectionParams(TypedDict):
    """Neo4j连接参数类型"""
    uri: str
    auth: Tuple[str, str]

class DatabaseConfig:
    """数据库配置类"""

    # OpenGauss配置
    OPENGAUSS_HOST = os.getenv('OPENGAUSS_HOST', '139.196.151.22')
    OPENGAUSS_PORT = int(os.getenv('OPENGAUSS_PORT', '5432'))
    OPENGAUSS_USER = os.getenv('OPENGAUSS_USER', 'gaussdb')
    OPENGAUSS_PASSWORD = os.getenv('OPENGAUSS_PASSWORD', 'GaussDB@2025')
    OPENGAUSS_DATABASE = os.getenv('OPENGAUSS_DATABASE', 'movie_dw')

    # 连接池配置
    OPENGAUSS_POOL_MIN_CONN = int(os.getenv('OPENGAUSS_POOL_MIN_CONN', '1'))
    OPENGAUSS_POOL_MAX_CONN = int(os.getenv('OPENGAUSS_POOL_MAX_CONN', '10'))

    # Hive配置
    HIVE_HOST = os.getenv('HIVE_HOST', '139.196.151.22')
    HIVE_PORT = int(os.getenv('HIVE_PORT', '10000'))
    HIVE_USER = os.getenv('HIVE_USER', 'hive')
    HIVE_DATABASE = os.getenv('HIVE_DATABASE', 'default')

    # Neo4j配置
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://139.196.151.22:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'neo4j_password')

    # 连接超时配置
    CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '30'))
    QUERY_TIMEOUT = int(os.getenv('QUERY_TIMEOUT', '300'))

    @classmethod
    def get_opengauss_connection_string(cls) -> str:
        """获取OpenGauss连接字符串"""
        return f"host={cls.OPENGAUSS_HOST} port={cls.OPENGAUSS_PORT} user={cls.OPENGAUSS_USER} password={cls.OPENGAUSS_PASSWORD} dbname={cls.OPENGAUSS_DATABASE}"

    @classmethod
    def get_hive_connection_params(cls) -> HiveConnectionParams:
        """获取Hive连接参数"""
        return {
            'host': cls.HIVE_HOST,
            'port': cls.HIVE_PORT,
            'username': cls.HIVE_USER,
            'database': cls.HIVE_DATABASE
        }

    @classmethod
    def get_neo4j_connection_params(cls) -> Neo4jConnectionParams:
        """获取Neo4j连接参数"""
        return {
            'uri': cls.NEO4J_URI,
            'auth': (cls.NEO4J_USER, cls.NEO4J_PASSWORD)
        }



