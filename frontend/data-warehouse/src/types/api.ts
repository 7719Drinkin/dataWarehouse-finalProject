import type { ActorCollaboration, DirectorActorCollaboration, Movie } from './data';
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

/**
 * Enum for different database types.
 */
export enum DatabaseType {
  OPENGAUSS = 'OpenGauss',
  HIVE = 'Hive',
  NEO4J = 'Neo4j'
}

// A union type for all possible result data structures
export type QueryResultData = Movie[] | ActorCollaboration[] | DirectorActorCollaboration[];

/**
 * Represents the result from a single database.
 */
export interface DatabaseResult {
  database: DatabaseType;
  success: boolean;
  execution_time: number; // in milliseconds
  result: QueryResultData;
  error?: string;
  record_count: number;
}

/**
 * Represents the results from all databases.
 */
export type DatabaseResults = Record<DatabaseType, DatabaseResult>;

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


