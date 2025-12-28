import { httpClient } from './httpClient';
import { BackendAdapter } from './adapters';
import { resolveQueryEndpoint, type DatabaseSelection, COMMON_ENDPOINTS } from './queryEndpoints';
import { QueryResponseAdapter, type BackendSingleQueryResponse } from './queryAdapter';
import type { BackendHealthResponse, BackendQueryResponse } from './adapters';
import type {
  ApiResponse,
  QueryResult
} from '../types/api';
import { QueryType } from '../types/query';
import type { QueryParams } from '../types/query';
import type { Review } from '../types/data';
import type { Pagination, QueryCondition, DataSource } from '../types/api';

import { mapParamsToBackend } from './paramMapping';

// 端点解析已迁移到 api/queryEndpoints.ts（支持单库/聚合自动切换）

export class QueryService {
  // 健康检查
  static async healthCheck(): Promise<ApiResponse<{status: string; service: string; version: string}>> {
    const response = await httpClient.get<BackendHealthResponse>(COMMON_ENDPOINTS.HEALTH);

    if (!response.success) {
      return {
        success: false,
        data: { status: 'unknown', service: 'Unknown', version: '0.0.0' },
        message: response.error || 'Health check failed',
        timestamp: new Date().toISOString()
      };
    }

    return BackendAdapter.adaptHealthResponse(response.data ?? null);
  }

  // 通用查询执行方法
  /**
   * 执行查询
   *
   * database 参数约定：
   * - 'aggregated'：走聚合查询接口 /api/query/...
   * - 'hive' | 'opengauss' | 'neo4j'：走单库查询接口 /api/query/{db}/...
   */
  static async executeQuery(
    queryType: QueryType,
    params: QueryParams,
    database: DatabaseSelection = 'aggregated'
  ): Promise<ApiResponse<QueryResult>> {
    try {
      const endpoint = resolveQueryEndpoint(queryType, database);

      const backendParams = mapParamsToBackend(queryType, params);

      // 聚合接口与单库接口的返回结构不同：
      // - 聚合：BackendQueryResponse（包含 results）
      // - 单库：BackendSingleQueryResponse（包含 database + result）
      if (database === 'aggregated') {
      const response = await httpClient.get<BackendQueryResponse>(endpoint, backendParams);

      if (!response.success) {
        return {
          success: false,
            data: {} as QueryResult,
            message: response.error || 'Query execution failed',
            timestamp: new Date().toISOString(),
          };
        }

        return BackendAdapter.adaptQueryResponse(response.data ?? { success: false });
      }

      const response = await httpClient.get<BackendSingleQueryResponse>(endpoint, backendParams);

      if (!response.success) {
        return {
          success: false,
          data: {} as QueryResult,
          message: response.error || 'Query execution failed',
          timestamp: new Date().toISOString(),
        };
      }

      return QueryResponseAdapter.adaptSingleToQueryResult(response.data ?? { success: false });
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

  // 获取指定电影的评论
  static async fetchReviews(
    conditions: QueryCondition<Review>,
    pagination: Pagination,
    source: DataSource
  ): Promise<ApiResponse<Review[]>> {
    try {
      const params = {
        ...conditions.filters,
        page: pagination.page,
        pageSize: pagination.pageSize,
        dataSource: source,
      };

      // 假设后端直接返回 { total: number, data: Review[] } 格式
      const response = await httpClient.get<{ total: number; data: Review[] }>(
        COMMON_ENDPOINTS.REVIEWS_BY_MOVIE,
        params
      );

      if (!response.success || !response.data) {
        return {
          success: false,
          data: [],
          message: response.error || 'Failed to fetch reviews',
          timestamp: new Date().toISOString(),
        };
      }

      return {
        success: true,
        data: response.data.data,
        total: response.data.total,
        message: 'Reviews fetched successfully',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        data: [],
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        timestamp: new Date().toISOString(),
      };
    }
  }
}