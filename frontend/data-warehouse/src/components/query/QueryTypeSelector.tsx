import React from 'react';
import { QueryType } from '../../types/apiTypes';

interface QueryTypeSelectorProps {
  selectedType: QueryType;
  onTypeChange: (type: QueryType) => void;
}

const QUERY_TYPE_OPTIONS = [
  { value: QueryType.MOVIES_BY_YEAR, label: '按年份查询' },
  { value: QueryType.MOVIES_BY_MONTH, label: '按月份查询' },
  { value: QueryType.MOVIES_BY_QUARTER, label: '按季度查询' },
  { value: QueryType.MOVIES_BY_WEEK, label: '按周查询' },
  { value: QueryType.MOVIES_BY_TITLE, label: '按电影名称查询' },
  { value: QueryType.MOVIES_BY_DIRECTOR, label: '按导演查询' },
  { value: QueryType.MOVIES_BY_ACTOR_STARRING, label: '按演员主演查询' },
  { value: QueryType.MOVIES_BY_ACTOR_PARTICIPATED, label: '按演员参演查询' },
  { value: QueryType.ACTOR_COLLABORATIONS, label: '演员合作关系查询' },
  { value: QueryType.DIRECTOR_ACTOR_COLLABORATIONS, label: '导演-演员合作查询' },
  { value: QueryType.POPULAR_ACTOR_COMBINATIONS, label: '热门演员组合查询' },
  { value: QueryType.MOVIES_BY_GENRE, label: '按电影类别查询' },
  { value: QueryType.HIGH_RATED_MOVIES, label: '高评分电影查询' },
  { value: QueryType.COMBINED_QUERY, label: '组合查询' }
];

const QueryTypeSelector: React.FC<QueryTypeSelectorProps> = ({
  selectedType,
  onTypeChange
}) => {
  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <label style={{
        display: 'block',
        marginBottom: '0.5rem',
        fontWeight: 'bold',
        color: '#333'
      }}>
        查询类型:
      </label>
      <select
        value={selectedType}
        onChange={(e) => onTypeChange(e.target.value as QueryType)}
        style={{
          width: '100%',
          padding: '8px 12px',
          border: '1px solid #d9d9d9',
          borderRadius: '4px',
          fontSize: '14px',
          backgroundColor: 'white'
        }}
      >
        {QUERY_TYPE_OPTIONS.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default QueryTypeSelector;