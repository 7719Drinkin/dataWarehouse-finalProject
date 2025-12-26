import type {
  ApiResponse,
  QueryResult,
  DatabaseResults,
  QueryResultData,
} from '../types/api';
import { DatabaseType } from '../types/api';
import { QueryType } from '../types/query';
import type { QueryParams } from '../types/query';

// 后端响应适配器 - 将后端响应格式转换为前端期望的格式
// Interfaces for raw backend responses to ensure type safety
interface BackendDatabaseResult {
  success?: boolean;
  execution_time?: number;
  result?: QueryResultData;
  record_count?: number;
  error?: string;
}

interface BackendQueryResponse {
  success: boolean;
  results?: Record<string, BackendDatabaseResult>;
  query_type?: QueryType;
  parameters?: QueryParams;
  total_execution_time?: number;
  timestamp?: string;
  error?: string;
}

interface BackendHealthResponse {
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
      [DatabaseType.OPENGAUSS]: { database: DatabaseType.OPENGAUSS, success: false, execution_time: 0, result: [], record_count: 0, error: 'No response' },
      [DatabaseType.HIVE]: { database: DatabaseType.HIVE, success: false, execution_time: 0, result: [], record_count: 0, error: 'No response' },
      [DatabaseType.NEO4J]: { database: DatabaseType.NEO4J, success: false, execution_time: 0, result: [], record_count: 0, error: 'No response' },
    };

    if (backendResponse.results) {
      // 处理后端返回的数据库结果
      Object.entries(backendResponse.results).forEach(([dbKey, dbResult]: [string, BackendDatabaseResult]) => {
        let databaseType: DatabaseType;

        // 映射数据库键名
        switch (dbKey.toLowerCase()) {
          case 'opengauss':
            databaseType = DatabaseType.OPENGAUSS;
            break;
          case 'hive':
            databaseType = DatabaseType.HIVE;
            break;
          case 'neo4j':
            databaseType = DatabaseType.NEO4J;
            break;
          default:
            return; // 跳过未知数据库
        }

        adaptedResults[databaseType] = {
          database: databaseType,
          success: dbResult.success !== false, // 后端可能没有success字段，默认为true
          execution_time: dbResult.execution_time || 0,
          result: Array.isArray(dbResult.result) ? dbResult.result : [],
          record_count: dbResult.record_count || (Array.isArray(dbResult.result) ? dbResult.result.length : 0),
          error: dbResult.error
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
