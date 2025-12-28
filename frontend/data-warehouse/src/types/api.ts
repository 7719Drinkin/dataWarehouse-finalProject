import type { QueryParams, QueryType } from './query';

/**
 * Generic API Response Wrapper
 */
/**
 * Generic API Response Wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
  total?: number; // For paginated data
  executionTime?: number; // in milliseconds
}

// 后端返回的行结构在不同查询中差异很大，这里使用“动态字段/动态列”承接
export type QueryResultData = Array<Record<string, any>>;

/**
 * Represents the result from a single database.
 */
export interface DatabaseResult {
  database: DataSource;
  success: boolean;
  execution_time: number; // in milliseconds
  result: QueryResultData;
  error?: string;
  record_count: number;
}

/**
 * Represents the results from all databases.
 */
export type DatabaseResults = Record<DataSource, DatabaseResult>;

/**
 * Represents the complete query result.
 */
export interface QueryResult {
  query_type: QueryType;
  query_params: QueryParams;
  total_execution_time: number;
  results: DatabaseResults;
  timestamp: string;
}

/**
 * Represents pagination parameters.
 */
export interface Pagination {
  page: number;
  pageSize: number;
}

/**
 * Represents query conditions.
 */
export interface QueryCondition<T> {
  filters: Partial<T>;
}

/**
 * Enum for data sources.
 */
export enum DataSource {
  OPENGAUSS = 'OpenGauss',
  HIVE = 'Hive',
  NEO4J = 'Neo4j'
}


