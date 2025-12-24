"""
基础模型类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union, Optional, Type
from types import TracebackType

from config.database import DatabaseConfig

# 查询参数类型
QueryParams = Union[Tuple[Any, ...], Dict[str, Any], None]

class BaseModel(ABC):
    """数据库模型基类
    
    提供数据库操作的统一接口，支持多种数据库（PostgreSQL/OpenGauss、Hive、Neo4j等）。
    子类需要实现具体的连接、断开和查询操作。
    
    属性:
        config (DatabaseConfig): 数据库配置对象
        connection: 数据库连接对象
        _connected (bool): 连接状态标记
    """

    def __init__(self):
        """初始化数据库模型
        
        初始化配置对象、连接对象和连接状态标记。
        """
        self.config = DatabaseConfig()
        self.connection = None
        self._connected = False

    @abstractmethod
    def connect(self):
        """建立数据库连接
        
        子类需要实现此方法以建立与特定数据库的连接，
        并在成功连接后设置 _connected 为 True。
        
        异常:
            Exception: 连接失败时抛出异常
        """
        pass

    @abstractmethod
    def disconnect(self):
        """断开数据库连接
        
        子类需要实现此方法以关闭数据库连接，
        并设置 _connected 为 False。
        
        异常:
            Exception: 断开失败时抛出异常
        """
        pass

    @abstractmethod
    def execute_query(self, query: str, params: QueryParams = None) -> List[Dict[str, Any]]:
        """执行查询操作
        
        执行 SELECT 等查询语句，返回结果集。
        
        参数:
            query (str): SQL 查询语句
            params (QueryParams, 可选): 查询参数，支持三种形式：
                - None: 无参数的简单查询
                - Tuple[Any, ...]: 位置参数（如 PostgreSQL 风格）
                - Dict[str, Any]: 命名参数（如 Hive 风格）
                默认为 None。
        
        返回:
            List[Dict[str, Any]]: 查询结果列表，每个元素是一条记录的字典表示
        
        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 查询执行失败时抛出
        """
        pass

    @abstractmethod
    def execute_non_query(self, query: str, params: QueryParams = None) -> int:
        """执行非查询操作
        
        执行 INSERT、UPDATE、DELETE 等非查询语句。
        
        参数:
            query (str): SQL 语句
            params (QueryParams, 可选): 操作参数，支持三种形式：
                - None: 无参数的操作
                - Tuple[Any, ...]: 位置参数
                - Dict[str, Any]: 命名参数
                默认为 None。
        
        返回:
            int: 受影响的行数
        
        异常:
            ConnectionError: 未建立连接时抛出
            Exception: 操作执行失败时抛出
        """
        pass

    def is_connected(self) -> bool:
        """检查当前连接状态
        
        返回:
            bool: 如果已连接返回 True，否则返回 False
        """
        return self._connected

    def __enter__(self):
        """上下文管理器入口
        
        支持 with 语句，自动建立数据库连接。
        
        返回:
            BaseModel: 返回自身以便在 with 语句中使用
        
        示例:
            with HiveModel() as model:
                result = model.execute_query("SELECT * FROM movies")
        """
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> Optional[bool]:
        """上下文管理器出口
        
        支持 with 语句，自动断开数据库连接。
        
        参数:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        self.disconnect()
        return None

    def _validate_connection(self):
        """验证数据库连接状态
        
        检查是否已建立连接，未连接时抛出异常。
        
        异常:
            ConnectionError: 未建立连接时抛出
        
        用法:
            在执行查询或其他操作前调用此方法，确保连接已建立。
        """
        if not self.is_connected():
            raise ConnectionError("Database connection not established")

    def health_check(self) -> bool:
        """执行健康检查
        
        通过执行简单的查询来检查数据库连接是否正常，
        用于监控数据库可用性。
        
        返回:
            bool: 连接正常返回 True，否则返回 False
        
        异常:
            不抛出异常，所有异常均捕获并返回 False。
        """
        try:
            # 执行一个简单的查询来检查连接
            result = self.execute_query("SELECT 1 as health_check")
            return len(result) > 0
        except Exception:
            return False

