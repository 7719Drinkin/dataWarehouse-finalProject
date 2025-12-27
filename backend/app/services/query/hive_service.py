from typing import Dict, Any, List, Optional
from app.models.base.base_model import QueryResult
from app.models.hive.models import HiveModel


class HiveService:
    """
    Hive 数据库查询服务

    封装 HiveModel，提供电影数据、用户评价及合作关系查询。
    支持时间维度查询、电影维度查询、用户评价分析、演员-导演关系统计。
    """

    def __init__(self):
        self.model = HiveModel()

    def __enter__(self):
        self.model.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.model.disconnect()

    # =========================
    # 一、时间维度查询/统计
    # =========================
    def get_movies_by_year(self, year: int) -> QueryResult:
        """按年份查询电影"""
        return self.model.get_movies_by_year(year)

    def get_movies_by_time(
        self,
        year: Optional[int] = None,
        quarter: Optional[int] = None,
        month: Optional[int] = None,
        week: Optional[int] = None
    ) -> QueryResult:
        """按时间维度动态查询（year/quarter/month/week 至少一个）"""
        return self.model.get_movies_by_time(year=year, quarter=quarter, month=month, week=week)

    def get_movies_by_time_dynamic(self, filters: dict) -> QueryResult:
        """按时间维度动态查询电影"""
        return self.model.get_movies_by_time_dynamic(filters=filters)

    def get_movies_by_quarter(self, year: int) -> QueryResult:
        """按季度统计电影"""
        return self.model.get_movies_by_quarter(year)

    def get_movies_by_month(self, year: int) -> QueryResult:
        """按月份统计电影"""
        return self.model.get_movies_by_month(year)

    def get_movies_by_week(self, year: int) -> QueryResult:
        """按周统计电影"""
        return self.model.get_movies_by_week(year)

    def get_movies_by_day(self, date: str) -> QueryResult:
        """按具体日期查询电影"""
        return self.model.get_movies_by_day(date)

    # HiveModel 当前未提供下列接口，Service 层先不暴露，避免类型检查/调用错误
    # def get_reviews_count_by_time(self, year: int) -> QueryResult:
    #     return self.model.get_reviews_count_by_time(year)

    # def get_reviews_count_by_score(self, min_score: float) -> QueryResult:
    #     return self.model.get_reviews_count_by_score(min_score)

    # def get_movies_reviews_stats_by_time(self, start_date: str, end_date: str) -> QueryResult:
    #     return self.model.get_movies_reviews_stats_by_time(start_date, end_date)

    # =========================
    # 二、电影维度查询/统计
    # =========================
    def get_movies_by_director(self, director: str) -> QueryResult:
        """按导演查询电影"""
        return self.model.get_movies_by_director(director)

    def get_movies_by_actor_starring(self, actor: str) -> QueryResult:
        """按演员查询主演电影"""
        return self.model.get_movies_by_actor_starring(actor)

    def get_movies_by_actor_participated(self, actor: str) -> QueryResult:
        """按演员查询参演电影"""
        return self.model.get_movies_by_actor_participated(actor)

    def get_movies_by_genre(self, genre: str) -> QueryResult:
        """按类型查询电影"""
        return self.model.get_movies_by_genre(genre)

    def get_movies_by_property(
        self,
        title: Optional[str] = None,
        genre: Optional[str] = None
    ) -> QueryResult:
        """按属性查询电影（title/genre 至少一个）"""
        return self.model.get_movies_by_property(title=title, genre=genre)

    def get_movies_by_multi_condition(
        self,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[str] = None
    ) -> QueryResult:
        """调用 HiveModel 的多条件查询"""
        with self.model as m:
            return m.get_movies_by_multi_condition(
                director=director,
                genre=genre,
                year=year,
                min_score=min_score,
                actor=actor
            )

    # =========================
    # 三、用户评价相关
    # =========================
    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> QueryResult:
        """查询高评分电影"""
        return self.model.get_high_rated_movies(min_score, min_reviews)

    def get_high_rated_movies_dynamic(
        self,
        min_score: Optional[float] = None,
        min_reviews: Optional[int] = None
    ) -> QueryResult:
        """高评分电影动态查询（min_score/min_reviews 至少一个）"""
        return self.model.get_high_rated_movies_dynamic(min_score=min_score, min_reviews=min_reviews)

    def get_reviews_by_keyword(self, keyword: str) -> QueryResult:
        """按关键词查询评论"""
        return self.model.get_reviews_by_keyword(keyword)

    # =========================
    # 四、演员-导演关系查询
    # =========================
    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> QueryResult:
        """查询演员合作关系"""
        return self.model.get_actor_collaborations(min_collaborations, limit)

    def get_actor_actor_collaborations(self, min_collaborations: int, limit: int = 20) -> QueryResult:
        """演员-演员合作关系（合作超过几次）"""
        return self.model.get_actor_actor_collaborations(min_collaborations=min_collaborations, limit=limit)

    def get_director_actor_collaborations_by_director(self, director: str, limit: int = 20) -> QueryResult:
        """导演-演员合作关系（仅要求导演名称）"""
        return self.model.get_director_actor_collaborations_by_director(director=director, limit=limit)

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> QueryResult:
        """查询导演与演员合作关系"""
        return self.model.get_director_actor_collaborations(director, min_collaborations, limit)

    # =========================
    # 五、聚合/统计方法 (aggregation)
    # =========================
    def get_movies_by_person(
        self,
        director: Optional[str] = None,
        actor: Optional[str] = None,
        starring: Optional[str] = None
    ) -> QueryResult:
        """按人员查询电影（director/actor/starring 任意组合，但至少一个）"""
        return self.model.get_movies_by_person(
            director=director,
            actor=actor,
            starring=starring
        )

    def aggregate_movies_count_by_year(self) -> QueryResult:
        """按年份统计电影总数"""
        # HiveModel.get_movies_by_year 目前要求 year 为 int，这里保持兼容性，不传 None
        return self.model.get_movies_by_year(0)

    def aggregate_movies_count_by_genre(self) -> QueryResult:
        """按类型统计电影数量"""
        # HiveModel.get_movies_by_genre 目前要求 genre 为 str，这里保持兼容性，不传 None
        return self.model.get_movies_by_genre("")

    def aggregate_high_rated_movies(self, min_score: float = 4.0) -> QueryResult:
        """统计高评分电影数量"""
        return self.model.get_high_rated_movies(min_score)
