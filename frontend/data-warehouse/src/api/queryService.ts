import { httpClient } from './httpClient';
import { BackendAdapter } from './adapters';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  QueryResult,
  QueryParams
} from '../types/apiTypes';
import { QueryType } from '../types/apiTypes';

// 参数映射：前端参数名 -> 后端参数名
const PARAM_MAPPING: Record<string, string> = {
  movie_title: 'title',
  role_type: 'role_type',
  min_score: 'min_score',
  min_reviews: 'min_reviews',
  min_collaborations: 'min_collaborations'
};

// 查询类型到端点的映射
const QUERY_ENDPOINT_MAP: Record<QueryType, string> = {
  [QueryType.MOVIES_BY_YEAR]: API_CONFIG.ENDPOINTS.MOVIES_BY_YEAR,
  [QueryType.MOVIES_BY_MONTH]: API_CONFIG.ENDPOINTS.MOVIES_BY_YEAR, // 使用相同的端点，根据参数区分
  [QueryType.MOVIES_BY_QUARTER]: API_CONFIG.ENDPOINTS.MOVIES_BY_YEAR,
  [QueryType.MOVIES_BY_WEEK]: API_CONFIG.ENDPOINTS.MOVIES_BY_YEAR,
  [QueryType.MOVIES_BY_TITLE]: API_CONFIG.ENDPOINTS.MOVIES_BY_YEAR, // 后端可能需要扩展
  [QueryType.MOVIES_BY_DIRECTOR]: API_CONFIG.ENDPOINTS.MOVIES_BY_DIRECTOR,
  [QueryType.MOVIES_BY_ACTOR_STARRING]: API_CONFIG.ENDPOINTS.MOVIES_BY_ACTOR,
  [QueryType.MOVIES_BY_ACTOR_PARTICIPATED]: API_CONFIG.ENDPOINTS.MOVIES_BY_ACTOR,
  [QueryType.ACTOR_COLLABORATIONS]: API_CONFIG.ENDPOINTS.ACTOR_COLLABORATIONS,
  [QueryType.DIRECTOR_ACTOR_COLLABORATIONS]: API_CONFIG.ENDPOINTS.DIRECTOR_ACTOR_COLLABORATIONS,
  [QueryType.POPULAR_ACTOR_COMBINATIONS]: API_CONFIG.ENDPOINTS.POPULAR_ACTOR_COMBINATIONS,
  [QueryType.MOVIES_BY_GENRE]: API_CONFIG.ENDPOINTS.MOVIES_BY_GENRE,
  [QueryType.HIGH_RATED_MOVIES]: API_CONFIG.ENDPOINTS.HIGH_RATED_MOVIES,
  [QueryType.COMBINED_QUERY]: API_CONFIG.ENDPOINTS.MOVIES_BY_YEAR // 需要后端支持
};

// 参数映射函数
function mapParamsToBackend(queryType: QueryType, params: QueryParams): Record<string, any> {
  const mappedParams: Record<string, any> = {};

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) return;

    const backendKey = PARAM_MAPPING[key] || key;
    mappedParams[backendKey] = value;
  });

  // 特殊处理：为演员查询添加role_type参数
  if (queryType === QueryType.MOVIES_BY_ACTOR_STARRING || queryType === QueryType.MOVIES_BY_ACTOR_PARTICIPATED) {
    mappedParams.role_type = queryType === QueryType.MOVIES_BY_ACTOR_STARRING ? 'starring' : 'participated';
  }

  return mappedParams;
}

export class QueryService {
  // 健康检查
  static async healthCheck(): Promise<ApiResponse<{status: string; service: string; version: string}>> {
    const response = await httpClient.get(API_CONFIG.ENDPOINTS.HEALTH);

    if (!response.success) {
      return {
        success: false,
        data: { status: 'unknown', service: 'Unknown', version: '0.0.0' },
        message: response.error || 'Health check failed',
        timestamp: new Date().toISOString()
      };
    }

    return BackendAdapter.adaptHealthResponse(response.data);
  }

  // 通用查询执行方法
  static async executeQuery(
    queryType: QueryType,
    params: QueryParams
  ): Promise<ApiResponse<QueryResult>> {
    try {
      const endpoint = QUERY_ENDPOINT_MAP[queryType];
      if (!endpoint) {
        throw new Error(`Unsupported query type: ${queryType}`);
      }

      const backendParams = mapParamsToBackend(queryType, params);
      const response = await httpClient.get(endpoint, backendParams);

      if (!response.success) {
        return {
          success: false,
          data: {} as QueryResult, // 提供空的QueryResult作为默认值
          message: response.error || 'Query execution failed',
          timestamp: new Date().toISOString()
        };
      }

      return BackendAdapter.adaptQueryResponse(response.data);
    } catch (error) {
      return {
        success: false,
        data: {} as QueryResult, // 提供空的QueryResult作为默认值
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        timestamp: new Date().toISOString()
      };
    }
  }

  // 便捷方法 - 各种查询类型
  static async queryMoviesByYear(year: number): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.MOVIES_BY_YEAR, { year });
  }

  static async queryMoviesByDirector(director: string): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.MOVIES_BY_DIRECTOR, { director });
  }

  static async queryMoviesByActor(actor: string, roleType: 'starring' | 'participated' = 'starring'): Promise<ApiResponse<QueryResult>> {
    const queryType = roleType === 'starring'
      ? QueryType.MOVIES_BY_ACTOR_STARRING
      : QueryType.MOVIES_BY_ACTOR_PARTICIPATED;
    return this.executeQuery(queryType, { actor, role_type: roleType });
  }

  static async queryMoviesByGenre(genre: string): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.MOVIES_BY_GENRE, { genre });
  }

  static async queryHighRatedMovies(minScore: number = 8.0, minReviews: number = 1000): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.HIGH_RATED_MOVIES, { min_score: minScore, min_reviews: minReviews });
  }

  static async queryActorCollaborations(minCollaborations: number = 2): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.ACTOR_COLLABORATIONS, { min_collaborations: minCollaborations });
  }

  static async queryDirectorActorCollaborations(director: string): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.DIRECTOR_ACTOR_COLLABORATIONS, { director });
  }

  static async queryPopularActorCombinations(genre: string): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.POPULAR_ACTOR_COMBINATIONS, { genre });
  }
}