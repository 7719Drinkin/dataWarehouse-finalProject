"""
查询API控制器
"""
from flask import Blueprint, request, jsonify
from app.services.query_service import QueryService
from app.services.performance_service import PerformanceService
from app.services.visualization_service import VisualizationService
from app.services.governance_service import GovernanceService

query_bp = Blueprint('query', __name__)

# 初始化服务
query_service = QueryService()
performance_service = PerformanceService()
visualization_service = VisualizationService()
governance_service = GovernanceService()

@query_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Movie Data Warehouse API',
        'version': '1.0.0'
    })

@query_bp.route('/movies-by-year', methods=['GET'])
def get_movies_by_year():
    """按年份查询电影统计"""
    try:
        year = int(request.args.get('year', 2020))

        # 并发查询三种数据库
        results = performance_service.compare_performance({
            'opengauss': lambda: query_service.query_opengauss_movies_by_year(year),
            'hive': lambda: query_service.query_hive_movies_by_year(year),
            'neo4j': lambda: query_service.query_neo4j_movies_by_year(year)
        })

        # 生成可视化数据
        chart_data = visualization_service.format_performance_chart_data(results)

        return jsonify({
            'success': True,
            'query_type': 'movies_by_year',
            'parameters': {'year': year},
            'results': results,
            'charts': {
                'performance_comparison': chart_data,
                'time_series': visualization_service.format_time_series_chart(
                    results['results'].get('opengauss', {}).get('result', [])
                )
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'query_type': 'movies_by_year'
        }), 400

@query_bp.route('/movies-by-director', methods=['GET'])
def get_movies_by_director():
    """按导演查询电影"""
    try:
        director = request.args.get('director', '').strip()
        if not director:
            return jsonify({'success': False, 'error': 'Director parameter is required'}), 400

        results = performance_service.compare_performance({
            'opengauss': lambda: query_service.query_opengauss_movies_by_director(director),
            'hive': lambda: query_service.query_hive_movies_by_director(director),
            'neo4j': lambda: query_service.query_neo4j_movies_by_director(director)
        })

        chart_data = visualization_service.format_performance_chart_data(results)

        return jsonify({
            'success': True,
            'query_type': 'movies_by_director',
            'parameters': {'director': director},
            'results': results,
            'charts': {'performance_comparison': chart_data}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'query_type': 'movies_by_director'
        }), 400

@query_bp.route('/movies-by-actor', methods=['GET'])
def get_movies_by_actor():
    """按演员查询电影"""
    try:
        actor = request.args.get('actor', '').strip()
        role_type = request.args.get('role_type', 'starring')  # starring or participated

        if not actor:
            return jsonify({'success': False, 'error': 'Actor parameter is required'}), 400

        if role_type == 'starring':
            query_funcs = {
                'opengauss': lambda: query_service.query_opengauss_movies_by_actor_starring(actor),
                'hive': lambda: query_service.query_hive_movies_by_actor_starring(actor),
                'neo4j': lambda: query_service.query_neo4j_movies_by_actor_starring(actor)
            }
        else:
            query_funcs = {
                'opengauss': lambda: query_service.query_opengauss_movies_by_actor_participated(actor),
                'hive': lambda: query_service.query_hive_movies_by_actor_participated(actor),
                'neo4j': lambda: query_service.query_neo4j_movies_by_actor_participated(actor)
            }

        results = performance_service.compare_performance(query_funcs)
        chart_data = visualization_service.format_performance_chart_data(results)

        return jsonify({
            'success': True,
            'query_type': f'movies_by_actor_{role_type}',
            'parameters': {'actor': actor, 'role_type': role_type},
            'results': results,
            'charts': {'performance_comparison': chart_data}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@query_bp.route('/movies-by-genre', methods=['GET'])
def get_movies_by_genre():
    """按电影类型查询统计"""
    try:
        genre = request.args.get('genre', '').strip()
        if not genre:
            return jsonify({'success': False, 'error': 'Genre parameter is required'}), 400

        results = performance_service.compare_performance({
            'opengauss': lambda: query_service.query_opengauss_movies_by_genre(genre),
            'hive': lambda: query_service.query_hive_movies_by_genre(genre),
            'neo4j': lambda: query_service.query_neo4j_movies_by_genre(genre)
        })

        chart_data = visualization_service.format_performance_chart_data(results)

        return jsonify({
            'success': True,
            'query_type': 'movies_by_genre',
            'parameters': {'genre': genre},
            'results': results,
            'charts': {'performance_comparison': chart_data}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@query_bp.route('/high-rated-movies', methods=['GET'])
def get_high_rated_movies():
    """查询高评分电影"""
    try:
        min_score = float(request.args.get('min_score', 4.0))
        min_reviews = int(request.args.get('min_reviews', 10))

        results = performance_service.compare_performance({
            'opengauss': lambda: query_service.query_opengauss_high_rated_movies(min_score, min_reviews),
            'hive': lambda: query_service.query_hive_high_rated_movies(min_score, min_reviews),
            'neo4j': lambda: query_service.query_neo4j_high_rated_movies(min_score, min_reviews)
        })

        chart_data = visualization_service.format_performance_chart_data(results)
        rating_chart = visualization_service.format_rating_distribution_chart(
            results['results'].get('opengauss', {}).get('result', [])
        )

        return jsonify({
            'success': True,
            'query_type': 'high_rated_movies',
            'parameters': {'min_score': min_score, 'min_reviews': min_reviews},
            'results': results,
            'charts': {
                'performance_comparison': chart_data,
                'rating_distribution': rating_chart
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@query_bp.route('/actor-collaborations', methods=['GET'])
def get_actor_collaborations():
    """查询演员合作关系"""
    try:
        min_collaborations = int(request.args.get('min_collaborations', 2))
        limit = int(request.args.get('limit', 20))

        results = performance_service.compare_performance({
            'opengauss': lambda: query_service.query_opengauss_actor_collaborations(min_collaborations, limit),
            'hive': lambda: query_service.query_hive_actor_collaborations(min_collaborations, limit),
            'neo4j': lambda: query_service.query_neo4j_actor_collaborations(min_collaborations, limit)
        })

        chart_data = visualization_service.format_performance_chart_data(results)
        network_data = visualization_service.format_collaboration_network_data(
            results['results'].get('neo4j', {}).get('result', [])
        )

        return jsonify({
            'success': True,
            'query_type': 'actor_collaborations',
            'parameters': {'min_collaborations': min_collaborations, 'limit': limit},
            'results': results,
            'charts': {
                'performance_comparison': chart_data,
                'collaboration_network': network_data
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@query_bp.route('/director-actor-collaborations', methods=['GET'])
def get_director_actor_collaborations():
    """查询导演演员合作关系"""
    try:
        director = request.args.get('director', '').strip()
        min_collaborations = int(request.args.get('min_collaborations', 1))
        limit = int(request.args.get('limit', 10))

        if not director:
            return jsonify({'success': False, 'error': 'Director parameter is required'}), 400

        results = performance_service.compare_performance({
            'opengauss': lambda: query_service.query_opengauss_director_actor_collaborations(director, min_collaborations, limit),
            'hive': lambda: query_service.query_hive_director_actor_collaborations(director, min_collaborations, limit),
            'neo4j': lambda: query_service.query_neo4j_director_actor_collaborations(director, min_collaborations, limit)
        })

        chart_data = visualization_service.format_performance_chart_data(results)

        return jsonify({
            'success': True,
            'query_type': 'director_actor_collaborations',
            'parameters': {'director': director, 'min_collaborations': min_collaborations, 'limit': limit},
            'results': results,
            'charts': {'performance_comparison': chart_data}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@query_bp.route('/popular-actor-combinations', methods=['GET'])
def get_popular_actor_combinations():
    """查询热门演员组合（仅Neo4j）"""
    try:
        genre = request.args.get('genre', 'Action').strip()

        # 只有Neo4j支持这个查询
        result = query_service.query_neo4j_popular_actor_combinations(genre)

        return jsonify({
            'success': True,
            'query_type': 'popular_actor_combinations',
            'parameters': {'genre': genre},
            'database': 'neo4j',
            'result': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@query_bp.route('/performance-report', methods=['GET'])
def get_performance_report():
    """获取性能报告"""
    try:
        # 这里可以实现获取历史性能数据的逻辑
        # 目前返回一个示例报告
        sample_results = {
            'results': {
                'opengauss': {'execution_time': 0.5, 'success': True},
                'hive': {'execution_time': 1.2, 'success': True},
                'neo4j': {'execution_time': 0.3, 'success': True}
            },
            'performance_stats': {
                'fastest_database': 'neo4j',
                'performance_ratio': 4.0,
                'average_execution_time': 0.67
            }
        }

        report = performance_service.generate_performance_report(sample_results)

        return jsonify({
            'success': True,
            'report': report
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

