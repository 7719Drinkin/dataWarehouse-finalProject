import React, { useState } from 'react';
import QueryForm from '../components/query/QueryForm';
import ResultTable from '../components/result/ResultTable';
import ChartRenderer from '../components/chart/ChartRenderer';
import LoadingIndicator from '../components/common/LoadingIndicator';
import ErrorMessage from '../components/common/ErrorMessage';
import { QueryService } from '../api/queryService';
import { QueryType } from '../types/apiTypes';
import type {
  QueryParams,
  QueryResult,
  ChartConfig
} from '../types/apiTypes';

const QueryDashboard: React.FC = () => {
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartConfig, setChartConfig] = useState<ChartConfig | null>(null);

  const handleQuery = async (queryType: QueryType, params: QueryParams) => {
    setLoading(true);
    setError(null);

    try {
      const response = await QueryService.executeQuery(queryType, params);

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
      minHeight: '100vh',
      backgroundColor: '#f0f2f5',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        {/* Header */}
        <div style={{
          padding: '24px',
          borderBottom: '1px solid #e8e8e8',
          backgroundColor: '#fafafa',
          borderRadius: '8px 8px 0 0'
        }}>
          <h1 style={{
            margin: 0,
            color: '#333',
            fontSize: '28px',
            fontWeight: 'bold'
          }}>
            🎬 电影数据仓库查询系统
          </h1>
          <p style={{
            margin: '8px 0 0 0',
            color: '#666',
            fontSize: '16px'
          }}>
            支持多种查询方式，实时展示来自多个数据源的结果
          </p>
        </div>

        {/* Query Form */}
        <QueryForm onSubmit={handleQuery} loading={loading} />

        {/* Loading State */}
        {loading && <LoadingIndicator message="正在查询数据..." />}

        {/* Error State */}
        {error && (
          <div style={{ padding: '20px' }}>
            <ErrorMessage message={error} onRetry={handleRetry} />
          </div>
        )}

        {/* Results */}
        {queryResult && !loading && !error && (
          <div style={{ padding: '20px' }}>
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

            {/* Results Table */}
            <ResultTable results={queryResult.results} />

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
  );
};

export default QueryDashboard;