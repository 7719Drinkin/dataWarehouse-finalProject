"""
查询API控制器

说明：
- 统一返回结构：results 为 AggregatedQueryResult
  其中 QueryResult / AggregatedQueryResult 定义在 app.models.base.base_model
- Controller 只负责：参数解析/校验 -> 调用 QueryAggregator.execute_on_all -> jsonify 返回

额外：
- /reviews-by-movie：按前端 fetchReviews() 预期返回 { total, data }
"""

from flask import Blueprint, request, jsonify

from app.models.base.base_model import AggregatedQueryResult
from app.services.query.query_aggregator import QueryAggregator
from app.models.opengauss.queries import OpenGaussQueries

query_bp = Blueprint('query', __name__)

# 初始化服务
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


@query_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Movie Data Warehouse API'
    })


# 1) 按时间查询电影：year/quarter/month/week 可选但至少一个
@query_bp.route('/movies-by-time', methods=['GET'])
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
            'week': week
        }
        _require_at_least_one(params)

        results: AggregatedQueryResult = query_service.execute_on_all(
            'get_movies_by_time_dynamic',
            filters=params
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_time',
            'parameters': params,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_time',
            'error': str(e)
        }), 400


# 2) 按人员查询电影：director/actor/starring 可选但至少一个
@query_bp.route('/movies-by-person', methods=['GET'])
def movies_by_person():
    try:
        director = _get_str('director')
        actor = _get_str('actor')
        starring = _get_str('starring')

        params = {
            'director': director,
            'actor': actor,
            'starring': starring
        }
        _require_at_least_one(params)

        results: AggregatedQueryResult = query_service.execute_on_all(
            'get_movies_by_person',
            director=director,
            actor=actor,
            starring=starring
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_person',
            'parameters': params,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_person',
            'error': str(e)
        }), 400


# 3) 按属性查询电影：title/genre 可选但至少一个
@query_bp.route('/movies-by-property', methods=['GET'])
def movies_by_property():
    try:
        title = _get_str('title')
        genre = _get_str('genre')

        params = {
            'title': title,
            'genre': genre
        }
        _require_at_least_one(params)

        results: AggregatedQueryResult = query_service.execute_on_all(
            'get_movies_by_property',
            title=title,
            genre=genre
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_property',
            'parameters': params,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_property',
            'error': str(e)
        }), 400


# 4) 按高评分查询电影：min_score/min_reviews 可选但至少一个
@query_bp.route('/high-rated-movies', methods=['GET'])
def high_rated_movies():
    try:
        min_score = _get_float('min_score')
        min_reviews = _get_int('min_reviews')

        params = {
            'min_score': min_score,
            'min_reviews': min_reviews
        }
        _require_at_least_one(params)

        results: AggregatedQueryResult = query_service.execute_on_all(
            'get_high_rated_movies_dynamic',
            min_score=min_score,
            min_reviews=min_reviews
        )

        return jsonify({
            'success': True,
            'query_type': 'high_rated_movies',
            'parameters': params,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'high_rated_movies',
            'error': str(e)
        }), 400


# 5) 演员-演员合作关系：仅 min_collaborations 必填（全局合作对）
@query_bp.route('/actor-collaborations', methods=['GET'])
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
            'limit': limit
        }

        results: AggregatedQueryResult = query_service.execute_on_all(
            'get_actor_actor_collaborations',
            min_collaborations=min_collaborations,
            limit=limit
        )

        return jsonify({
            'success': True,
            'query_type': 'actor_actor_collaborations',
            'parameters': params,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'actor_actor_collaborations',
            'error': str(e)
        }), 400


# 6) 导演-演员合作关系：仅 director 必填（按你的最终需求，不传 min_collaborations）
@query_bp.route('/director-actor-collaborations', methods=['GET'])
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
            'limit': limit
        }

        results: AggregatedQueryResult = query_service.execute_on_all(
            'get_director_actor_collaborations_by_director',
            director=director,
            limit=limit
        )

        return jsonify({
            'success': True,
            'query_type': 'director_actor_collaborations',
            'parameters': params,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'director_actor_collaborations',
            'error': str(e)
        }), 400


# 7) 组合查询电影：year/director/starring/actor/title 至少一个
@query_bp.route('/movies-by-combined-query', methods=['GET'])
def movies_by_combined_query():
    try:
        year = _get_int('year')
        director = _get_str('director')
        starring = _get_str('starring')
        actor = _get_str('actor')
        title = _get_str('title')

        params = {
            'year': year,
            'director': director,
            'starring': starring,
            'actor': actor,
            'title': title
        }
        _require_at_least_one(params)

        results: AggregatedQueryResult = query_service.execute_on_all(
            'get_movies_by_multi_condition',
            year=year,
            director=director,
            starring=starring,
            actor=actor,
            title=title
        )

        return jsonify({
            'success': True,
            'query_type': 'movies_by_combined_query',
            'parameters': params,
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'query_type': 'movies_by_combined_query',
            'error': str(e)
        }), 400


# Reviews: 前端 fetchReviews() 期望返回 { total, data }
@query_bp.route('/reviews-by-movie', methods=['GET'])
def reviews_by_movie():
    """获取指定电影的评论（分页）

    兼容前端 QueryService.fetchReviews：
    - 入参：movie_id 或 asin 或 title（至少一个）
    - 返回：{ total: number, data: Review[] }

    注意：不同数据库 review 表结构可能不一致。
    这里优先以 OpenGauss 的 fact_reviews 为准；如 OpenGauss 失败，返回空。
    """
    try:
        movie_id = _get_str('movie_id')
        asin = _get_str('asin')
        title = _get_str('title')

        page = _get_int('page') or 1
        page_size = _get_int('pageSize') or 20
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        if not any([movie_id, asin, title]):
            raise ValueError('movie_id/asin/title 至少提供一个')

        # 方案A：仅使用 OpenGauss 的 fact_reviews 返回评论明细（不参与三库性能对比）
        # 说明：movie_id/asin 都视为 fact_reviews.movie_id
        target_movie_id = movie_id or asin

        if not target_movie_id:
            raise ValueError('方案A要求提供 movie_id 或 asin')

        offset = (page - 1) * page_size

        with query_service.opengauss_service as s:
            # 1) total
            total_res = s.model.execute_query(OpenGaussQueries.REVIEWS_COUNT_BY_MOVIE_ID, (target_movie_id,))
            total = 0
            if total_res.get('success') and total_res.get('data'):
                total = int(total_res['data'][0].get('total', 0))

            # 2) page data
            data_res = s.model.execute_query(OpenGaussQueries.REVIEWS_BY_MOVIE_ID, (target_movie_id, page_size, offset))
            rows = data_res.get('data') if data_res.get('success') else []

        return jsonify({
            'total': total,
            'data': rows or []
        })

    except Exception as e:
        return jsonify({
            'total': 0,
            'data': [],
            'error': str(e)
        }), 400
