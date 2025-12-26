import React, { useState } from 'react';
import QueryTypeSelector from './QueryTypeSelector';
import { QueryType } from '../../types/query';
import type { QueryParams } from '../../types/query';

interface QueryFormProps {
  onSubmit: (queryType: QueryType, params: QueryParams) => void;
  loading?: boolean;
  database: string;
  onDatabaseChange: (db: string) => void;
}

const QueryForm: React.FC<QueryFormProps> = ({
  onSubmit,
  loading = false,
  database,
  onDatabaseChange,
}) => {
    const [queryType, setQueryType] = useState<QueryType>(QueryType.MOVIES_BY_TIME);
  const [params, setParams] = useState<QueryParams>({
    movie_title: '',
    director: '',
    starring_actor: '',
    participating_actor: '',
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

  const updateParam = (key: keyof QueryParams, value: string | number | undefined) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const renderParameterInputs = () => {
    // Helper to create styled input fields for consistency
    const createInput = (label: string, key: keyof QueryParams, type: string, placeholder: string, min?: number, max?: number) => (
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ color: '#4b5563', fontSize: '14px', display: 'block', marginBottom: '4px' }}>{label}:</label>
        <input
          type={type}
          value={params[key] || ''}
          onChange={(e) => updateParam(key, e.target.value ? (type === 'number' ? parseInt(e.target.value) : e.target.value) : undefined)}
          placeholder={placeholder}
          min={min}
          max={max}
          style={{
            width: '100%',
            padding: '10px',
            borderRadius: '6px',
            border: '1px solid #d1d5db',
            fontSize: '16px',
            backgroundColor: 'white'
          }}
        />
      </div>
    );

    switch (queryType) {
      case QueryType.MOVIES_BY_TIME:
        return (
          <div>
            {createInput('年份', 'year', 'number', '可选，例如: 2023', 1900, 2030)}
            {createInput('月份', 'month', 'number', '可选 (1-12)', 1, 12)}
            {createInput('季度', 'quarter', 'number', '可选 (1-4)', 1, 4)}
            {createInput('周', 'week', 'number', '可选 (1-52)', 1, 52)}
          </div>
        );

      case QueryType.MOVIES_BY_PERSON:
        return (
          <div>
            {createInput('导演', 'director', 'text', '可选')}
            {createInput('主演', 'starring_actor', 'text', '可选')}
            {createInput('参演', 'participating_actor', 'text', '可选')}
          </div>
        );

      case QueryType.MOVIES_BY_PROPERTY:
        return (
          <div>
            {createInput('电影名称', 'movie_title', 'text', '可选')}
            {createInput('电影类别', 'genre', 'text', '可选')}
          </div>
        );

      case QueryType.ACTOR_COLLABORATIONS:
        return createInput('最小合作次数', 'min_collaborations', 'number', '例如: 2', 1, 10);

      case QueryType.DIRECTOR_ACTOR_COLLABORATIONS:
        return createInput('导演', 'director', 'text', '输入导演姓名');

      case QueryType.HIGH_RATED_MOVIES:
        return (
          <div>
            {createInput('最低评分', 'min_score', 'number', '例如: 8.0', 0, 10)}
            {createInput('最少评价数', 'min_reviews', 'number', '例如: 1000', 0)}
          </div>
        );

      case QueryType.COMBINED_QUERY:
        return (
          <div>
            {createInput('年份', 'year', 'number', '可选')}
            {createInput('导演', 'director', 'text', '可选')}
                        {createInput('主演', 'starring_actor', 'text', '可选')}
            {createInput('参演', 'participating_actor', 'text', '可选')}
            {createInput('类别', 'genre', 'text', '可选')}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ textAlign: 'center', color: '#1f2937', marginBottom: '1.5rem', fontSize: '24px', fontWeight: 'bold' }}>电影数据查询</h2>
      <form onSubmit={handleSubmit}>
        <QueryTypeSelector
          selectedType={queryType}
          onTypeChange={setQueryType}
        />

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ color: '#4b5563', fontSize: '16px', marginBottom: '8px' }}>选择数据源</h3>
          <select
            value={database}
            onChange={(e) => onDatabaseChange(e.target.value)}
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '6px',
              border: '1px solid #d1d5db',
              backgroundColor: 'white',
              fontSize: '16px',
              transition: 'border-color 0.2s, box-shadow 0.2s',
              cursor: 'pointer'
            }}
          >
            <option value="hive">Hive</option>
            <option value="opengauss">OpenGauss</option>
            <option value="neo4j">Neo4j</option>
          </select>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          {renderParameterInputs()}
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px 20px',
            fontSize: '16px',
            fontWeight: 'bold',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            background: loading ? '#9ca3af' : 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s, box-shadow 0.2s',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? '查询中...' : '执行查询'}
        </button>
      </form>
    </div>
  );
};

export default QueryForm;