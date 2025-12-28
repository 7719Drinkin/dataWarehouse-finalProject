import type { ApiResponse, QueryResult, DatabaseResults } from '../types/api';
import type { BackendQueryResponse, BackendDatabaseResult } from './adapters';
import { DataSource } from '../types/api';
import { QueryType } from '../types/query';

/**
 * 说明：
 * - 聚合查询接口：后端返回 { success, results: {opengauss/hive/neo4j: QueryResult}, ... }
 * - 单库查询接口：后端返回 { success, database, result: QueryResult, ... }
 *
 * 前端页面渲染目前统一依赖 QueryResult（其中必须有 results: DatabaseResults）。
 * 因此本适配器负责把“单库响应”包装成 QueryResult：
 * - results 中只有一个数据库为真实值，其他库填充为默认失败值
 * - total_execution_time 可直接使用该库 execution_time 或 0
 */

export interface BackendSingleQueryResponse {
  success: boolean;
  query_type?: string;
  parameters?: Record<string, any>;
  database?: 'opengauss' | 'hive' | 'neo4j';
  result?: Omit<BackendDatabaseResult, never>; // 复用字段：data/execution_time/success/error
  timestamp?: string;
  error?: string;
}

function emptyDbResult(database: DataSource) {
  return { database, success: false, execution_time: 0, result: [], record_count: 0, error: 'No response' };
}

export class QueryResponseAdapter {
  static adaptAggregated(_backendResponse: BackendQueryResponse): ApiResponse<QueryResult> {
    void _backendResponse;
    // 直接复用原有 BackendAdapter 逻辑（避免重复），这里不再实现。
    // 该方法保留只是为了概念分层。
    throw new Error('Use BackendAdapter.adaptQueryResponse for aggregated responses');
  }

  static adaptSingleToQueryResult(single: BackendSingleQueryResponse): ApiResponse<QueryResult> {
    if (!single.success) {
      return {
        success: false,
        data: {} as QueryResult,
        message: single.error || 'Query failed',
        timestamp: single.timestamp || new Date().toISOString(),
      };
    }

    const dbKey = (single.database || '').toLowerCase();
    let ds: DataSource | null = null;
    if (dbKey === 'opengauss') ds = DataSource.OPENGAUSS;
    if (dbKey === 'hive') ds = DataSource.HIVE;
    if (dbKey === 'neo4j') ds = DataSource.NEO4J;

    if (!ds) {
      return {
        success: false,
        data: {} as QueryResult,
        message: 'Invalid database in single query response',
        timestamp: single.timestamp || new Date().toISOString(),
      };
    }

    const rows = Array.isArray(single.result?.data)
      ? single.result!.data!
      : (Array.isArray((single.result as any)?.result) ? (single.result as any).result : []);

    const adaptedResults: DatabaseResults = {
      [DataSource.OPENGAUSS]: emptyDbResult(DataSource.OPENGAUSS),
      [DataSource.HIVE]: emptyDbResult(DataSource.HIVE),
      [DataSource.NEO4J]: emptyDbResult(DataSource.NEO4J),
    };

    adaptedResults[ds] = {
      database: ds,
      success: single.result?.success !== false,
      execution_time: (single.result?.execution_time as any) || 0,
      result: rows,
      record_count: rows.length,
      error: single.result?.error ?? undefined,
    };

    const qr: QueryResult = {
      // 统一 query_type：后端可能返回 movies_by_combined_query，这里映射回前端枚举 combined_query
      query_type: (single.query_type === 'movies_by_combined_query'
        ? QueryType.COMBINED_QUERY
        : (single.query_type as QueryType)) ?? QueryType.MOVIES_BY_TIME,
      query_params: (single.parameters as any) || {},
      total_execution_time: (single.result?.execution_time as any) || 0,
      results: adaptedResults,
      timestamp: single.timestamp || new Date().toISOString(),
    };

    return {
      success: true,
      data: qr,
      message: 'Query executed successfully',
      timestamp: qr.timestamp,
    };
  }
}

