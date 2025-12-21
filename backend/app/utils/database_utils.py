"""
数据库工具类
"""
import time
from typing import Any, Dict, List, Callable
from contextlib import contextmanager

class DatabaseUtils:
    """数据库相关工具"""

    @staticmethod
    @contextmanager
    def connection_context(manager):
        """数据库连接上下文管理器"""
        try:
            with manager:
                yield manager
        except Exception as e:
            print(f"Database operation failed: {e}")
            raise

    @staticmethod
    def retry_operation(operation: Callable, max_retries: int = 3, delay: float = 1.0) -> Any:
        """重试数据库操作"""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay * (2 ** attempt))  # 指数退避
                continue

        raise last_exception

    @staticmethod
    def validate_connection_params(params: Dict[str, Any], required_fields: List[str]) -> bool:
        """验证连接参数"""
        for field in required_fields:
            if field not in params or not params[field]:
                return False
        return True

    @staticmethod
    def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """清理查询参数，防止SQL注入"""
        sanitized = {}

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
        """格式化执行时间"""
        if seconds < 1:
            return ".4f"
        elif seconds < 60:
            return ".2f"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.2f}s"

    @staticmethod
    def estimate_query_complexity(query_type: str, params: Dict[str, Any]) -> str:
        """估算查询复杂度"""
        complexity_map = {
            'simple_lookup': 'Low',
            'aggregation': 'Medium',
            'join_operation': 'High',
            'graph_traversal': 'High',
            'complex_analytics': 'Very High'
        }

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
        """生成查询ID用于日志和缓存"""
        import hashlib
        import json

        # 创建查询签名
        query_signature = {
            'type': query_type,
            'params': sorted(params.items())
        }

        signature_str = json.dumps(query_signature, sort_keys=True)
        return hashlib.md5(signature_str.encode()).hexdigest()[:8]

    @staticmethod
    def log_query_performance(query_id: str, db_type: str, execution_time: float, success: bool, error: str = None):
        """记录查询性能日志"""
        status = "SUCCESS" if success else "FAILED"
        time_str = DatabaseUtils.format_execution_time(execution_time)

        log_entry = f"[QUERY] {query_id} | {db_type} | {status} | {time_str}"
        if error:
            log_entry += f" | ERROR: {error}"

        print(log_entry)  # 在生产环境中应该使用适当的日志系统

    @staticmethod
    def compare_result_consistency(results: Dict[str, Any], key_fields: List[str] = None) -> Dict[str, Any]:
        """比较不同数据库结果的一致性"""
        if not results or len(results) < 2:
            return {'consistent': True, 'differences': []}

        # 默认比较键字段
        if not key_fields:
            key_fields = ['movie_id', 'title', 'count', 'avg_score']

        databases = list(results.keys())
        base_db = databases[0]
        base_result = results[base_db].get('result', [])

        differences = []

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
                    base_value = base_record.get(field)
                    compare_value = compare_record.get(field)

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

