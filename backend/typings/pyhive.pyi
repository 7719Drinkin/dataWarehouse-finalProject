"""
PyHive 类型存根包
为 pyhive 库提供完整的类型注解支持
"""
from typing import Any, Dict, List, Optional, Tuple, Union

class Cursor:
    """Hive 游标对象
    
    提供对 Hive 查询结果的访问接口。
    """
    
    description: Optional[List[Tuple[str, Any, Any, Any, Any, Any, Any]]]
    """查询结果的列描述信息"""
    
    rowcount: int
    """最后一次操作影响的行数"""
    
    def execute(self, operation: str, parameters: Optional[Union[List[Any], Tuple[Any, ...], Dict[str, Any]]] = None) -> None:
        """执行 Hive 查询或操作
        
        参数:
            operation: SQL 语句
            parameters: 查询参数
        """
        ...
    
    def fetchall(self) -> List[Tuple[Any, ...]]:
        """获取所有查询结果
        
        返回:
            所有结果行的列表
        """
        ...
    
    def fetchone(self) -> Optional[Tuple[Any, ...]]:
        """获取下一条查询结果
        
        返回:
            单条结果行，如果没有更多结果则返回 None
        """
        ...
    
    def fetchmany(self, size: int) -> List[Tuple[Any, ...]]:
        """获取指定数量的查询结果
        
        参数:
            size: 要获取的行数
        
        返回:
            指定数量的结果行
        """
        ...
    
    def close(self) -> None:
        """关闭游标"""
        ...


class Connection:
    """Hive 连接对象
    
    表示与 Hive 服务器的一个连接。
    """
    
    def cursor(self) -> Cursor:
        """创建一个新的游标
        
        返回:
            Cursor: 新的游标对象
        """
        ...
    
    def close(self) -> None:
        """关闭连接"""
        ...
    
    def __enter__(self) -> "Connection":
        """上下文管理器入口"""
        ...
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """上下文管理器出口"""
        ...


def connect(
    host: str,
    port: int = 10000,
    username: str = "default",
    database: str = "default",
    auth: Optional[str] = None,
    password: Optional[str] = None,
    kerberos_service_name: Optional[str] = None,
    use_https: bool = False,
    **kwargs: Any
) -> Connection:
    """建立 Hive 连接
    
    参数:
        host: Hive 服务器主机名
        port: Hive 服务器端口，默认 10000
        username: 连接用户名
        database: 数据库名称
        auth: 认证方式
        password: 连接密码
        kerberos_service_name: Kerberos 服务名称
        use_https: 是否使用 HTTPS
    
    返回:
        Connection: Hive 连接对象
    """
    ...

