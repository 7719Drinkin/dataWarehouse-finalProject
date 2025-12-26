// API Response Types - MUST BE USED EXACTLY

// Generic API Response Wrapper
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

// Database Types
export enum DatabaseType {
  OPENGAUSS = 'openGauss',
  HIVE = 'Hive',
  NEO4J = 'Neo4j'
}

// Query Types
export enum QueryType {
  MOVIES_BY_TIME = 'movies_by_time',
  MOVIES_BY_PERSON = 'movies_by_person',
  MOVIES_BY_PROPERTY = 'movies_by_property',
  ACTOR_COLLABORATIONS = 'actor_collaborations',
  DIRECTOR_ACTOR_COLLABORATIONS = 'director_actor_collaborations',
  HIGH_RATED_MOVIES = 'high_rated_movies',
  COMBINED_QUERY = 'combined_query'
}

// Query Parameters
export interface QueryParams {
  database?: string;
  year?: number;
  month?: number;
  quarter?: number;
  week?: number;
  movie_title?: string;
  director?: string;
  starring_actor?: string;
  participating_actor?: string;
  genre?: string;
  min_score?: number;
  min_reviews?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
  min_collaborations?: number;
}

// Movie Data Structure
export interface Movie {
  id: string;
  title: string;
  release_date: string;
  director: string;
  actors: string[];
  genres: string[];
  rating: number;
  review_count: number;
  plot?: string;
  runtime?: number;
  box_office?: number;
}

// Database Result Structure
export interface DatabaseResult {
  database: DatabaseType;
  success: boolean;
  execution_time: number; // in milliseconds
  result: Movie[];
  error?: string;
  record_count: number;
}

// Results from all databases
export type DatabaseResults = Record<DatabaseType, DatabaseResult>;

// Complete Query Result
export interface QueryResult {
  query_type: QueryType;
  query_params: QueryParams;
  total_execution_time: number;
  results: DatabaseResults;
  timestamp: string;
}

// Chart Data Structures
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'doughnut';
  data: ChartData;
  options?: any;
}