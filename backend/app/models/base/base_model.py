"""
基础模型类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from config.database import DatabaseConfig

class BaseModel(ABC):
    """数据库模型基类"""

    def __init__(self):
        self.config = DatabaseConfig()
        self.connection = None
        self._connected = False

    @abstractmethod
    def connect(self):
        """建立数据库连接"""
        pass

    @abstractmethod
    def disconnect(self):
        """断开数据库连接"""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        pass

    @abstractmethod
    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """执行非查询操作（INSERT, UPDATE, DELETE）"""
        pass

    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()

    def _validate_connection(self):
        """验证连接"""
        if not self.is_connected():
            raise ConnectionError("Database connection not established")

    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 执行一个简单的查询来检查连接
            result = self.execute_query("SELECT 1 as health_check")
            return len(result) > 0
        except Exception:
            return False

