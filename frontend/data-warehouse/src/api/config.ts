// 获取 API URL 的辅助函数
const getBaseUrl = (): string => {
  // 方案 1: 使用 Vite 环境变量
  if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  return 'http://localhost:5000';
};

export const API_CONFIG = {
  BASE_URL: getBaseUrl(),
  ENDPOINTS: {
    HEALTH: '/api/query/health',
    MOVIES_BY_YEAR: '/api/query/movies-by-year',
    MOVIES_BY_DIRECTOR: '/api/query/movies-by-director',
    MOVIES_BY_ACTOR: '/api/query/movies-by-actor',
    MOVIES_BY_GENRE: '/api/query/movies-by-genre',
    HIGH_RATED_MOVIES: '/api/query/high-rated-movies',
    ACTOR_COLLABORATIONS: '/api/query/actor-collaborations',
    DIRECTOR_ACTOR_COLLABORATIONS: '/api/query/director-actor-collaborations',
    POPULAR_ACTOR_COMBINATIONS: '/api/query/popular-actor-combinations'
  },
  TIMEOUT: 30000 // 30秒超时
};