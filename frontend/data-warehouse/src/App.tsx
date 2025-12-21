import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme, Spin, Alert } from 'antd';
import zhCN from 'antd/locale';
import 'antd/dist/reset.css';

import Layout from './components/Layout';
import QueryForm from './components/QueryForm';
import PerformanceChart from './components/PerformanceChart';
import DataVisualization from './components/DataVisualization';
import DataQualityDashboard from './components/DataQualityDashboard';
import ApiService from './services/api';
import type { QueryType, QueryResult, DatabaseResults, PerformanceStats, QueryParams } from './types';
import { formatQueryTypeName } from './utils/formatters';

function App() {
  const [loading, setLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [performanceStats, setPerformanceStats] = useState<PerformanceStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'query' | 'results' | 'quality'>('query');

  // 处理查询
  const handleQuery = async (queryType: QueryType, params: QueryParams) => {
    setLoading(true);
    setError(null);

    try {
      const result = await ApiService.executeQuery(queryType, params);
      setQueryResult(result);

      // 计算性能统计
      if (result.results) {
        const stats: PerformanceStats = {
          fastest_database: '',
          slowest_database: '',
          performance_ratio: 1,
          average_execution_time: 0,
          success_rate: 0,
          successful_queries: 0,
          total_queries: 0
        };

        const dbResults = result.results as DatabaseResults;
        const databases = Object.keys(dbResults);
        stats.total_queries = databases.length;

        let totalTime = 0;
        let successfulCount = 0;
        let fastestTime = Infinity;
        let slowestTime = 0;
        let fastestDb = '';
        let slowestDb = '';

        databases.forEach(db => {
          const dbResult = dbResults[db as keyof DatabaseResults];
          totalTime += dbResult.execution_time;

          if (dbResult.success) {
            successfulCount++;

            if (dbResult.execution_time < fastestTime) {
              fastestTime = dbResult.execution_time;
              fastestDb = db;
            }

            if (dbResult.execution_time > slowestTime) {
              slowestTime = dbResult.execution_time;
              slowestDb = db;
            }
          }
        });

        stats.successful_queries = successfulCount;
        stats.success_rate = successfulCount / databases.length;
        stats.average_execution_time = totalTime / databases.length;
        stats.fastest_database = fastestDb;
        stats.slowest_database = slowestDb;
        stats.performance_ratio = slowestTime > 0 ? fastestTime / slowestTime : 1;

        setPerformanceStats(stats);
      }

      setCurrentView('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败');
    } finally {
      setLoading(false);
    }
  };

  // 切换到查询界面
  const handleBackToQuery = () => {
    setCurrentView('query');
    setQueryResult(null);
    setPerformanceStats(null);
    setError(null);
  };

  // 切换到数据质量界面
  const handleShowQuality = () => {
    setCurrentView('quality');
  };

  // 获取页面标题和面包屑
  const getPageInfo = () => {
    switch (currentView) {
      case 'query':
        return {
          title: '数据查询',
          breadcrumb: ['查询']
        };
      case 'results':
        return {
          title: queryResult ? formatQueryTypeName(queryResult.query_type) : '查询结果',
          breadcrumb: ['查询', '结果']
        };
      case 'quality':
        return {
          title: '数据治理',
          breadcrumb: ['治理']
        };
      default:
        return {
          title: '电影数据仓库',
          breadcrumb: []
        };
    }
  };

  const pageInfo = getPageInfo();

  // 渲染主要内容
  const renderContent = () => {
    if (error) {
      return (
        <Alert
          message="查询失败"
          description={error}
          type="error"
          showIcon
          action={
            <a onClick={handleBackToQuery}>返回查询</a>
          }
        />
      );
    }

    switch (currentView) {
      case 'query':
        return (
          <QueryForm
            onQuery={handleQuery}
            loading={loading}
          />
        );

      case 'results': {
        if (!queryResult || !performanceStats) {
          return <Spin size="large" tip="加载结果..." />;
        }

        const dbResults = queryResult.results as DatabaseResults;
        // 获取最成功的数据库结果用于可视化
        const bestResult = Object.values(dbResults).find(r => r.success);
        const resultData = bestResult?.result || [];

        return (
          <div>
            {/* 性能对比图表 */}
            <PerformanceChart
              results={dbResults}
              stats={performanceStats}
              totalTime={queryResult.total_execution_time}
            />

            {/* 数据可视化 */}
            {resultData.length > 0 && (
              <>
                <div style={{ margin: '32px 0 16px 0' }}>
                  <h3>数据可视化分析</h3>
                </div>
                <DataVisualization
                  data={resultData}
                  title={`查询结果分析 (${resultData.length} 条记录)`}
                />
              </>
            )}

            {/* 返回查询按钮 */}
            <div style={{ marginTop: 32, textAlign: 'center' }}>
              <a onClick={handleBackToQuery} style={{ marginRight: 16 }}>
                ← 返回查询
              </a>
              <a onClick={handleShowQuality}>
                查看数据质量 →
              </a>
            </div>
          </div>
        );
      }

      case 'quality':
        return (
          <DataQualityDashboard
            refreshTrigger={Date.now()}
          />
        );

      default:
        return null;
    }
  };

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <Router>
        <Layout
          title={pageInfo.title}
          breadcrumb={pageInfo.breadcrumb}
          loading={loading && currentView === 'query'}
        >
          <Routes>
            <Route path="/" element={renderContent()} />
            <Route path="/query" element={
              <QueryForm onQuery={handleQuery} loading={loading} />
            } />
            <Route path="/results" element={
              queryResult ? renderContent() : <Navigate to="/" />
            } />
            <Route path="/quality" element={<DataQualityDashboard />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;
