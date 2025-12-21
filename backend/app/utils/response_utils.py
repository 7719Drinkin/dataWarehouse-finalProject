"""
响应格式化工具
"""
from typing import Any, Dict, Optional
from flask import jsonify
from datetime import datetime

class ResponseUtils:
    """API响应格式化工具"""

    @staticmethod
    def success_response(data: Any = None, message: str = "Success", **kwargs) -> Dict[str, Any]:
        """成功响应"""
        response = {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        }

        if data is not None:
            response['data'] = data

        # 添加额外的字段
        response.update(kwargs)

        return response

    @staticmethod
    def error_response(error: str, error_code: str = "INTERNAL_ERROR", **kwargs) -> Dict[str, Any]:
        """错误响应"""
        response = {
            'success': False,
            'error': error,
            'error_code': error_code,
            'timestamp': datetime.now().isoformat(),
        }

        # 添加额外的字段
        response.update(kwargs)

        return response

    @staticmethod
    def paginated_response(
        data: list,
        page: int,
        per_page: int,
        total: int,
        **kwargs
    ) -> Dict[str, Any]:
        """分页响应"""
        response = ResponseUtils.success_response(
            data=data,
            pagination={
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            },
            **kwargs
        )

        return response

    @staticmethod
    def validation_error_response(errors: Dict[str, Any]) -> Dict[str, Any]:
        """验证错误响应"""
        return ResponseUtils.error_response(
            error="Validation failed",
            error_code="VALIDATION_ERROR",
            validation_errors=errors
        )

    @staticmethod
    def format_query_result(
        query_type: str,
        parameters: Dict[str, Any],
        results: Dict[str, Any],
        charts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """格式化查询结果响应"""
        response = ResponseUtils.success_response(
            query_type=query_type,
            parameters=parameters,
            results=results,
            execution_time=results.get('total_execution_time', 0),
            timestamp=datetime.now().isoformat()
        )

        if charts:
            response['charts'] = charts

        return response

    @staticmethod
    def format_performance_comparison(
        query_type: str,
        results: Dict[str, Any],
        charts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """格式化性能对比响应"""
        stats = results.get('performance_stats', {})

        response = ResponseUtils.success_response(
            query_type=query_type,
            performance_comparison={
                'fastest_database': stats.get('fastest_database'),
                'slowest_database': stats.get('slowest_database'),
                'performance_ratio': stats.get('performance_ratio'),
                'average_time': stats.get('average_execution_time'),
                'success_rate': stats.get('success_rate')
            },
            detailed_results=results.get('results', {}),
            total_execution_time=results.get('total_execution_time', 0)
        )

        if charts:
            response['charts'] = charts

        return response

