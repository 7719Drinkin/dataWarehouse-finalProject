"""Hive 单库查询 Controller

为什么需要这个文件？
- 与 opengauss_query_controller.py 类似，本文件提供 Hive 专用的单库查询路由：/api/query/hive/...
- 目的：让前端选择 Hive 时，能真正只请求 Hive，而不是请求三库聚合。

实现方式：
- 参数解析/校验逻辑与聚合 controller（query_controller.py）保持一致。
- 调用 QueryAggregator.execute_on_one('hive', method_name, **params) 执行单库查询。

返回结构约定（单库统一格式）：
{
  "success": true,
  "query_type": "...",
  "parameters": { ... },
  "database": "hive",
  "result": {
    "data": [...],
    "execution_time": 12.3,
    "success": true,
    "error": null
  }
}
"""

from flask import Blueprint, request, jsonify

from app.services.query.query_aggregator import QueryAggregator

hive_query_bp = Blueprint('hive_query', __name__)
query_service = QueryAggregator()


def _get_str(name: str) -> str | None:
    v = request.args.get(name)
    if v is None:
        return None
    v = v.strip()
    return v or None


def _get_int(name: str) -> int | None:
    v = _get_str(name)
    if v is None:
        return None
    return int(v)


def _get_float(name: str) -> float | None:
    v = _get_str(name)
    if v is None:
        return None
    return float(v)


def _require_at_least_one(params: dict) -> None:
    if not any(v is not None for v in params.values()):
        raise ValueError("至少需要提供一个查询参数")


# 1) 按时间查询电影：year/quarter/month/week 可选但至少一个
@hive_query_bp.route('/movies-by-time', methods=['GET'])
def movies_by_time():
    try:
        year = _get_int('year')
        quarter = _get_int('quarter')
        month = _get_int('month')
        week = _get_int('week')

        params = {
            'year': year,
            'quarter': quarter,
            'month': month,
            'week': week,
        }
        _require_at_least_one(params)

        result = query_service.execute_on_one(
            'hive',
            'get_movies_by_time',
            year=year,
            quarter=quarter,
            month=month,
            week=week,
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_time',
            'parameters': params,
            'database': 'hive',
            'result': result,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_time',
            'database': 'hive',
            'error': str(e),
        }), 400


# 2) 按人员查询电影：director/actor/starring 可选但至少一个
@hive_query_bp.route('/movies-by-person', methods=['GET'])
def movies_by_person():
    try:
        director = _get_str('director')
        actor = _get_str('actor')
        starring = _get_str('starring')

        params = {
            'director': director,
            'actor': actor,
            'starring': starring,
        }
        _require_at_least_one(params)

        result = query_service.execute_on_one(
            'hive',
            'get_movies_by_person',
            director=director,
            actor=actor,
            starring=starring,
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_person',
            'parameters': params,
            'database': 'hive',
            'result': result,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_person',
            'database': 'hive',
            'error': str(e),
        }), 400


# 3) 按属性查询电影：title/genre 可选但至少一个
@hive_query_bp.route('/movies-by-property', methods=['GET'])
def movies_by_property():
    try:
        title = _get_str('title')
        genre = _get_str('genre')

        params = {
            'title': title,
            'genre': genre,
        }
        _require_at_least_one(params)

        result = query_service.execute_on_one(
            'hive',
            'get_movies_by_property',
            title=title,
            genre=genre,
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_property',
            'parameters': params,
            'database': 'hive',
            'result': result,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_property',
            'database': 'hive',
            'error': str(e),
        }), 400


# 4) 按高评分查询电影：min_score/min_reviews 可选但至少一个
@hive_query_bp.route('/high-rated-movies', methods=['GET'])
def high_rated_movies():
    try:
        min_score = _get_float('min_score')
        min_reviews = _get_int('min_reviews')

        params = {
            'min_score': min_score,
            'min_reviews': min_reviews,
        }
        _require_at_least_one(params)

        result = query_service.execute_on_one(
            'hive',
            'get_high_rated_movies_dynamic',
            min_score=min_score,
            min_reviews=min_reviews,
        )

        return jsonify({
            'success': True,
            'query_type': 'high_rated_movies',
            'parameters': params,
            'database': 'hive',
            'result': result,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'high_rated_movies',
            'database': 'hive',
            'error': str(e),
        }), 400


# 5) 演员-演员合作关系：min_collaborations 必填
@hive_query_bp.route('/actor-collaborations', methods=['GET'])
def actor_actor_collaborations():
    try:
        min_collaborations = _get_int('min_collaborations')
        if min_collaborations is None:
            raise ValueError('min_collaborations 参数必填')

        limit = _get_int('limit')
        if limit is None:
            limit = 20

        params = {
            'min_collaborations': min_collaborations,
            'limit': limit,
        }

        result = query_service.execute_on_one(
            'hive',
            'get_actor_actor_collaborations',
            min_collaborations=min_collaborations,
            limit=limit,
        )

        return jsonify({
            'success': True,
            'query_type': 'actor_actor_collaborations',
            'parameters': params,
            'database': 'hive',
            'result': result,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'actor_actor_collaborations',
            'database': 'hive',
            'error': str(e),
        }), 400


# 6) 导演-演员合作关系：仅 director 必填（按你的最终需求，不传 min_collaborations）
@hive_query_bp.route('/director-actor-collaborations', methods=['GET'])
def director_actor_collaborations():
    try:
        director = _get_str('director')
        if not director:
            raise ValueError('director 参数必填')

        limit = _get_int('limit')
        if limit is None:
            limit = 20

        params = {
            'director': director,
            'limit': limit,
        }

        result = query_service.execute_on_one(
            'hive',
            'get_director_actor_collaborations_by_director',
            director=director,
            limit=limit,
        )

        return jsonify({
            'success': True,
            'query_type': 'director_actor_collaborations',
            'parameters': params,
            'database': 'hive',
            'result': result,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'director_actor_collaborations',
            'database': 'hive',
            'error': str(e),
        }), 400


# 7) 组合查询电影：year/director/actor/min_score/genre 至少一个
@hive_query_bp.route('/movies-by-combined-query', methods=['GET'])
def movies_by_combined_query():
    try:
        year = _get_int('year')
        director = _get_str('director')
        actor = _get_str('actor')
        min_score = _get_float('min_score')
        genre = _get_str('genre')

        params = {
            'year': year,
            'director': director,
            'actor': actor,
            'min_score': min_score,
            'genre': genre,
        }
        _require_at_least_one(params)

        result = query_service.execute_on_one(
            'hive',
            'get_movies_by_multi_condition',
            year=year,
            director=director,
            actor=actor,
            min_score=min_score,
            genre=genre,
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_combined_query',
            'parameters': params,
            'database': 'hive',
            'result': result,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_combined_query',
            'database': 'hive',
            'error': str(e),
        }), 400

