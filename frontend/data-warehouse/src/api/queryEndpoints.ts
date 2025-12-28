import { API_CONFIG } from './config';
import { QueryType } from '../types/query';

/**
 * 说明：
 * - 之前前端只支持聚合查询（/api/query/...）。
 * - 现在后端新增了单库查询路由：
 *   /api/query/opengauss/...
 *   /api/query/hive/...
 *   /api/query/neo4j/...
 * - 本文件把“查询类型 -> endpoint”统一收敛，并按数据库进行前缀拼接。
 */

export type DatabaseSelection = 'aggregated' | 'opengauss' | 'hive' | 'neo4j';

const AGG_PREFIX = '/api/query';
const SINGLE_PREFIX: Record<Exclude<DatabaseSelection, 'aggregated'>, string> = {
  opengauss: '/api/query/opengauss',
  hive: '/api/query/hive',
  neo4j: '/api/query/neo4j',
};

/**
 * 基础端点（不包含数据库前缀）。
 * 注意：这里的 path 必须和后端 controller 路由保持一致。
 */
const QUERY_PATH_BY_TYPE: Record<QueryType, string> = {
  [QueryType.MOVIES_BY_TIME]: '/movies-by-time',
  [QueryType.MOVIES_BY_PERSON]: '/movies-by-person',
  [QueryType.MOVIES_BY_PROPERTY]: '/movies-by-property',
  [QueryType.HIGH_RATED_MOVIES]: '/high-rated-movies',
  [QueryType.ACTOR_COLLABORATIONS]: '/actor-collaborations',
  [QueryType.DIRECTOR_ACTOR_COLLABORATIONS]: '/director-actor-collaborations',
  // 前端枚举里叫 combined_query，但后端聚合接口 query_type 实际是 movies_by_combined_query
  [QueryType.COMBINED_QUERY]: '/movies-by-combined-query',
};

export function resolveQueryEndpoint(queryType: QueryType, database: DatabaseSelection): string {
  const path = QUERY_PATH_BY_TYPE[queryType];
  if (!path) {
    throw new Error(`Unsupported query type: ${queryType}`);
  }

  // 聚合查询：走原有聚合接口
  if (database === 'aggregated') {
    return `${AGG_PREFIX}${path}`;
  }

  // 单库查询：走对应库的前缀
  return `${SINGLE_PREFIX[database]}${path}`;
}

/**
 * Health / Reviews 等不随数据库切换的端点仍然来自 API_CONFIG。
 * 这里导出只是为了让其他 api 文件更好地分层引用。
 */
export const COMMON_ENDPOINTS = {
  HEALTH: API_CONFIG.ENDPOINTS.HEALTH,
  REVIEWS_BY_MOVIE: API_CONFIG.ENDPOINTS.REVIEWS_BY_MOVIE,
};

