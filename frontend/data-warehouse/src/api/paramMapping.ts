import type { QueryParams } from '../types/query';
import { QueryType } from '../types/query';

/**
 * 参数映射：前端 QueryParams 字段名 -> 后端 controller 期望的 query string 参数名。
 *
 * 注意：不同查询类型对字段名的约定不同：
 * - movies-by-person 后端期望：director / actor / starring
 *   但前端表单字段是：director / participating_actor / starring_actor
 */

const COMMON_MAPPING: Record<string, string> = {
  movie_title: 'title',
  min_score: 'min_score',
  min_reviews: 'min_reviews',
  min_collaborations: 'min_collaborations',
};

export function mapParamsToBackend(queryType: QueryType, params: QueryParams): Record<string, string | number> {
  const mapped: Record<string, string | number> = {};

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;

    // 查询类型特化映射
    if (queryType === QueryType.MOVIES_BY_PERSON) {
      if (key === 'starring_actor') {
        mapped['starring'] = value as any;
        return;
      }
      if (key === 'participating_actor') {
        mapped['actor'] = value as any;
        return;
      }
    }

    const backendKey = COMMON_MAPPING[key] || key;
    mapped[backendKey] = value as any;
  });

  return mapped;
}

