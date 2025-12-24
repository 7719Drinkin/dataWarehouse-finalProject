// API响应类型定义
export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  error_code?: string;
  timestamp: string;
}

// 查询结果类型
export interface QueryResult {
  query_type: string;
  parameters: Record<string, unknown>;
  results: DatabaseResults;
  total_execution_time: number;
  charts?: ChartData;
}

export interface DatabaseResults {
  opengauss: DatabaseResult;
  hive: DatabaseResult;
  neo4j: DatabaseResult;
}

export interface DatabaseResult {
  result: Record<string, unknown>[];
  execution_time: number;
  success: boolean;
  error?: string;
}

// 电影数据类型
export interface Movie {
  movie_id: string;
  title: string;
  release_date: string;
  genres: string[];
  director: string;
  actors: string[];
  starring?: string[];
  versions?: string[];
  review_count?: number;
  avg_score?: number;
}

// 图表数据类型
export interface ChartData {
  performance_comparison?: ChartConfig;
  time_series?: ChartConfig;
  rating_distribution?: ChartConfig;
  genre_pie?: ChartConfig;
  collaboration_network?: NetworkData;
}

// Chart.js配置类型
export interface ChartConfig {
  type: 'bar' | 'line' | 'doughnut' | 'pie';
  data: {
    labels: string[];
    datasets: ChartDataset[];
  };
  options?: Record<string, unknown>;
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
  tension?: number;
}

// 网络图数据类型
export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export interface NetworkNode {
  id: number;
  label: string;
  size?: number;
}

export interface NetworkEdge {
  from: number;
  to: number;
  value?: number;
  title?: string;
}

// 查询参数类型
export interface QueryParams {
  year?: number;
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

// 性能统计类型
export interface PerformanceStats {
  fastest_database: string;
  slowest_database: string;
  performance_ratio: number;
  average_execution_time: number;
  success_rate: number;
  successful_queries: number;
  total_queries: number;
}

// 异常数据类型
export interface AnomalyDetail {
  record_index: number;
  missing_fields?: string[];
  score?: number;
  release_date?: string;
  review_time?: string;
  duplicate_hash?: string;
}

// 数据质量类型
export interface DataQualityReport {
  quality_metrics: {
    total_records: number;
    completeness: {
      overall: number;
      by_field: Record<string, number>;
    };
    uniqueness: number;
    validity: number;
    quality_score: number;
  };
  source_analysis: {
    source_distribution: Record<string, number>;
    source_file_distribution: Record<string, number>;
    total_sources: number;
    total_source_files: number;
  };
  anomaly_detection: {
    total_anomalies: number;
    anomalies_by_type: Record<string, number>;
    detailed_anomalies: Record<string, AnomalyDetail[]>;
  };
  recommendations: string[];
}

// 性能报告类型
export interface PerformanceReport {
  summary: {
    total_execution_time: number;
    query_count: number;
    successful_queries: number;
    success_rate: string;
  };
  performance_analysis: {
    fastest_database: string;
    fastest_time: string;
    slowest_database: string;
    slowest_time: string;
    performance_ratio: string;
    average_time: string;
  };
  detailed_results: Record<string, {
    execution_time: string;
    success: boolean;
    result_count: number;
    error?: string;
  }>;
}

// 数据血缘类型
export interface DataLineageReport {
  data_flow: {
    raw_data_sources: string[];
    processing_steps: string[];
    target_systems: string[];
  };
  lineage_stats: {
    total_movies_processed?: number;
    non_movie_data_filtered?: number;
    harry_potter_movies?: number;
    harry_potter_versions?: number;
    source_files?: number;
    [key: string]: number | undefined;
  };
  data_quality_gates: string[];
}

// 健康检查类型
export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
}

// UI状态类型
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  error?: string;
  errorCode?: string;
}

// 查询类型枚举
export enum QueryType {
  MOVIES_BY_YEAR = 'movies_by_year',
  MOVIES_BY_DIRECTOR = 'movies_by_director',
  MOVIES_BY_ACTOR = 'movies_by_actor',
  MOVIES_BY_GENRE = 'movies_by_genre',
  HIGH_RATED_MOVIES = 'high_rated_movies',
  ACTOR_COLLABORATIONS = 'actor_collaborations',
  DIRECTOR_ACTOR_COLLABORATIONS = 'director_actor_collaborations',
  POPULAR_ACTOR_COMBINATIONS = 'popular_actor_combinations'
}

// 数据库类型枚举
export enum DatabaseType {
  OPENGAUSS = 'opengauss',
  HIVE = 'hive',
  NEO4J = 'neo4j'
}
