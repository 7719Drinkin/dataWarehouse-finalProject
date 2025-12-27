from typing import Dict, Any, List
from app.models.opengauss.models import OpenGaussModel

class OpenGaussService:
    """
    OpenGauss 数据库查询服务

    封装 OpenGaussModel，提供以下功能：
    1. 时间维度查询/统计
    2. 电影维度查询/统计
    3. 用户评价相关查询
    4. 演员-导演关系查询

    支持上下文管理 (with) 自动建立和关闭数据库连接。
    """

    def __init__(self):
        self.model = OpenGaussModel()

    def __enter__(self):
        self.model.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.model.disconnect()

    # =========================
    # 一、时间维度查询/统计
    # =========================
    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """按年份查询电影"""
        return self.model.get_movies_by_year(year)

    def get_movies_by_quarter(self, year: int) -> List[Dict[str, Any]]:
        """按季度查询电影"""
        return self.model.get_movies_by_quarter(year)

    def get_movies_by_month(self, year: int) -> List[Dict[str, Any]]:
        """按月份查询电影"""
        return self.model.get_movies_by_month(year)

    def get_movies_by_week(self, year: int) -> List[Dict[str, Any]]:
        """按周查询电影"""
        return self.model.get_movies_by_week(year)

    def get_movies_by_day(self, day: str) -> List[Dict[str, Any]]:
        """按具体日期查询电影"""
        return self.model.get_movies_by_day(day)

    def get_reviews_count_by_time(self, year: int) -> List[Dict[str, Any]]:
        """按年份统计用户评价数量"""
        return self.model.get_reviews_count_by_time(year)

    def get_reviews_count_by_score(self, min_score: float) -> List[Dict[str, Any]]:
        """按最低评分统计用户评价数量"""
        return self.model.get_reviews_count_by_score(min_score)

    def get_movies_reviews_stats_by_time(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """按时间段统计电影及其评价信息"""
        return self.model.get_movies_reviews_stats_by_time(start_date, end_date)

    # =========================
    # 二、电影维度查询/统计
    # =========================
    def get_movies_versions_by_title(self, title: str) -> List[Dict[str, Any]]:
        """查询指定电影的所有版本"""
        return self.model.get_movies_versions_by_title(title)

    def get_movie_reviews_by_title(self, title: str) -> List[Dict[str, Any]]:
        """按电影名称查询用户评价"""
        return self.model.get_movie_reviews_by_title(title)

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """按导演查询电影"""
        return self.model.get_movies_by_director(director)

    def get_director_movie_count(self, director: str) -> List[Dict[str, Any]]:
        """统计导演作品数量"""
        return self.model.get_director_movie_count(director)

    def get_movies_by_actor_starring(self, actor_id: int) -> List[Dict[str, Any]]:
        """查询指定演员主演的电影"""
        return self.model.get_movies_by_actor_starring(actor_id)

    def get_movies_by_actor_participated(self, actor_id: int) -> List[Dict[str, Any]]:
        """查询指定演员参演的电影"""
        return self.model.get_movies_by_actor_participated(actor_id)

    def get_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """按电影类型查询电影"""
        return self.model.get_movies_by_genre(genre)

    def get_movies_by_multi_condition(
        self,
        director: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        min_score: Optional[float] = None,
        actor: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Service 层多条件查询接口

        调用 Model 层的 get_movies_by_multi_condition 方法，
        支持可选参数并通过上下文管理器自动连接和断开数据库。

        返回：
            List[Dict[str, Any]]: 满足条件的电影列表
        """
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
    def get_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """查询高评分电影"""
        return self.model.get_high_rated_movies(min_score, min_reviews)

    def get_reviews_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """按关键词查询评论"""
        return self.model.get_reviews_by_keyword(keyword)

    # =========================
    # 四、演员-导演关系查询
    # =========================
    def get_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """查询演员合作关系"""
        return self.model.get_actor_collaborations(min_collaborations, limit)

    def get_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """查询导演与演员合作关系"""
        return self.model.get_director_actor_collaborations(director, min_collaborations, limit)

    def get_popular_actor_combinations_by_genre(self, genre: str, limit: int = 10) -> List[Dict[str, Any]]:
        """查询指定类型热门演员组合"""
        return self.model.get_popular_actor_combinations_by_genre(genre, limit)
