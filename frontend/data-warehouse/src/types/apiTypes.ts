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
  MOVIES_BY_YEAR = 'movies_by_year',
  MOVIES_BY_MONTH = 'movies_by_month',
  MOVIES_BY_QUARTER = 'movies_by_quarter',
  MOVIES_BY_WEEK = 'movies_by_week',
  MOVIES_BY_TITLE = 'movies_by_title',
  MOVIES_BY_DIRECTOR = 'movies_by_director',
  MOVIES_BY_ACTOR_STARRING = 'movies_by_actor_starring',
  MOVIES_BY_ACTOR_PARTICIPATED = 'movies_by_actor_participated',
  ACTOR_COLLABORATIONS = 'actor_collaborations',
  DIRECTOR_ACTOR_COLLABORATIONS = 'director_actor_collaborations',
  POPULAR_ACTOR_COMBINATIONS = 'popular_actor_combinations',
  MOVIES_BY_GENRE = 'movies_by_genre',
  HIGH_RATED_MOVIES = 'high_rated_movies',
  COMBINED_QUERY = 'combined_query'
}

// Query Parameters
export interface QueryParams {
  year?: number;
  month?: number;
  quarter?: number;
  week?: number;
  movie_title?: string;
  director?: string;
  actor?: string;
  role_type?: 'starring' | 'participated';
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