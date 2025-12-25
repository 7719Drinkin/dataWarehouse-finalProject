import React from 'react';
import { DatabaseType } from '../../types/apiTypes';

interface DataSourceBadgeProps {
  database: DatabaseType;
  executionTime: number;
  recordCount: number;
  success: boolean;
}

const DATABASE_COLORS = {
  [DatabaseType.OPENGAUSS]: '#52c41a',
  [DatabaseType.HIVE]: '#1890ff',
  [DatabaseType.NEO4J]: '#722ed1'
};

const DataSourceBadge: React.FC<DataSourceBadgeProps> = ({
  database,
  executionTime,
  recordCount,
  success
}) => {
  const color = DATABASE_COLORS[database];

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '4px 12px',
      backgroundColor: success ? `${color}15` : '#fff2f0',
      border: `1px solid ${success ? color : '#ffccc7'}`,
      borderRadius: '20px',
      fontSize: '14px'
    }}>
      <div style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: success ? color : '#ff4d4f'
      }} />
      <span style={{ fontWeight: 'bold', color: success ? color : '#cf1322' }}>
        {database}
      </span>
      <span style={{ color: '#666' }}>
        {recordCount} 条记录
      </span>
      <span style={{ color: '#666' }}>
        {executionTime.toFixed(0)}ms
      </span>
      {!success && (
        <span style={{ color: '#cf1322', fontSize: '12px' }}>
          失败
        </span>
      )}
    </div>
  );
};

export default DataSourceBadge;