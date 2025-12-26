import { httpClient } from './httpClient';
import { BackendAdapter } from './adapters';
import { API_CONFIG } from './config';
import type {
  ApiResponse,
  QueryResult
} from '../types/api';
import { QueryType } from '../types/query';
import type { QueryParams } from '../types/query';

// 参数映射：前端参数名 -> 后端参数名
const PARAM_MAPPING: Record<string, string> = {
  movie_title: 'title',

  min_score: 'min_score',
  min_reviews: 'min_reviews',
  min_collaborations: 'min_collaborations'
};

// 查询类型到端点的映射
const QUERY_ENDPOINT_MAP: Record<QueryType, string> = {
  [QueryType.MOVIES_BY_TIME]: API_CONFIG.ENDPOINTS.MOVIES_BY_TIME, // 使用相同的端点，根据参数区分
  [QueryType.MOVIES_BY_PERSON]: API_CONFIG.ENDPOINTS.MOVIES_BY_PERSON, // Generic endpoint
  [QueryType.MOVIES_BY_PROPERTY]: API_CONFIG.ENDPOINTS.MOVIES_BY_PROPERTY, // Generic endpoint
  [QueryType.HIGH_RATED_MOVIES]: API_CONFIG.ENDPOINTS.HIGH_RATED_MOVIES,
  [QueryType.ACTOR_COLLABORATIONS]: API_CONFIG.ENDPOINTS.ACTOR_COLLABORATIONS,
  [QueryType.DIRECTOR_ACTOR_COLLABORATIONS]: API_CONFIG.ENDPOINTS.DIRECTOR_ACTOR_COLLABORATIONS,
  [QueryType.COMBINED_QUERY]: API_CONFIG.ENDPOINTS.MOVIES_BY_COMBINED_QUERY // 需要后端支持
};

// 参数映射函数
function mapParamsToBackend(queryType: QueryType, params: QueryParams): Record<string, string | number> {
  const mappedParams: Record<string, string | number> = {};

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) return;

    const backendKey = PARAM_MAPPING[key] || key;
    mappedParams[backendKey] = value;
  });

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
  static async queryHighRatedMovies(minScore: number = 8.0, minReviews: number = 1000): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.HIGH_RATED_MOVIES, { min_score: minScore, min_reviews: minReviews });
  }

  static async queryActorCollaborations(minCollaborations: number = 2): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.ACTOR_COLLABORATIONS, { min_collaborations: minCollaborations });
  }

  static async queryDirectorActorCollaborations(director: string): Promise<ApiResponse<QueryResult>> {
    return this.executeQuery(QueryType.DIRECTOR_ACTOR_COLLABORATIONS, { director });
  }
}