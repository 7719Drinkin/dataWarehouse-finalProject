"""
数据库工具类
"""
import time
import logging
from typing import Any, Dict, List, Callable, Optional
from logger_setup import setup_query_logger
from contextlib import contextmanager

from pathlib import Path

class DatabaseUtils:
    """数据库相关工具

    提供数据库连接管理、重试机制、参数验证等实用工具。
    """
    logger = setup_query_logger()

    @staticmethod
    @contextmanager
    def connection_context(manager: Any):
        """数据库连接上下文管理器
        
        参数:
            manager: 连接管理器对象
        
        使用方式:
            with DatabaseUtils.connection_context(connection_manager) as conn:
                # 执行数据库操作
        """
        try:
            with manager:
                yield manager
        except Exception as e:
            print(f"Database operation failed: {e}")
            raise

    @staticmethod
    def retry_operation(operation: Callable, max_retries: int = 3, delay: float = 1.0) -> Any:
        """重试数据库操作
        
        参数:
            operation (Callable): 要执行的操作函数
            max_retries (int): 最大重试次数，默认 3
            delay (float): 重试间隔（秒），默认 1.0，支持指数退避
        
        返回:
            Any: 操作的返回值
        
        异常:
            Exception: 所有重试都失败时抛出最后一个异常
        
        使用方式:
            result = DatabaseUtils.retry_operation(lambda: execute_query(), max_retries=3)
        """
        last_exception: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay * (2 ** attempt))  # 指数退避
                continue

        # last_exception 在循环中至少被赋值一次，所以不会为 None
        if last_exception is not None:
            raise last_exception
        else:
            raise RuntimeError("Operation failed after retries")

    @staticmethod
    def validate_connection_params(params: Dict[str, Any], required_fields: List[str]) -> bool:
        """验证连接参数
        
        参数:
            params (Dict[str, Any]): 连接参数字典
            required_fields (List[str]): 必需的字段列表
        
        返回:
            bool: 所有必需字段都存在且非空时返回 True
        """
        for field in required_fields:
            if field not in params or not params[field]:
                return False
        return True

    @staticmethod
    def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """清理查询参数，防止SQL注入
        
        参数:
            params (Dict[str, Any]): 原始查询参数
        
        返回:
            Dict[str, Any]: 清理后的参数字典
        
        注意:
            本方法仅进行基本清理。在实际应用中，应该使用参数化查询。
        """
        sanitized: Dict[str, Any] = {}

        for key, value in params.items():
            if isinstance(value, str):
                # 移除潜在的危险字符，这里是基本清理
                # 在实际应用中，应该使用参数化查询
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value

        return sanitized

    @staticmethod
    def format_execution_time(seconds: float) -> str:
        """格式化执行时间
        
        参数:
            seconds (float): 执行时间（秒）
        
        返回:
            str: 格式化的时间字符串
        """
        if seconds < 1:
            return f"{seconds:.4f}s"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.2f}s"

    @staticmethod
    def estimate_query_complexity(query_type: str, params: Dict[str, Any]) -> str:
        """估算查询复杂度
        
        参数:
            query_type (str): 查询类型
            params (Dict[str, Any]): 查询参数
        
        返回:
            str: 复杂度等级（Low, Medium, High, Very High）
        """
        # 基于查询类型和参数估算复杂度
        if 'limit' in params and params.get('limit', 0) < 10:
            return 'Low'
        elif any(keyword in query_type.lower() for keyword in ['aggregation', 'count', 'avg']):
            return 'Medium'
        elif 'collaboration' in query_type.lower() or 'relationship' in query_type.lower():
            return 'High'
        else:
            return 'Medium'

    @staticmethod
    def generate_query_id(query_type: str, params: Dict[str, Any]) -> str:
        """生成查询ID用于日志和缓存
        
        参数:
            query_type (str): 查询类型
            params (Dict[str, Any]): 查询参数
        
        返回:
            str: 查询的唯一 ID（8 位十六进制哈希）
        """
        import hashlib
        import json

        # 创建查询签名
        query_signature: Dict[str, Any] = {
            'type': query_type,
            'params': sorted(params.items())
        }

        signature_str = json.dumps(query_signature, sort_keys=True)
        return hashlib.md5(signature_str.encode()).hexdigest()[:8]

    @staticmethod
    def log_query_performance(
        query_id: str, 
        db_type: str, 
        execution_time: float, 
        success: bool, 
        error: Optional[str] = None
    ) -> None:
        """记录查询性能日志
        
        参数:
            query_id (str): 查询 ID
            db_type (str): 数据库类型
            execution_time (float): 执行时间（秒）
            success (bool): 是否成功
            error (Optional[str]): 错误信息，可选
        
        注意:
            在生产环境中应该使用适当的日志系统而不是 print()
        """
        status = "SUCCESS" if success else "FAILED"
        time_str = DatabaseUtils.format_execution_time(execution_time)
        log_entry = f"[QUERY] {query_id} | {db_type} | {status} | {time_str}"
        if error:
            log_entry += f" | ERROR: {error}"
        logger.info(log_entry)

    @staticmethod
    def compare_result_consistency(
        results: Dict[str, Any], 
        key_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """比较不同数据库结果的一致性
        
        参数:
            results (Dict[str, Any]): 各数据库的查询结果
            key_fields (Optional[List[str]]): 用于比较的关键字段列表，可选
        
        返回:
            Dict[str, Any]: 包含一致性比较结果的字典
        
        返回字典字段:
            - consistent: 结果是否一致
            - differences: 差异列表
            - compared_databases: 比较的数据库列表
        """
        if not results or len(results) < 2:
            return {'consistent': True, 'differences': [], 'compared_databases': []}

        # 默认比较键字段
        if key_fields is None:
            key_fields = ['movie_id', 'title', 'count', 'avg_score']

        databases = list(results.keys())
        base_db = databases[0]
        base_result = results[base_db].get('result', [])

        differences: List[Dict[str, Any]] = []

        for db in databases[1:]:
            db_result = results[db].get('result', [])

            # 比较结果数量
            if len(base_result) != len(db_result):
                differences.append({
                    'type': 'count_mismatch',
                    'databases': [base_db, db],
                    'base_count': len(base_result),
                    'compare_count': len(db_result)
                })

            # 比较关键字段
            min_length = min(len(base_result), len(db_result))
            for i in range(min_length):
                base_record = base_result[i]
                compare_record = db_result[i]

                for field in key_fields:
                    base_value = base_record.get(field) if isinstance(base_record, dict) else None
                    compare_value = compare_record.get(field) if isinstance(compare_record, dict) else None

                    if base_value != compare_value:
                        differences.append({
                            'type': 'field_mismatch',
                            'databases': [base_db, db],
                            'record_index': i,
                            'field': field,
                            'base_value': base_value,
                            'compare_value': compare_value
                        })

        return {
            'consistent': len(differences) == 0,
            'differences': differences,
            'compared_databases': databases
        }

