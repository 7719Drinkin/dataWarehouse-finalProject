"""
查询服务
"""
from typing import Dict, Any, List, Optional
from app.models.opengauss.models import OpenGaussModel
from app.models.hive.models import HiveModel
from app.models.neo4j.models import Neo4jModel

class QueryService:
    """统一查询服务"""

    def __init__(self):
        self.opengauss = OpenGaussModel()
        self.hive = HiveModel()
        self.neo4j = Neo4jModel()

    # OpenGauss查询方法
    def query_opengauss_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """OpenGauss: 按年份查询电影"""
        with self.opengauss:
            return self.opengauss.get_movies_by_year(year)

    def query_opengauss_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """OpenGauss: 按导演查询电影"""
        with self.opengauss:
            return self.opengauss.get_movies_by_director(director)

    def query_opengauss_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """OpenGauss: 按演员查询主演电影"""
        with self.opengauss:
            return self.opengauss.get_movies_by_actor_starring(actor)

    def query_opengauss_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """OpenGauss: 按演员查询参演电影"""
        with self.opengauss:
            return self.opengauss.get_movies_by_actor_participated(actor)

    def query_opengauss_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """OpenGauss: 按类型查询电影统计"""
        with self.opengauss:
            return self.opengauss.get_movies_by_genre(genre)

    def query_opengauss_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """OpenGauss: 查询高评分电影"""
        with self.opengauss:
            return self.opengauss.get_high_rated_movies(min_score, min_reviews)

    def query_opengauss_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """OpenGauss: 查询演员合作关系"""
        with self.opengauss:
            return self.opengauss.get_actor_collaborations(min_collaborations, limit)

    def query_opengauss_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """OpenGauss: 查询导演演员合作关系"""
        with self.opengauss:
            return self.opengauss.get_director_actor_collaborations(director, min_collaborations, limit)

    # Hive查询方法
    def query_hive_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """Hive: 按年份查询电影"""
        with self.hive:
            return self.hive.get_movies_by_year(year)

    def query_hive_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """Hive: 按导演查询电影"""
        with self.hive:
            return self.hive.get_movies_by_director(director)

    def query_hive_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """Hive: 按演员查询主演电影"""
        with self.hive:
            return self.hive.get_movies_by_actor_starring(actor)

    def query_hive_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """Hive: 按演员查询参演电影"""
        with self.hive:
            return self.hive.get_movies_by_actor_participated(actor)

    def query_hive_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """Hive: 按类型查询电影统计"""
        with self.hive:
            return self.hive.get_movies_by_genre(genre)

    def query_hive_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """Hive: 查询高评分电影"""
        with self.hive:
            return self.hive.get_high_rated_movies(min_score, min_reviews)

    def query_hive_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """Hive: 查询演员合作关系"""
        with self.hive:
            return self.hive.get_actor_collaborations(min_collaborations, limit)

    def query_hive_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Hive: 查询导演演员合作关系"""
        with self.hive:
            return self.hive.get_director_actor_collaborations(director, min_collaborations, limit)

    # Neo4j查询方法
    def query_neo4j_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """Neo4j: 按年份查询电影"""
        with self.neo4j:
            return self.neo4j.get_movies_by_year(year)

    def query_neo4j_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """Neo4j: 按导演查询电影"""
        with self.neo4j:
            return self.neo4j.get_movies_by_director(director)

    def query_neo4j_movies_by_actor_starring(self, actor: str) -> List[Dict[str, Any]]:
        """Neo4j: 按演员查询主演电影"""
        with self.neo4j:
            return self.neo4j.get_movies_by_actor_starring(actor)

    def query_neo4j_movies_by_actor_participated(self, actor: str) -> List[Dict[str, Any]]:
        """Neo4j: 按演员查询参演电影"""
        with self.neo4j:
            return self.neo4j.get_movies_by_actor_participated(actor)

    def query_neo4j_movies_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """Neo4j: 按类型查询电影统计"""
        with self.neo4j:
            return self.neo4j.get_movies_by_genre(genre)

    def query_neo4j_high_rated_movies(self, min_score: float = 4.0, min_reviews: int = 10) -> List[Dict[str, Any]]:
        """Neo4j: 查询高评分电影"""
        with self.neo4j:
            return self.neo4j.get_high_rated_movies(min_score, min_reviews)

    def query_neo4j_actor_collaborations(self, min_collaborations: int = 2, limit: int = 20) -> List[Dict[str, Any]]:
        """Neo4j: 查询演员合作关系"""
        with self.neo4j:
            return self.neo4j.get_actor_collaborations(min_collaborations, limit)

    def query_neo4j_director_actor_collaborations(self, director: str, min_collaborations: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Neo4j: 查询导演演员合作关系"""
        with self.neo4j:
            return self.neo4j.get_director_actor_collaborations(director, min_collaborations, limit)

    def query_neo4j_popular_actor_combinations(self, genre: str) -> List[Dict[str, Any]]:
        """Neo4j: 查询热门演员组合"""
        with self.neo4j:
            return self.neo4j.get_popular_actor_combinations(genre)

    # 通用查询方法
    def execute_query_on_all_databases(self, query_type: str, **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """在所有数据库上执行相同类型的查询"""
        query_methods = {
            'movies_by_year': {
                'opengauss': self.query_opengauss_movies_by_year,
                'hive': self.query_hive_movies_by_year,
                'neo4j': self.query_neo4j_movies_by_year
            },
            'movies_by_director': {
                'opengauss': self.query_opengauss_movies_by_director,
                'hive': self.query_hive_movies_by_director,
                'neo4j': self.query_neo4j_movies_by_director
            },
            'movies_by_actor_starring': {
                'opengauss': self.query_opengauss_movies_by_actor_starring,
                'hive': self.query_hive_movies_by_actor_starring,
                'neo4j': self.query_neo4j_movies_by_actor_starring
            },
            'movies_by_actor_participated': {
                'opengauss': self.query_opengauss_movies_by_actor_participated,
                'hive': self.query_hive_movies_by_actor_participated,
                'neo4j': self.query_neo4j_movies_by_actor_participated
            },
            'movies_by_genre': {
                'opengauss': self.query_opengauss_movies_by_genre,
                'hive': self.query_hive_movies_by_genre,
                'neo4j': self.query_neo4j_movies_by_genre
            },
            'high_rated_movies': {
                'opengauss': self.query_opengauss_high_rated_movies,
                'hive': self.query_hive_high_rated_movies,
                'neo4j': self.query_neo4j_high_rated_movies
            },
            'actor_collaborations': {
                'opengauss': self.query_opengauss_actor_collaborations,
                'hive': self.query_hive_actor_collaborations,
                'neo4j': self.query_neo4j_actor_collaborations
            },
            'director_actor_collaborations': {
                'opengauss': self.query_opengauss_director_actor_collaborations,
                'hive': self.query_hive_director_actor_collaborations,
                'neo4j': self.query_neo4j_director_actor_collaborations
            }
        }

        if query_type not in query_methods:
            raise ValueError(f"Unknown query type: {query_type}")

        results = {}
        for db_name, query_func in query_methods[query_type].items():
            try:
                results[db_name] = query_func(**kwargs)
            except Exception as e:
                print(f"Error querying {db_name}: {e}")
                results[db_name] = []

        return results

