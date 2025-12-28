"""
可视化服务
"""
import json
from typing import Dict, Any, List
from datetime import datetime

class VisualizationService:
    """数据可视化服务"""

    @staticmethod
    def format_performance_chart_data(performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """格式化性能对比图表数据"""
        results = performance_results.get('results', {})

        # 提取执行时间数据
        labels = []
        execution_times = []
        success_status = []

        for db_name, data in results.items():
            labels.append(db_name.upper())
            execution_times.append(round(data.get('execution_time', 0), 4))
            success_status.append(data.get('success', False))

        # 生成图表配置
        chart_data = {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Execution Time (seconds)',
                    'data': execution_times,
                    'backgroundColor': [
                        'rgba(54, 162, 235, 0.6)' if success else 'rgba(255, 99, 132, 0.6)'
                        for success in success_status
                    ],
                    'borderColor': [
                        'rgba(54, 162, 235, 1)' if success else 'rgba(255, 99, 132, 1)'
                        for success in success_status
                    ],
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'top',
                    },
                    'title': {
                        'display': True,
                        'text': 'Database Query Performance Comparison'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Time (seconds)'
                        }
                    }
                }
            }
        }

        return chart_data

    @staticmethod
    def format_time_series_chart(movies_data: List[Dict[str, Any]], time_field: str = 'release_date') -> Dict[str, Any]:
        """格式化时间序列图表数据"""
        # 按年份分组统计
        year_stats = {}
        for movie in movies_data:
            if time_field in movie and movie[time_field]:
                try:
                    if isinstance(movie[time_field], str):
                        year = datetime.fromisoformat(movie[time_field].split('T')[0]).year
                    else:
                        year = movie[time_field].year if hasattr(movie[time_field], 'year') else int(movie[time_field])

                    if year not in year_stats:
                        year_stats[year] = 0
                    year_stats[year] += 1
                except (ValueError, AttributeError):
                    continue

        # 排序年份
        sorted_years = sorted(year_stats.keys())
        movie_counts = [year_stats[year] for year in sorted_years]

        chart_data = {
            'type': 'line',
            'data': {
                'labels': sorted_years,
                'datasets': [{
                    'label': 'Movies Count',
                    'data': movie_counts,
                    'fill': False,
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'tension': 0.1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'top',
                    },
                    'title': {
                        'display': True,
                        'text': 'Movies by Year'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Number of Movies'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Year'
                        }
                    }
                }
            }
        }

        return chart_data

    @staticmethod
    def format_rating_distribution_chart(movies_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """格式化评分分布图表数据"""
        rating_ranges = {
            '0-1': 0,
            '1-2': 0,
            '2-3': 0,
            '3-4': 0,
            '4-5': 0
        }

        for movie in movies_data:
            score = movie.get('avg_score') or movie.get('score')
            if score is not None:
                if score < 1:
                    rating_ranges['0-1'] += 1
                elif score < 2:
                    rating_ranges['1-2'] += 1
                elif score < 3:
                    rating_ranges['2-3'] += 1
                elif score < 4:
                    rating_ranges['3-4'] += 1
                else:
                    rating_ranges['4-5'] += 1

        chart_data = {
            'type': 'doughnut',
            'data': {
                'labels': list(rating_ranges.keys()),
                'datasets': [{
                    'data': list(rating_ranges.values()),
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 205, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ],
                    'borderColor': [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'right',
                    },
                    'title': {
                        'display': True,
                        'text': 'Rating Distribution'
                    }
                }
            }
        }

        return chart_data

    @staticmethod
    def format_genre_pie_chart(movies_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """格式化类型分布饼图数据"""
        genre_counts = {}

        for movie in movies_data:
            genres = movie.get('genres', [])
            if isinstance(genres, str):
                # 如果是字符串，尝试分割
                genres = [g.strip() for g in genres.split(',')]

            for genre in genres:
                if genre:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # 取前10个最常见的类型
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        chart_data = {
            'type': 'pie',
            'data': {
                'labels': [genre for genre, count in sorted_genres],
                'datasets': [{
                    'data': [count for genre, count in sorted_genres],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 205, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(199, 199, 199, 0.6)',
                        'rgba(83, 102, 255, 0.6)',
                        'rgba(255, 99, 255, 0.6)',
                        'rgba(99, 255, 132, 0.6)'
                    ],
                    'borderColor': [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(199, 199, 199, 1)',
                        'rgba(83, 102, 255, 1)',
                        'rgba(255, 99, 255, 1)',
                        'rgba(99, 255, 132, 1)'
                    ],
                    'borderWidth': 1
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {
                        'position': 'right',
                    },
                    'title': {
                        'display': True,
                        'text': 'Genre Distribution (Top 10)'
                    }
                }
            }
        }

        return chart_data

    @staticmethod
    def format_collaboration_network_data(collaboration_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """格式化合作关系网络图数据"""
        nodes = []
        edges = []
        node_ids = {}

        node_counter = 0

        for item in collaboration_data:
            actor1 = item.get('actor1')
            actor2 = item.get('actor2')
            collaborations = item.get('collaborations', 0)

            # 添加节点
            for actor in [actor1, actor2]:
                if actor and actor not in node_ids:
                    node_ids[actor] = node_counter
                    nodes.append({
                        'id': node_counter,
                        'label': actor,
                        'size': collaborations * 10  # 节点大小基于合作次数
                    })
                    node_counter += 1

            # 添加边
            if actor1 in node_ids and actor2 in node_ids:
                edges.append({
                    'from': node_ids[actor1],
                    'to': node_ids[actor2],
                    'value': collaborations,
                    'title': f'Collaborations: {collaborations}'
                })

        network_data = {
            'nodes': nodes,
            'edges': edges
        }

        return network_data

    @staticmethod
    def generate_dashboard_summary(performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成仪表板摘要数据"""
        results = performance_results.get('results', {})
        stats = performance_results.get('performance_stats', {})

        summary = {
            'total_queries': len(results),
            'successful_queries': stats.get('successful_queries', 0),
            'success_rate': f"{stats.get('success_rate', 0) * 100:.1f}%",
            'fastest_database': stats.get('fastest_database', 'N/A'),
            'performance_ratio': f"{stats.get('performance_ratio', 0):.2f}x",
            'average_time': f"{stats.get('average_execution_time', 0):.4f}s",
            'last_updated': datetime.now().isoformat()
        }

        return summary

