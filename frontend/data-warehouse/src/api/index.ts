// src/api/index.ts
import type { Movie, Review } from '../types/data';
import type { QueryCondition, Pagination, ApiResponse, DataSource } from '../types/api';

// 模拟电影数据
const generateMockMovies = (count: number): Movie[] => {
  return Array.from({ length: count }, (_, i) => ({
    id: `m_${i + 1}`,            // 改成 id
    title: `Movie Title ${i + 1}`,
    release_date: `${2020 - i}-01-01`,
    genres: ['Action', 'Adventure', 'Sci-Fi'].slice(i % 3),
    director: `Director ${i % 5}`,
    actors: [`Actor ${i + 1}`, `Actor ${i + 2}`],
    starring: [`Actor ${i + 1}`],
    versions: ['IMAX', '3D'].slice(i % 2),
    rating: Math.round(Math.random() * 5 * 10) / 10, // 0~5 星
    review_count: Math.floor(Math.random() * 1000)
  }));
};

// 模拟评论数据
const generateMockReviews = (count: number, movieId: string): Review[] => {
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

const allMovies = generateMockMovies(100);
const allReviews = allMovies.reduce((acc, movie) => {
  return acc.concat(generateMockReviews(100, movie.id));
}, [] as Review[]);


export async function fetchMovies(
  conditions: QueryCondition<Movie>,
  pagination: Pagination,
  source: DataSource
): Promise<ApiResponse<Movie[]>> {
  console.log('Fetching movies from:', source, 'with conditions:', conditions, 'and pagination:', pagination);
  
  // 模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 500));

  const start = (pagination.page - 1) * pagination.pageSize;
  const end = start + pagination.pageSize;
  const data = allMovies.slice(start, end);

  return {
    success: true,
    timestamp: new Date().toISOString(),
    total: allMovies.length,
    data,
    executionTime: Math.random() * 100 + 50, // 模拟执行时间
  };
}

export async function fetchReviews(
  conditions: QueryCondition<Review>,
  pagination: Pagination,
  source: DataSource
): Promise<ApiResponse<Review[]>> {
  console.log('Fetching reviews from:', source, 'with conditions:', conditions, 'and pagination:', pagination);
  
  // 模拟网络延迟
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
    executionTime: Math.random() * 200 + 100, // 模拟执行时间
  };
}
