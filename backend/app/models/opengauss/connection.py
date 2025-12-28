"""
OpenGauss数据库连接管理
"""
from typing import Any, Optional
import psycopg2  # type: ignore
from psycopg2 import pool  # type: ignore
from psycopg2.extras import RealDictCursor  # type: ignore
from contextlib import contextmanager
from config.database import DatabaseConfig

class OpenGaussConnection:
    """OpenGauss连接管理器
    
    提供 OpenGauss 数据库连接池管理，支持上下文管理器模式。
    """

    _pool: Any = None
    config: Any = DatabaseConfig()

    @classmethod
    def get_pool(cls) -> Any:
        """获取连接池
        
        返回:
            psycopg2 连接池对象
        """
        if cls._pool is None:
            cls._pool = psycopg2.pool.SimpleConnectionPool(  # type: ignore
                cls.config.OPENGAUSS_POOL_MIN_CONN,
                cls.config.OPENGAUSS_POOL_MAX_CONN,
                cls.config.get_opengauss_connection_string(),
                cursor_factory=RealDictCursor
            )
        return cls._pool

    @classmethod
    @contextmanager
    def get_connection(cls):  # type: ignore
        """获取数据库连接的上下文管理器
        
        返回:
            psycopg2 连接对象
        
        用法:
            with OpenGaussConnection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM movies")
                    results = cursor.fetchall()
        """
        conn = None
        try:
            conn = cls.get_pool().getconn()
            yield conn
        finally:
            if conn:
                cls.get_pool().putconn(conn)

    @classmethod
    def close_all_connections(cls) -> None:
        """关闭所有连接
        
        关闭连接池中的所有连接，释放资源。
        """
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None

    @classmethod
    def health_check(cls) -> bool:
        """健康检查
        
        通过执行简单查询检查数据库连接是否正常。
        
        返回:
            bool: 连接正常返回 True，否则返回 False
        
        异常:
            不抛出异常，所有异常均捕获并返回 False。
        """
        try:
            with cls.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception:
            return False

