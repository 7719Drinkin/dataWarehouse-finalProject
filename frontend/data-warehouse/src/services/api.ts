import axios from 'axios'
import { QueryType } from '../types';
import type { AxiosResponse } from 'axios';
import type {
  ApiResponse,
  QueryResult,
  HealthCheckResponse,
  DataQualityReport,
  DataLineageReport,
  PerformanceReport,
  QueryParams,
} from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    return Promise.reject(error);
  }
);

class ApiService {
  // 健康检查
  static async healthCheck(): Promise<HealthCheckResponse> {
    const response = await api.get<ApiResponse<HealthCheckResponse>>('/api/health');
    return response.data.data!;
  }

  // 查询电影数据
  static async queryMoviesByYear(year: number): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/movies-by-year', {
      params: { year }
    });
    return response.data.data!;
  }

  static async queryMoviesByDirector(director: string): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/movies-by-director', {
      params: { director }
    });
    return response.data.data!;
  }

  static async queryMoviesByActor(actor: string, roleType: 'starring' | 'participated' = 'starring'): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/movies-by-actor', {
      params: { actor, role_type: roleType }
    });
    return response.data.data!;
  }

  static async queryMoviesByGenre(genre: string): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/movies-by-genre', {
      params: { genre }
    });
    return response.data.data!;
  }

  static async queryHighRatedMovies(minScore: number = 4.0, minReviews: number = 10): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/high-rated-movies', {
      params: { min_score: minScore, min_reviews: minReviews }
    });
    return response.data.data!;
  }

  static async queryActorCollaborations(minCollaborations: number = 2, limit: number = 20): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/actor-collaborations', {
      params: { min_collaborations: minCollaborations, limit }
    });
    return response.data.data!;
  }

  static async queryDirectorActorCollaborations(
    director: string,
    minCollaborations: number = 1,
    limit: number = 10
  ): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/director-actor-collaborations', {
      params: { director, min_collaborations: minCollaborations, limit }
    });
    return response.data.data!;
  }

  static async queryPopularActorCombinations(genre: string): Promise<QueryResult> {
    const response = await api.get<ApiResponse<QueryResult>>('/api/query/popular-actor-combinations', {
      params: { genre }
    });
    return response.data.data!;
  }

  // 数据治理接口
  static async getDataQuality(): Promise<DataQualityReport> {
    const response = await api.get<ApiResponse<DataQualityReport>>('/api/query/data-quality');
    return response.data.data!;
  }

  static async getDataLineage(): Promise<DataLineageReport> {
    const response = await api.get<ApiResponse<DataLineageReport>>('/api/query/data-lineage');
    return response.data.data!;
  }

  // 性能报告
  static async getPerformanceReport(): Promise<PerformanceReport> {
    const response = await api.get<ApiResponse<PerformanceReport>>('/api/query/performance-report');
    return response.data.data!;
  }

  // 通用查询方法
  static async executeQuery(queryType: QueryType, params: QueryParams = {}): Promise<QueryResult> {
    const queryMap = {
      [QueryType.MOVIES_BY_YEAR]: () => this.queryMoviesByYear(params.year!),
      [QueryType.MOVIES_BY_DIRECTOR]: () => this.queryMoviesByDirector(params.director!),
      [QueryType.MOVIES_BY_ACTOR]: () => this.queryMoviesByActor(params.actor!, params.role_type),
      [QueryType.MOVIES_BY_GENRE]: () => this.queryMoviesByGenre(params.genre!),
      [QueryType.HIGH_RATED_MOVIES]: () => this.queryHighRatedMovies(params.min_score, params.min_reviews),
      [QueryType.ACTOR_COLLABORATIONS]: () => this.queryActorCollaborations(params.min_collaborations, params.limit),
      [QueryType.DIRECTOR_ACTOR_COLLABORATIONS]: () => this.queryDirectorActorCollaborations(
        params.director!, params.min_collaborations, params.limit
      ),
      [QueryType.POPULAR_ACTOR_COMBINATIONS]: () => this.queryPopularActorCombinations(params.genre!)
    };

    if (!queryMap[queryType]) {
      throw new Error(`Unknown query type: ${queryType}`);
    }

    return queryMap[queryType]();
  }

  // 批量查询多个数据库的相同查询
  static async compareDatabases(queryType: QueryType, params: QueryParams = {}): Promise<QueryResult> {
    return this.executeQuery(queryType, params);
  }
}

export default ApiService;

