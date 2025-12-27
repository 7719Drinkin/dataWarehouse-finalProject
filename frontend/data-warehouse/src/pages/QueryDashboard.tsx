import React, { useState } from 'react';
import QueryForm from '../components/query/QueryForm';
import QueryResultDisplay from '../components/result/QueryResultDisplay';
import ChartRenderer from '../components/chart/ChartRenderer';
import LoadingIndicator from '../components/common/LoadingIndicator';
import ErrorMessage from '../components/common/ErrorMessage';
import WelcomePlaceholder from '../components/common/WelcomePlaceholder';
import { QueryService } from '../api/queryService';
import { mockQueryResult } from '../api/mock'; // 导入模拟数据
import type { QueryType, QueryParams } from '../types/query';
import type { QueryResult, DataSource } from '../types/api';
import type {  ChartConfig} from '../types/data';

const QueryDashboard: React.FC = () => {
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartConfig, setChartConfig] = useState<ChartConfig | null>(null);
  // database 既控制“前端展示的 dataSource”，也控制“请求打到单库还是聚合接口”
  // - aggregated：调用 /api/query/...（三库并发）
  // - hive/opengauss/neo4j：调用 /api/query/{db}/...（单库）
  const [database, setDatabase] = useState('aggregated');

  const handleQuery = async (queryType: QueryType, params: QueryParams) => {
    setLoading(true);
    setError(null);

    try {
      const response = await QueryService.executeQuery(
        queryType,
        params,
        database as any
      );

      if (response.success) {
        setQueryResult(response.data);
        generateChart(response.data);
      } else {
        setError(response.message || '查询失败');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : '网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 新增：加载模拟数据的处理函数
  const handleLoadMockData = () => {
    setError(null);
    setQueryResult(mockQueryResult);
    generateChart(mockQueryResult);
  };

  const generateChart = (result: QueryResult) => {
    // Generate a simple chart showing execution times by database
    const labels = Object.keys(result.results);
    const executionTimes = Object.values(result.results).map(db => db.execution_time);

    const chartConfig: ChartConfig = {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: '执行时间 (ms)',
          data: executionTimes,
          backgroundColor: '#1890ff'
        }]
      }
    };

    setChartConfig(chartConfig);
  };

  const handleRetry = () => {
    if (queryResult) {
      handleQuery(queryResult.query_type, queryResult.query_params);
    }
  };

  return (
    <div style={{
      height: '100vh',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      display: 'flex',
      flexDirection: 'column'
    }}> 
      {/* Header */}
      <div style={{
        padding: '20px 24px',
        backgroundColor: 'rgba(255, 255, 255, 0.7)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
        flexShrink: 0,
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
      }}>
        <h1 style={{
          margin: 0,
          color: '#333',
          fontSize: '28px',
          fontWeight: 'bold'
        }}>
          电影数据仓库查询系统
        </h1>
        <p style={{
          margin: '8px 0 0 0',
          color: '#666',
          fontSize: '16px'
        }}>
          支持多种查询方式，实时展示来自多个数据源的结果
        </p>
      </div>

      <div style={{ flex: 1, display: 'flex', padding: '20px', gap: '20px', minHeight: 0 }}>
          {/* Left Panel: Query Form */}
          <div style={{
            flex: '0 0 400px',
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            backdropFilter: 'blur(10px)',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            overflowY: 'auto',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            padding: '20px' // Added padding for inner content
          }}>
            <QueryForm
              onSubmit={handleQuery}
              loading={loading}
              database={database}
              onDatabaseChange={setDatabase}
            />
            {/* 新增：加载模拟数据的按钮 */}
            <button
              onClick={handleLoadMockData}
              style={{
                width: '100%',
                padding: '10px',
                marginTop: '16px',
                backgroundColor: '#722ed1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold',
                transition: 'background-color 0.3s',
              }}
            >
              加载模拟数据
            </button>
          </div>

          {/* Right Panel: Results */}
          <div style={{
            flex: '1 1 auto',
            minWidth: 0,
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            backdropFilter: 'blur(10px)',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            padding: '20px',
            overflowY: 'auto',
            border: '1px solid rgba(255, 255, 255, 0.3)'
          }}>
            {/* Loading State */}
            {loading && <LoadingIndicator message="正在查询数据..." />}

            {/* Error State */}
            {error && (
              <ErrorMessage message={error} onRetry={handleRetry} />
            )}

            {/* Welcome Placeholder */}
            {!loading && !error && !queryResult && <WelcomePlaceholder />}

            {/* Results */}
            {queryResult && !loading && !error && (
              <div>
                {/* Query Summary */}
                <div style={{
                  marginBottom: '2rem',
                  padding: '1rem',
                  backgroundColor: '#f6ffed',
                  border: '1px solid #b7eb8f',
                  borderRadius: '6px'
                }}>
                  <h2 style={{ margin: '0 0 8px 0', color: '#52c41a' }}>
                    查询成功
                  </h2>
                  <p style={{ margin: 0, color: '#666' }}>
                    查询类型: {queryResult.query_type} | 总执行时间: {queryResult.total_execution_time}ms
                  </p>
                </div>

                {/* Results Display */}
                {/* 单库/聚合选择与 ReviewList 的 dataSource 不完全一致：
                    - aggregated 不是一个真实库，这里默认用 OpenGauss 拉评论（后端 reviews-by-movie 也主要走 OpenGauss）
                    - 单库时按所选库传递
                */}
                <QueryResultDisplay
                  results={queryResult.results}
                  dataSource={(database === 'aggregated' ? 'OpenGauss' : (database === 'opengauss' ? 'OpenGauss' : database === 'hive' ? 'Hive' : 'Neo4j')) as DataSource}
                />

                {/* Chart */}
                {chartConfig && (
                  <ChartRenderer
                    config={chartConfig}
                    title="各数据源执行时间对比"
                  />
                )}
              </div>
            )}
          </div>
        </div>
    </div>
  );
};

export default QueryDashboard;
