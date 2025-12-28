import type { Movie, Review } from '../types/data';
import type { QueryCondition, Pagination, ApiResponse, DataSource, QueryResult } from '../types/api';
import { QueryType } from '../types/query';
import { DataSource as DB } from '../types/api';

// 模拟电影数据
export const generateMockMovies = (count: number): Movie[] => {
  return Array.from({ length: count }, (_, i) => ({
    id: `m_${i + 1}`,
    title: `Mock Movie Title ${i + 1}`,
    release_date: `${2020 - i}-01-01`,
    genres: ['Action', 'Adventure', 'Sci-Fi'].slice(i % 3),
    director: `Director ${i % 5}`,
    actors: [`Actor ${i + 1}`, `Actor ${i + 2}`],
    starring: [`Actor ${i + 1}`],
    versions: ['IMAX', '3D'].slice(i % 2),
    rating: Math.round(Math.random() * 5 * 10) / 10,
    review_count: Math.floor(Math.random() * 1000)
  }));
};

// 模拟评论数据
export const generateMockReviews = (count: number, movieId: string): Review[] => {
  return Array.from({ length: count }, (_, i) => ({
    asin: `asin_${movieId}_${i}`,
    movie_id: movieId,
    user_id: `u_${i + 1}`,
    profile_name: `User ${i + 1}`,
    helpfulness: [i, i + 5],
    score: (i % 5) + 1,
    review_time: new Date().toISOString(),
    review_summary: `Summary for review ${i + 1}`,
    review_text: `This is the detailed review text for movie ${movieId}, review number ${i + 1}.`,
  }));
};

// 创建一个完整的、可导出的模拟查询结果
export const mockQueryResult: QueryResult = {
  query_type: QueryType.HIGH_RATED_MOVIES,
  query_params: { min_score: 8.5, min_reviews: 500 },
  total_execution_time: 450.5,
  timestamp: new Date().toISOString(),
  results: {
    [DB.HIVE]: {
      database: DB.HIVE,
      success: true,
      execution_time: 150.2,
      result: generateMockMovies(5),
      record_count: 5,
    },
    [DB.NEO4J]: {
      database: DB.NEO4J,
      success: true,
      execution_time: 80.3,
      result: generateMockMovies(5),
      record_count: 5,
    },
    [DB.OPENGAUSS]: {
      database: DB.OPENGAUSS,
      success: true,
      execution_time: 220.0,
      result: generateMockMovies(5),
      record_count: 5,
    },
  },
};


const allMovies = generateMockMovies(100);
const allReviews = allMovies.reduce((acc, movie) => {
  return acc.concat(generateMockReviews(100, movie.id));
}, [] as Review[]);

export async function mockFetchMovies(
  conditions: QueryCondition<Movie>,
  pagination: Pagination,
  source: DataSource
): Promise<ApiResponse<Movie[]>> {
  console.log('Fetching mock movies from:', source, 'with conditions:', conditions, 'and pagination:', pagination);
  
  await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 500));

  const start = (pagination.page - 1) * pagination.pageSize;
  const end = start + pagination.pageSize;
  const data = allMovies.slice(start, end);

  return {
    success: true,
    timestamp: new Date().toISOString(),
    total: allMovies.length,
    data,
    executionTime: Math.random() * 100 + 50,
  };
}

export async function mockFetchReviews(
  conditions: QueryCondition<Review>,
  pagination: Pagination,
  source: DataSource
): Promise<ApiResponse<Review[]>> {
  console.log('Fetching mock reviews from:', source, 'with conditions:', conditions, 'and pagination:', pagination);
  
  await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 800));

  const movieId = conditions.filters.movie_id;
  const filteredReviews = movieId ? allReviews.filter(r => r.movie_id === movieId) : allReviews;

  const start = (pagination.page - 1) * pagination.pageSize;
  const end = start + pagination.pageSize;
  const data = filteredReviews.slice(start, end);

  return {
    success: true,
    timestamp: new Date().toISOString(),
    total: filteredReviews.length,
    data,
    executionTime: Math.random() * 200 + 100,
  };
}
