"""
性能监控服务
"""
import time
import asyncio
from typing import Dict, Any, Callable, List
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from config.database import DatabaseConfig

class PerformanceService:
    """性能监控和比较服务"""

    def __init__(self):
        self.config = DatabaseConfig()

    @staticmethod
    def measure_execution_time(func: Callable, timeout: int = None) -> Dict[str, Any]:
        """测量函数执行时间"""
        start_time = time.time()
        error = None
        result = None
        success = False

        try:
            if timeout:
                # 使用线程池执行带超时的函数
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func)
                    result = future.result(timeout=timeout)
            else:
                result = func()

            success = True
        except TimeoutError:
            error = f"Query timeout after {timeout} seconds"
        except Exception as e:
            error = str(e)

        execution_time = time.time() - start_time

        return {
            'result': result,
            'execution_time': execution_time,
            'success': success,
            'error': error,
            'timestamp': time.time()
        }

    def compare_performance(self, query_funcs: Dict[str, Callable], timeout: int = None) -> Dict[str, Any]:
        """并发比较多个查询的性能"""
        if timeout is None:
            timeout = self.config.QUERY_TIMEOUT

        results = {}
        total_start_time = time.time()

        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=len(query_funcs)) as executor:
            future_to_db = {
                executor.submit(self.measure_execution_time, func, timeout): db_name
                for db_name, func in query_funcs.items()
            }

            for future in as_completed(future_to_db, timeout=timeout + 5):  # 额外5秒容忍时间
                db_name = future_to_db[future]
                try:
                    results[db_name] = future.result()
                except TimeoutError:
                    results[db_name] = {
                        'result': None,
                        'execution_time': timeout,
                        'success': False,
                        'error': f"Overall timeout after {timeout + 5} seconds",
                        'timestamp': time.time()
                    }
                except Exception as e:
                    results[db_name] = {
                        'result': None,
                        'execution_time': 0,
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    }

        total_execution_time = time.time() - total_start_time

        # 计算性能统计
        performance_stats = self._calculate_performance_stats(results)

        return {
            'results': results,
            'total_execution_time': total_execution_time,
            'performance_stats': performance_stats,
            'comparison_timestamp': time.time()
        }

    def _calculate_performance_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """计算性能统计"""
        successful_queries = {
            db: data for db, data in results.items()
            if data['success'] and data['execution_time'] > 0
        }

        if not successful_queries:
            return {
                'fastest_database': None,
                'slowest_database': None,
                'performance_ratio': None,
                'average_execution_time': 0,
                'success_rate': 0
            }

        # 找到最快和最慢的数据库
        sorted_by_time = sorted(successful_queries.items(), key=lambda x: x[1]['execution_time'])

        fastest_db, fastest_data = sorted_by_time[0]
        slowest_db, slowest_data = sorted_by_time[-1]

        # 计算性能倍数
        performance_ratio = slowest_data['execution_time'] / fastest_data['execution_time'] if fastest_data['execution_time'] > 0 else float('inf')

        # 计算平均执行时间
        avg_time = sum(data['execution_time'] for data in successful_queries.values()) / len(successful_queries)

        # 成功率
        success_rate = len(successful_queries) / len(results)

        return {
            'fastest_database': fastest_db,
            'fastest_time': fastest_data['execution_time'],
            'slowest_database': slowest_db,
            'slowest_time': slowest_data['execution_time'],
            'performance_ratio': round(performance_ratio, 2),
            'average_execution_time': round(avg_time, 4),
            'success_rate': round(success_rate, 2),
            'successful_queries': len(successful_queries),
            'total_queries': len(results)
        }

    def generate_performance_report(self, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成性能报告"""
        results = comparison_results['results']
        stats = comparison_results['performance_stats']

        report = {
            'summary': {
                'total_execution_time': round(comparison_results['total_execution_time'], 4),
                'query_count': len(results),
                'successful_queries': stats['successful_queries'],
                'success_rate': f"{stats['success_rate'] * 100:.1f}%"
            },
            'performance_analysis': {
                'fastest_database': stats['fastest_database'],
                'fastest_time': f"{stats['fastest_time']:.4f}s",
                'slowest_database': stats['slowest_database'],
                'slowest_time': f"{stats['slowest_time']:.4f}s",
                'performance_ratio': f"{stats['performance_ratio']:.2f}x",
                'average_time': f"{stats['average_execution_time']:.4f}s"
            },
            'detailed_results': {}
        }

        # 详细结果
        for db_name, data in results.items():
            report['detailed_results'][db_name] = {
                'execution_time': f"{data['execution_time']:.4f}s",
                'success': data['success'],
                'result_count': len(data['result']) if data['result'] else 0,
                'error': data['error']
            }

        return report

    def benchmark_query(self, func: Callable, iterations: int = 5) -> Dict[str, Any]:
        """对单个查询进行基准测试"""
        execution_times = []

        for i in range(iterations):
            result = self.measure_execution_time(func)
            if result['success']:
                execution_times.append(result['execution_time'])

        if not execution_times:
            return {
                'success': False,
                'error': 'All iterations failed',
                'iterations': iterations,
                'successful_iterations': 0
            }

        return {
            'success': True,
            'iterations': iterations,
            'successful_iterations': len(execution_times),
            'min_time': min(execution_times),
            'max_time': max(execution_times),
            'avg_time': sum(execution_times) / len(execution_times),
            'median_time': sorted(execution_times)[len(execution_times) // 2],
            'std_dev': self._calculate_std_dev(execution_times)
        }

    def _calculate_std_dev(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) <= 1:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

