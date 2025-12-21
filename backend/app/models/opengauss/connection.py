"""
OpenGauss数据库连接管理
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config.database import DatabaseConfig

class OpenGaussConnection:
    """OpenGauss连接管理器"""

    _pool = None

    @classmethod
    def get_pool(cls):
        """获取连接池"""
        if cls._pool is None:
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                cls.config.OPENGAUSS_POOL_MIN_CONN,
                cls.config.OPENGAUSS_POOL_MAX_CONN,
                cls.config.get_opengauss_connection_string(),
                cursor_factory=RealDictCursor
            )
        return cls._pool

    @classmethod
    @contextmanager
    def get_connection(cls):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = cls.get_pool().getconn()
            yield conn
        finally:
            if conn:
                cls.get_pool().putconn(conn)

    @classmethod
    def close_all_connections(cls):
        """关闭所有连接"""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None

    @classmethod
    def health_check(cls) -> bool:
        """健康检查"""
        try:
            with cls.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception:
            return False

