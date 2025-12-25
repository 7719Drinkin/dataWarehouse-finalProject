import React, { useState } from 'react';
import QueryTypeSelector from './QueryTypeSelector';
import { QueryType } from '../../types/apiTypes';
import type { QueryParams } from '../../types/apiTypes';

interface QueryFormProps {
  onSubmit: (queryType: QueryType, params: QueryParams) => void;
  loading?: boolean;
}

const QueryForm: React.FC<QueryFormProps> = ({ onSubmit, loading = false }) => {
  const [queryType, setQueryType] = useState<QueryType>(QueryType.MOVIES_BY_YEAR);
  const [params, setParams] = useState<QueryParams>({
    year: new Date().getFullYear(),
    month: 1,
    quarter: 1,
    week: 1,
    movie_title: '',
    director: '',
    actor: '',
    role_type: 'starring',
    genre: '',
    min_score: 8.0,
    min_reviews: 1000,
    limit: 10,
    min_collaborations: 2
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(queryType, params);
  };

  const updateParam = (key: keyof QueryParams, value: any) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const renderParameterInputs = () => {
    switch (queryType) {
      case QueryType.MOVIES_BY_YEAR:
        return (
          <div>
            <label>年份:</label>
            <input
              type="number"
              value={params.year || ''}
              onChange={(e) => updateParam('year', parseInt(e.target.value))}
              placeholder="输入年份"
              min="1900"
              max="2030"
            />
          </div>
        );

      case QueryType.MOVIES_BY_MONTH:
        return (
          <div>
            <label>年份:</label>
            <input
              type="number"
              value={params.year || ''}
              onChange={(e) => updateParam('year', parseInt(e.target.value))}
              placeholder="输入年份"
            />
            <label>月份:</label>
            <input
              type="number"
              value={params.month || ''}
              onChange={(e) => updateParam('month', parseInt(e.target.value))}
              placeholder="输入月份 (1-12)"
              min="1"
              max="12"
            />
          </div>
        );

      case QueryType.MOVIES_BY_QUARTER:
        return (
          <div>
            <label>年份:</label>
            <input
              type="number"
              value={params.year || ''}
              onChange={(e) => updateParam('year', parseInt(e.target.value))}
              placeholder="输入年份"
            />
            <label>季度:</label>
            <select
              value={params.quarter || 1}
              onChange={(e) => updateParam('quarter', parseInt(e.target.value))}
            >
              <option value={1}>第一季度</option>
              <option value={2}>第二季度</option>
              <option value={3}>第三季度</option>
              <option value={4}>第四季度</option>
            </select>
          </div>
        );

      case QueryType.MOVIES_BY_WEEK:
        return (
          <div>
            <label>年份:</label>
            <input
              type="number"
              value={params.year || ''}
              onChange={(e) => updateParam('year', parseInt(e.target.value))}
              placeholder="输入年份"
            />
            <label>周数:</label>
            <input
              type="number"
              value={params.week || ''}
              onChange={(e) => updateParam('week', parseInt(e.target.value))}
              placeholder="输入周数 (1-52)"
              min="1"
              max="52"
            />
          </div>
        );

      case QueryType.MOVIES_BY_TITLE:
        return (
          <div>
            <label>电影名称:</label>
            <input
              type="text"
              value={params.movie_title || ''}
              onChange={(e) => updateParam('movie_title', e.target.value)}
              placeholder="输入电影名称"
            />
          </div>
        );

      case QueryType.MOVIES_BY_DIRECTOR:
        return (
          <div>
            <label>导演:</label>
            <input
              type="text"
              value={params.director || ''}
              onChange={(e) => updateParam('director', e.target.value)}
              placeholder="输入导演姓名"
            />
          </div>
        );

      case QueryType.MOVIES_BY_ACTOR_STARRING:
      case QueryType.MOVIES_BY_ACTOR_PARTICIPATED:
        return (
          <div>
            <label>演员:</label>
            <input
              type="text"
              value={params.actor || ''}
              onChange={(e) => updateParam('actor', e.target.value)}
              placeholder="输入演员姓名"
            />
          </div>
        );

      case QueryType.ACTOR_COLLABORATIONS:
        return (
          <div>
            <label>最小合作次数:</label>
            <input
              type="number"
              value={params.min_collaborations || 2}
              onChange={(e) => updateParam('min_collaborations', parseInt(e.target.value))}
              min="1"
              max="10"
            />
          </div>
        );

      case QueryType.DIRECTOR_ACTOR_COLLABORATIONS:
        return (
          <div>
            <label>导演:</label>
            <input
              type="text"
              value={params.director || ''}
              onChange={(e) => updateParam('director', e.target.value)}
              placeholder="输入导演姓名"
            />
          </div>
        );

      case QueryType.POPULAR_ACTOR_COMBINATIONS:
        return (
          <div>
            <label>电影类别:</label>
            <input
              type="text"
              value={params.genre || ''}
              onChange={(e) => updateParam('genre', e.target.value)}
              placeholder="输入电影类别"
            />
          </div>
        );

      case QueryType.MOVIES_BY_GENRE:
        return (
          <div>
            <label>电影类别:</label>
            <input
              type="text"
              value={params.genre || ''}
              onChange={(e) => updateParam('genre', e.target.value)}
              placeholder="输入电影类别"
            />
          </div>
        );

      case QueryType.HIGH_RATED_MOVIES:
        return (
          <div>
            <label>最低评分:</label>
            <input
              type="number"
              value={params.min_score || 8.0}
              onChange={(e) => updateParam('min_score', parseFloat(e.target.value))}
              step="0.1"
              min="0"
              max="10"
            />
            <label>最少评价数:</label>
            <input
              type="number"
              value={params.min_reviews || 1000}
              onChange={(e) => updateParam('min_reviews', parseInt(e.target.value))}
              min="0"
            />
          </div>
        );

      case QueryType.COMBINED_QUERY:
        return (
          <div>
            <label>年份:</label>
            <input
              type="number"
              value={params.year || ''}
              onChange={(e) => updateParam('year', parseInt(e.target.value))}
              placeholder="可选"
            />
            <label>导演:</label>
            <input
              type="text"
              value={params.director || ''}
              onChange={(e) => updateParam('director', e.target.value)}
              placeholder="可选"
            />
            <label>演员:</label>
            <input
              type="text"
              value={params.actor || ''}
              onChange={(e) => updateParam('actor', e.target.value)}
              placeholder="可选"
            />
            <label>类别:</label>
            <input
              type="text"
              value={params.genre || ''}
              onChange={(e) => updateParam('genre', e.target.value)}
              placeholder="可选"
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div style={{
      padding: '2rem',
      backgroundColor: '#f5f5f5',
      borderRadius: '8px',
      marginBottom: '2rem'
    }}>
      <h2>电影数据查询</h2>
      <form onSubmit={handleSubmit}>
        <QueryTypeSelector
          selectedType={queryType}
          onTypeChange={setQueryType}
        />

        <div style={{ marginBottom: '1.5rem' }}>
          {renderParameterInputs()}
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#d9d9d9' : '#1890ff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
        >
          {loading ? '查询中...' : '执行查询'}
        </button>
      </form>
    </div>
  );
};

export default QueryForm;