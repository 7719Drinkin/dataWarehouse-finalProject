import React from 'react';
import { QueryType } from '../../types/query';

interface QueryTypeSelectorProps {
  selectedType: QueryType;
  onTypeChange: (type: QueryType) => void;
}

const QUERY_TYPE_OPTIONS = [
  { value: QueryType.MOVIES_BY_TIME, label: '按时间查询' },
  { value: QueryType.MOVIES_BY_PERSON, label: '按人员查询' },
  { value: QueryType.MOVIES_BY_PROPERTY, label: '按属性查询' },
  { value: QueryType.HIGH_RATED_MOVIES, label: '高评分电影查询' },
  { value: QueryType.ACTOR_COLLABORATIONS, label: '演员-演员合作关系查询' },
  { value: QueryType.DIRECTOR_ACTOR_COLLABORATIONS, label: '导演-演员合作关系查询' },
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