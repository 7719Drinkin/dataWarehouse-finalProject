"""
Hive数据库连接管理
"""
from pyhive import hive
from contextlib import contextmanager
from config.database import DatabaseConfig

class HiveConnection:
    """Hive连接管理器"""

    _connection = None

    @classmethod
    @contextmanager
    def get_connection(cls):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            if cls._connection is None:
                config = DatabaseConfig()
                conn_params = config.get_hive_connection_params()
                cls._connection = hive.Connection(**conn_params)

            conn = cls._connection
            yield conn
        except Exception as e:
            # 如果连接失败，尝试重新连接
            if cls._connection:
                cls._connection.close()
                cls._connection = None
            raise e
        finally:
            # Hive连接通常保持打开状态，不在这里关闭
            pass

    @classmethod
    def close_connection(cls):
        """关闭连接"""
        if cls._connection:
            cls._connection.close()
            cls._connection = None

    @classmethod
    def health_check(cls) -> bool:
        """健康检查"""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception:
            return False

