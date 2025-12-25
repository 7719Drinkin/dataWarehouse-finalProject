// 声明process类型
declare const process: {
  env: {
    REACT_APP_API_URL?: string;
    [key: string]: string | undefined;
  };
};

export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
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
