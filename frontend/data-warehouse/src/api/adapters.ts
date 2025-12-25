import type {
  ApiResponse,
  QueryResult,
  DatabaseResults
} from '../types/apiTypes';
import { DatabaseType } from '../types/apiTypes';

// 后端响应适配器 - 将后端响应格式转换为前端期望的格式
export class BackendAdapter {
  static adaptQueryResponse(backendResponse: any): ApiResponse<QueryResult> {
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
      [DatabaseType.OPENGAUSS]: {} as any,
      [DatabaseType.HIVE]: {} as any,
      [DatabaseType.NEO4J]: {} as any
    };

    if (backendResponse.results) {
      // 处理后端返回的数据库结果
      Object.entries(backendResponse.results).forEach(([dbKey, dbResult]: [string, any]) => {
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
      query_type: backendResponse.query_type || 'unknown',
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
  static adaptHealthResponse(backendResponse: any): ApiResponse<{status: string; service: string; version: string}> {
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
