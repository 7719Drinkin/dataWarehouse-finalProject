import React from 'react';
import DataSourceBadge from './DataSourceBadge';
import { DatabaseType } from '../../types/apiTypes';
import type { DatabaseResults } from '../../types/apiTypes';

interface ResultTableProps {
  results: DatabaseResults;
}

const ResultTable: React.FC<ResultTableProps> = ({ results }) => {
  const allMovies = Object.values(results).flatMap(dbResult =>
    dbResult.result.map(movie => ({
      ...movie,
      database: dbResult.database,
      executionTime: dbResult.execution_time,
      success: dbResult.success
    }))
  );

  if (allMovies.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
        暂无查询结果
      </div>
    );
  }

  return (
    <div style={{ marginTop: '2rem' }}>
      {/* Data Source Badges */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '2rem',
        flexWrap: 'wrap'
      }}>
        {Object.values(results).map(dbResult => (
          <DataSourceBadge
            key={dbResult.database}
            database={dbResult.database}
            executionTime={dbResult.execution_time}
            recordCount={dbResult.record_count}
            success={dbResult.success}
          />
        ))}
      </div>

      {/* Results Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          backgroundColor: 'white',
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <thead>
            <tr style={{ backgroundColor: '#fafafa' }}>
              <th style={tableHeaderStyle}>电影名称</th>
              <th style={tableHeaderStyle}>导演</th>
              <th style={tableHeaderStyle}>主演</th>
              <th style={tableHeaderStyle}>类别</th>
              <th style={tableHeaderStyle}>评分</th>
              <th style={tableHeaderStyle}>评价数</th>
              <th style={tableHeaderStyle}>上映日期</th>
              <th style={tableHeaderStyle}>片长(分钟)</th>
              <th style={tableHeaderStyle}>票房</th>
              <th style={tableHeaderStyle}>数据源</th>
            </tr>
          </thead>
          <tbody>
            {allMovies.map((movie, index) => (
              <tr key={`${movie.database}-${movie.id}-${index}`} style={tableRowStyle}>
                <td style={tableCellStyle}>{movie.title}</td>
                <td style={tableCellStyle}>{movie.director}</td>
                <td style={tableCellStyle}>{movie.actors.join(', ')}</td>
                <td style={tableCellStyle}>{movie.genres.join(', ')}</td>
                <td style={tableCellStyle}>{movie.rating}</td>
                <td style={tableCellStyle}>{movie.review_count.toLocaleString()}</td>
                <td style={tableCellStyle}>{movie.release_date}</td>
                <td style={tableCellStyle}>{movie.runtime}</td>
                <td style={tableCellStyle}>
                  {movie.box_office ? `$${movie.box_office.toLocaleString()}` : 'N/A'}
                </td>
                <td style={tableCellStyle}>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    backgroundColor: getDatabaseColor(movie.database),
                    color: 'white'
                  }}>
                    {movie.database}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span style={{ fontWeight: 'bold' }}>
          总计: {allMovies.length} 条记录
        </span>
        <span style={{ color: '#666' }}>
          查询完成时间: {new Date().toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};

const tableHeaderStyle: React.CSSProperties = {
  padding: '12px 16px',
  textAlign: 'left',
  fontWeight: 'bold',
  borderBottom: '2px solid #e8e8e8',
  backgroundColor: '#fafafa'
};

const tableRowStyle: React.CSSProperties = {
  borderBottom: '1px solid #f0f0f0'
};

const tableCellStyle: React.CSSProperties = {
  padding: '12px 16px',
  borderBottom: '1px solid #f0f0f0'
};

function getDatabaseColor(database: DatabaseType): string {
  const colors = {
    [DatabaseType.OPENGAUSS]: '#52c41a',
    [DatabaseType.HIVE]: '#1890ff',
    [DatabaseType.NEO4J]: '#722ed1'
  };
  return colors[database] || '#666';
}

export default ResultTable;