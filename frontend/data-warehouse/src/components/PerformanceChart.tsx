import React, { useMemo } from 'react';
import {
  Bar,
  BarChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { Card, Statistic, Row, Col, Progress, Typography, Space } from 'antd';
import {
  TrophyOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import type { DatabaseResults, PerformanceStats } from '../types';
import { formatExecutionTime, formatDatabaseName, getPerformanceLevel } from '../utils/formatters';

const { Title, Text } = Typography;

interface PerformanceChartProps {
  results: DatabaseResults;
  stats: PerformanceStats;
  totalTime: number;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({
  results,
  stats,
  totalTime
}) => {
  // 准备图表数据
  const chartData = useMemo(() => {
    return Object.entries(results).map(([dbName, result]) => ({
      database: formatDatabaseName(dbName),
      time: Number(result.execution_time.toFixed(4)),
      success: result.success,
      resultCount: result.result?.length || 0
    }));
  }, [results]);

  // 图表颜色
  const colors = ['#1890ff', '#52c41a', '#faad14'];

  // 性能等级
  const performanceLevel = getPerformanceLevel(stats.performance_ratio);

  return (
    <div style={{ width: '100%' }}>
      {/* 性能统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="最快数据库"
              value={formatDatabaseName(stats.fastest_database)}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="性能倍数"
              value={stats.performance_ratio}
              suffix="x"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: performanceLevel.color }}
              precision={2}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总执行时间"
              value={totalTime}
              suffix="秒"
              prefix={<ClockCircleOutlined />}
              precision={3}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="成功率"
              value={stats.successful_queries}
              suffix={`/ ${stats.total_queries}`}
              prefix={<CheckCircleOutlined />}
              valueStyle={{
                color: stats.success_rate === 1 ? '#52c41a' : '#faad14'
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 性能等级指示器 */}
      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Title level={4}>性能等级</Title>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Progress
              type="circle"
              percent={Math.min(stats.performance_ratio * 20, 100)}
              format={() => performanceLevel.level}
              strokeColor={performanceLevel.color}
              width={80}
            />
            <div>
              <Text strong style={{ fontSize: 16 }}>
                {performanceLevel.level}
              </Text>
              <br />
              <Text type="secondary">
                最慢数据库比最快数据库慢 {stats.performance_ratio.toFixed(2)} 倍
              </Text>
            </div>
          </div>
        </Space>
      </Card>

      {/* 执行时间对比图表 */}
      <Card title="数据库查询性能对比" bordered={false}>
        <div style={{ width: '100%', height: 400 }}>
          <ResponsiveContainer>
            <BarChart
              data={chartData}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="database"
                tick={{ fontSize: 12 }}
              />
              <YAxis
                label={{
                  value: '执行时间 (秒)',
                  angle: -90,
                  position: 'insideLeft'
                }}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                formatter={(value: any, name: string) => [
                  `${Number(value).toFixed(4)} 秒`,
                  '执行时间'
                ]}
                labelFormatter={(label) => `${label}`}
              />
              <Legend />
              <Bar
                dataKey="time"
                name="执行时间"
                radius={[4, 4, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.success ? colors[index % colors.length] : '#ff4d4f'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* 详细结果表格 */}
      <Card title="详细执行结果" style={{ marginTop: 16 }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#fafafa' }}>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #f0f0f0' }}>
                  数据库
                </th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #f0f0f0' }}>
                  执行时间
                </th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #f0f0f0' }}>
                  状态
                </th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #f0f0f0' }}>
                  结果数量
                </th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #f0f0f0' }}>
                  错误信息
                </th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(results).map(([dbName, result]) => (
                <tr key={dbName}>
                  <td style={{ padding: '12px', border: '1px solid #f0f0f0' }}>
                    {formatDatabaseName(dbName)}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #f0f0f0' }}>
                    {formatExecutionTime(result.execution_time)}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #f0f0f0' }}>
                    <span style={{
                      color: result.success ? '#52c41a' : '#ff4d4f',
                      fontWeight: 'bold'
                    }}>
                      {result.success ? '成功' : '失败'}
                    </span>
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #f0f0f0' }}>
                    {result.result?.length || 0}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #f0f0f0' }}>
                    <Text
                      ellipsis={{ tooltip: result.error }}
                      style={{ maxWidth: 200 }}
                    >
                      {result.error || '-'}
                    </Text>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default PerformanceChart;

