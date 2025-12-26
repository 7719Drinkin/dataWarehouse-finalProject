from typing import Dict, Any, List
from app.models.neo4j.models import Neo4jModel

class Neo4jService:
    """
    Neo4j 图数据库查询服务

    封装 Neo4jModel，支持节点关系分析、演员-导演合作统计和时间维度聚合。
    """

    def __init__(self):
        self.model = Neo4jModel()

    def __enter__(self):
        self.model.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.model.disconnect()

    # =========================
    # 一、时间维度查询/统计
    # =========================
    def get_movies_count_by_year(self) -> List[Dict[str, Any]]:
        """按年份统计电影数量"""
        return self.model.get_movies_count_by_year()

    def get_movies_count_by_quarter(self) -> List[Dict[str, Any]]:
        """按季度统计电影数量"""
        return self.model.get_movies_count_by_quarter()

    def get_movies_count_by_month(self) -> List[Dict[str, Any]]:
        """按月份统计电影数量"""
        return self.model.get_movies_count_by_month()

    def get_movies_count_by_week(self) -> List[Dict[str, Any]]:
        """按周统计电影数量"""
        return self.model.get_movies_count_by_week()

    def get_movies_count_by_day(self, date: str) -> List[Dict[str, Any]]:
        """按指定日期统计电影数量"""
        return self.model.get_movies_count_by_day(date)

    def get_reviews_count_by_year(self) -> List[Dict[str, Any]]:
        """按年份统计用户评价数量"""
        return self.model.get_reviews_count_by_year()

    def get_reviews_count_by_score(self, min_score: float) -> List[Dict[str, Any]]:
        """按评分区间统计用户评价数量"""
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
        """调用 Neo4jModel 的多条件查询"""
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

    # =========================
    # 五、聚合/统计方法 (aggregation)
    # =========================
    def aggregate_movies_count_by_year(self) -> List[Dict[str, Any]]:
        """按年份统计电影总数"""
        return self.model.get_movies_count_by_year()

    def aggregate_movies_count_by_genre(self, genre: str = None) -> List[Dict[str, Any]]:
        """按类型统计电影数量"""
        return self.model.get_movies_by_genre(genre)

    def aggregate_high_rated_movies(self, min_score: float = 4.0) -> List[Dict[str, Any]]:
        """统计高评分电影数量"""
        return self.model.get_high_rated_movies(min_score)
