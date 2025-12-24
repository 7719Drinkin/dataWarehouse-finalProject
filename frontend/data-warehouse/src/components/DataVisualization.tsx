import React, { useMemo } from 'react';
import {
  Line,
  LineChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Bar,
  BarChart,
} from 'recharts';
import { Card, Row, Col, Typography, Empty } from 'antd';
import type { Movie, ChartData } from '../types';

const { Title } = Typography;

interface DataVisualizationProps {
  data: Movie[];
  charts?: ChartData;
  title?: string;
}

const DataVisualization: React.FC<DataVisualizationProps> = ({
  data,
  title = "数据可视化"
}) => {
  // 时间序列数据（按年份统计）
  const timeSeriesData = useMemo(() => {
    const yearStats: Record<number, number> = {};

    data.forEach(movie => {
      if (movie.release_date) {
        try {
          const year = new Date(movie.release_date).getFullYear();
          yearStats[year] = (yearStats[year] || 0) + 1;
        } catch {
          // 忽略无效日期
        }
      }
    });

    return Object.entries(yearStats)
      .sort(([a], [b]) => Number(a) - Number(b))
      .map(([year, count]) => ({
        year: Number(year),
        count
      }));
  }, [data]);

  // 评分分布数据
  const ratingDistributionData = useMemo(() => {
    const ratingRanges = {
      '0-1': 0,
      '1-2': 0,
      '2-3': 0,
      '3-4': 0,
      '4-5': 0
    };

    data.forEach(movie => {
      const score = movie.avg_score;
      if (typeof score === 'number') {
        if (score < 1) ratingRanges['0-1']++;
        else if (score < 2) ratingRanges['1-2']++;
        else if (score < 3) ratingRanges['2-3']++;
        else if (score < 4) ratingRanges['3-4']++;
        else ratingRanges['4-5']++;
      }
    });

    return Object.entries(ratingRanges).map(([range, count]) => ({
      range,
      count,
      percentage: data.length > 0 ? (count / data.length * 100).toFixed(1) : '0'
    }));
  }, [data]);

  // 类型分布数据
  const genreDistributionData = useMemo(() => {
    const genreStats: Record<string, number> = {};

    data.forEach(movie => {
      if (movie.genres && Array.isArray(movie.genres)) {
        movie.genres.forEach(genre => {
          genreStats[genre] = (genreStats[genre] || 0) + 1;
        });
      }
    });

    return Object.entries(genreStats)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10) // 取前10个最常见的类型
      .map(([genre, count]) => ({
        genre,
        count,
        percentage: data.length > 0 ? (count / data.length * 100).toFixed(1) : '0'
      }));
  }, [data]);

  // 图表颜色
  const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'];

  if (data.length === 0) {
    return (
      <Card title={title}>
        <Empty description="暂无数据可供可视化" />
      </Card>
    );
  }

  return (
    <div style={{ width: '100%' }}>
      <Title level={4} style={{ marginBottom: 24 }}>{title}</Title>

      <Row gutter={[16, 16]}>
        {/* 时间序列图 */}
        <Col xs={24} lg={12}>
          <Card title={`电影上映年份分布 (${data.length} 部电影)`} bordered={false}>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="year"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value: number | string) => [value, '电影数量']}
                    labelFormatter={(label) => `${label}年`}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#1890ff"
                    strokeWidth={2}
                    name="电影数量"
                    dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* 评分分布饼图 */}
        <Col xs={24} lg={12}>
          <Card title="评分分布" bordered={false}>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={ratingDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ range, percentage }) => `${range}星: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {ratingDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => [value, '电影数量']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* 类型分布柱状图 */}
        <Col xs={24}>
          <Card title={`电影类型分布 (Top 10)`} bordered={false}>
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <BarChart data={genreDistributionData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="genre"
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(value: any) => [value, '电影数量']}
                  />
                  <Legend />
                  <Bar dataKey="count" fill="#52c41a" name="电影数量" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* 导演统计 */}
        <Col xs={24} md={12}>
          <Card title="导演统计" bordered={false}>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart
                  data={(() => {
                    const directorStats: Record<string, number> = {};
                    data.forEach(movie => {
                      if (movie.director) {
                        directorStats[movie.director] = (directorStats[movie.director] || 0) + 1;
                      }
                    });
                    return Object.entries(directorStats)
                      .sort(([, a], [, b]) => b - a)
                      .slice(0, 10)
                      .map(([director, count]) => ({ director, count }));
                  })()}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="director"
                    tick={{ fontSize: 10 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: any) => [value, '电影数量']} />
                  <Bar dataKey="count" fill="#722ed1" name="电影数量" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* 评论数量分布 */}
        <Col xs={24} md={12}>
          <Card title="评论数量分布" bordered={false}>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart
                  data={(() => {
                    const reviewRanges = {
                      '0-10': 0,
                      '11-50': 0,
                      '51-100': 0,
                      '101-500': 0,
                      '500+': 0
                    };

                    data.forEach(movie => {
                      const reviews = movie.review_count || 0;
                      if (reviews <= 10) reviewRanges['0-10']++;
                      else if (reviews <= 50) reviewRanges['11-50']++;
                      else if (reviews <= 100) reviewRanges['51-100']++;
                      else if (reviews <= 500) reviewRanges['101-500']++;
                      else reviewRanges['500+']++;
                    });

                    return Object.entries(reviewRanges).map(([range, count]) => ({
                      range,
                      count
                    }));
                  })()}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: any) => [value, '电影数量']} />
                  <Bar dataKey="count" fill="#fa8c16" name="电影数量" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DataVisualization;

