import type {
  ApiResponse,
  QueryResult,
  DatabaseResults,
  QueryResultData,
} from '../types/api';
import { DataSource } from '../types/api';
import { QueryType } from '../types/query';
import type { QueryParams } from '../types/query';

// 后端响应适配器 - 将后端响应格式转换为前端期望的格式
// Interfaces for raw backend responses to ensure type safety
export interface BackendDatabaseResult {
  success?: boolean;
  execution_time?: number;
  // 后端当前返回字段名为 data（QueryResult.data），同时兼容旧字段 result
  data?: QueryResultData;
  result?: QueryResultData;
  error?: string | null;
}

export interface BackendQueryResponse {
  success: boolean;
  results?: Record<string, BackendDatabaseResult>;
  query_type?: QueryType;
  parameters?: QueryParams;
  total_execution_time?: number;
  timestamp?: string;
  error?: string;
}

export interface BackendHealthResponse {
  status?: string;
  service?: string;
  version?: string;
}

// 后端响应适配器 - 将后端响应格式转换为前端期望的格式
export class BackendAdapter {
  static adaptQueryResponse(backendResponse: BackendQueryResponse): ApiResponse<QueryResult> {
    if (!backendResponse.success) {
      return {
        success: false,
        data: {} as QueryResult, // 提供空的QueryResult作为默认值
        message: backendResponse.error || 'Query failed',
        timestamp: backendResponse.timestamp || new Date().toISOString()
      };
    }

    // 适配数据库结果
    const adaptedResults: DatabaseResults = {
      [DataSource.OPENGAUSS]: { database: DataSource.OPENGAUSS, success: false, execution_time: 0, result: [], record_count: 0, error: 'No response' },
      [DataSource.HIVE]: { database: DataSource.HIVE, success: false, execution_time: 0, result: [], record_count: 0, error: 'No response' },
      [DataSource.NEO4J]: { database: DataSource.NEO4J, success: false, execution_time: 0, result: [], record_count: 0, error: 'No response' },
    };

    if (backendResponse.results) {
      // 处理后端返回的数据库结果
      Object.entries(backendResponse.results).forEach(([dbKey, dbResult]: [string, BackendDatabaseResult]) => {
        let databaseType: DataSource;

        // 映射数据库键名
        switch (dbKey.toLowerCase()) {
          case 'opengauss':
            databaseType = DataSource.OPENGAUSS;
            break;
          case 'hive':
            databaseType = DataSource.HIVE;
            break;
          case 'neo4j':
            databaseType = DataSource.NEO4J;
            break;
          default:
            return; // 跳过未知数据库
        }

        const rows = Array.isArray(dbResult.data)
          ? dbResult.data
          : (Array.isArray(dbResult.result) ? dbResult.result : []);

        adaptedResults[databaseType] = {
          database: databaseType,
          success: dbResult.success !== false, // 后端可能没有success字段，默认为true
          execution_time: dbResult.execution_time || 0,
          result: rows,
          record_count: rows.length,
          error: dbResult.error ?? undefined
        };
      });
    }

    // 计算总执行时间
    const totalExecutionTime = Object.values(adaptedResults).reduce(
      (sum, dbResult) => sum + (dbResult.execution_time || 0),
      0
    );

    const queryResult: QueryResult = {
      query_type: backendResponse.query_type ?? QueryType.MOVIES_BY_TIME, // 此处赋值一个默认值
      query_params: backendResponse.parameters || {},
      total_execution_time: backendResponse.total_execution_time || totalExecutionTime,
      results: adaptedResults,
      timestamp: backendResponse.timestamp || new Date().toISOString()
    };

    return {
      success: true,
      data: queryResult,
      message: 'Query executed successfully',
      timestamp: backendResponse.timestamp || new Date().toISOString()
    };
  }

  // 适配健康检查响应
  static adaptHealthResponse(backendResponse: BackendHealthResponse | null): ApiResponse<{status: string; service: string; version: string}> {
    if (!backendResponse) {
      return {
        success: false,
        data: { status: 'unknown', service: 'Unknown', version: '0.0.0' },
        message: 'Health check failed',
        timestamp: new Date().toISOString()
      };
    }

    return {
      success: true,
      data: {
        status: backendResponse.status || 'unknown',
        service: backendResponse.service || 'Movie Data Warehouse API',
        version: backendResponse.version || '1.0.0'
      },
      message: 'Health check successful',
      timestamp: new Date().toISOString()
    };
  }
}
