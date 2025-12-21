import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Progress,
  Statistic,
  Table,
  Typography,
  Space,
  Tag,
  Alert,
  Spin,
  Tabs,
  List
} from 'antd';
import {
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  DatabaseOutlined,
  ExperimentOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import type { DataQualityReport, DataLineageReport } from '../types';
import ApiService from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface DataQualityDashboardProps {
  refreshTrigger?: number;
}

const DataQualityDashboard: React.FC<DataQualityDashboardProps> = ({
  refreshTrigger
}) => {
  const [qualityReport, setQualityReport] = useState<DataQualityReport | null>(null);
  const [lineageReport, setLineageReport] = useState<DataLineageReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [qualityData, lineageData] = await Promise.all([
        ApiService.getDataQuality(),
        ApiService.getDataLineage()
      ]);

      setQualityReport(qualityData);
      setLineageReport(lineageData);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.9) return '#52c41a';
    if (score >= 0.7) return '#faad14';
    return '#ff4d4f';
  };

  const getQualityStatus = (score: number) => {
    if (score >= 0.9) return { icon: <CheckCircleOutlined />, text: '优秀' };
    if (score >= 0.7) return { icon: <WarningOutlined />, text: '良好' };
    return { icon: <CloseCircleOutlined />, text: '需要改进' };
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载数据质量报告...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
        action={
          <a onClick={loadData}>重试</a>
        }
      />
    );
  }

  if (!qualityReport || !lineageReport) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 50 }}>
          <InfoCircleOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
          <div style={{ marginTop: 16, color: '#8c8c8c' }}>暂无数据质量报告</div>
        </div>
      </Card>
    );
  }

  const quality = qualityReport.quality_metrics;
  const source = qualityReport.source_analysis;
  const anomalies = qualityReport.anomaly_detection;

  return (
    <div style={{ width: '100%' }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        <ExperimentOutlined style={{ marginRight: 12 }} />
        数据治理仪表板
      </Title>

      <Tabs defaultActiveKey="quality" type="card">
        {/* 数据质量标签页 */}
        <TabPane
          tab={
            <span>
              <CheckCircleOutlined />
              数据质量
            </span>
          }
          key="quality"
        >
          <Row gutter={[16, 16]}>
            {/* 整体质量评分 */}
            <Col xs={24} md={8}>
              <Card>
                <Statistic
                  title="整体质量评分"
                  value={quality.quality_score}
                  precision={3}
                  suffix="/ 1.0"
                  valueStyle={{
                    color: getQualityColor(quality.quality_score)
                  }}
                  prefix={getQualityStatus(quality.quality_score).icon}
                />
                <div style={{ marginTop: 16 }}>
                  <Text type="secondary">
                    {getQualityStatus(quality.quality_score).text}
                  </Text>
                </div>
              </Card>
            </Col>

            {/* 完整性 */}
            <Col xs={24} md={8}>
              <Card>
                <Statistic
                  title="数据完整性"
                  value={quality.completeness.overall}
                  precision={3}
                  suffix="/ 1.0"
                  valueStyle={{
                    color: getQualityColor(quality.completeness.overall)
                  }}
                />
                <Progress
                  percent={Math.round(quality.completeness.overall * 100)}
                  status={quality.completeness.overall >= 0.8 ? 'success' : 'normal'}
                  size="small"
                  style={{ marginTop: 8 }}
                />
              </Card>
            </Col>

            {/* 唯一性 */}
            <Col xs={24} md={8}>
              <Card>
                <Statistic
                  title="数据唯一性"
                  value={quality.uniqueness}
                  precision={3}
                  suffix="/ 1.0"
                  valueStyle={{
                    color: getQualityColor(quality.uniqueness)
                  }}
                />
                <Progress
                  percent={Math.round(quality.uniqueness * 100)}
                  status={quality.uniqueness >= 0.95 ? 'success' : 'normal'}
                  size="small"
                  style={{ marginTop: 8 }}
                />
              </Card>
            </Col>

            {/* 字段完整性详情 */}
            <Col xs={24}>
              <Card title="字段完整性详情" bordered={false}>
                <Table
                  dataSource={Object.entries(quality.completeness.by_field).map(([field, score]) => ({
                    field,
                    completeness: score,
                    status: score >= 0.8 ? '良好' : score >= 0.5 ? '一般' : '较差'
                  }))}
                  columns={[
                    {
                      title: '字段名',
                      dataIndex: 'field',
                      key: 'field'
                    },
                    {
                      title: '完整性',
                      dataIndex: 'completeness',
                      key: 'completeness',
                      render: (value: number) => (
                        <Progress
                          percent={Math.round(value * 100)}
                          size="small"
                          status={value >= 0.8 ? 'success' : 'normal'}
                        />
                      )
                    },
                    {
                      title: '状态',
                      dataIndex: 'status',
                      key: 'status',
                      render: (status: string) => {
                        const color = status === '良好' ? 'green' : status === '一般' ? 'orange' : 'red';
                        return <Tag color={color}>{status}</Tag>;
                      }
                    }
                  ]}
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>

            {/* 数据异常检测 */}
            <Col xs={24}>
              <Card title="数据异常检测" bordered={false}>
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={6}>
                    <Statistic
                      title="总异常数"
                      value={anomalies.total_anomalies}
                      valueStyle={{
                        color: anomalies.total_anomalies > 0 ? '#ff4d4f' : '#52c41a'
                      }}
                    />
                  </Col>
                  <Col xs={24} sm={6}>
                    <Statistic
                      title="缺失关键字段"
                      value={anomalies.anomalies_by_type.missing_critical_fields}
                    />
                  </Col>
                  <Col xs={24} sm={6}>
                    <Statistic
                      title="无效评分"
                      value={anomalies.anomalies_by_type.invalid_ratings}
                    />
                  </Col>
                  <Col xs={24} sm={6}>
                    <Statistic
                      title="重复记录"
                      value={anomalies.anomalies_by_type.duplicate_records}
                    />
                  </Col>
                </Row>
              </Card>
            </Col>

            {/* 数据源分析 */}
            <Col xs={24}>
              <Card title="数据源分布" bordered={false}>
                <Row gutter={[16, 16]}>
                  <Col xs={24} md={12}>
                    <Statistic
                      title="数据源数量"
                      value={source.total_sources}
                      prefix={<DatabaseOutlined />}
                    />
                  </Col>
                  <Col xs={24} md={12}>
                    <Statistic
                      title="源文件数量"
                      value={source.total_source_files}
                      prefix={<FileTextOutlined />}
                    />
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 数据血缘标签页 */}
        <TabPane
          tab={
            <span>
              <FileTextOutlined />
              数据血缘
            </span>
          }
          key="lineage"
        >
          <Row gutter={[16, 16]}>
            <Col xs={24}>
              <Card title="数据流向" bordered={false}>
                <div style={{ padding: 20 }}>
                  <Title level={4}>数据处理流程</Title>
                  <div style={{ marginTop: 16 }}>
                    {lineageReport.data_flow.raw_data_sources.map((source, index) => (
                      <div key={index} style={{ marginBottom: 8 }}>
                        <Tag color="blue">原始数据</Tag>
                        <Text style={{ marginLeft: 8 }}>{source}</Text>
                      </div>
                    ))}

                    <div style={{ margin: '16px 0', textAlign: 'center' }}>
                      <Text type="secondary">↓ ETL处理 ↓</Text>
                    </div>

                    {lineageReport.data_flow.processing_steps.map((step, index) => (
                      <div key={index} style={{ marginBottom: 8 }}>
                        <Tag color="green">处理步骤</Tag>
                        <Text style={{ marginLeft: 8 }}>{step}</Text>
                      </div>
                    ))}

                    <div style={{ margin: '16px 0', textAlign: 'center' }}>
                      <Text type="secondary">↓ 存储到 ↓</Text>
                    </div>

                    {lineageReport.data_flow.target_systems.map((system, index) => (
                      <div key={index} style={{ marginBottom: 8 }}>
                        <Tag color="purple">目标系统</Tag>
                        <Text style={{ marginLeft: 8 }}>{system}</Text>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </Col>

            <Col xs={24}>
              <Card title="溯源统计" bordered={false}>
                <Row gutter={[16, 16]}>
                  <Col xs={24} md={6}>
                    <Statistic
                      title="处理的总电影数"
                      value={lineageReport.lineage_stats.total_movies_processed || 0}
                      groupSeparator=","
                    />
                  </Col>
                  <Col xs={24} md={6}>
                    <Statistic
                      title="过滤的非电影数据"
                      value={lineageReport.lineage_stats.non_movie_data_filtered || 0}
                      groupSeparator=","
                    />
                  </Col>
                  <Col xs={24} md={6}>
                    <Statistic
                      title="哈利波特系列电影"
                      value={lineageReport.lineage_stats.harry_potter_movies || 0}
                    />
                  </Col>
                  <Col xs={24} md={6}>
                    <Statistic
                      title="哈利波特版本数"
                      value={lineageReport.lineage_stats.harry_potter_versions || 0}
                    />
                  </Col>
                </Row>
              </Card>
            </Col>

            <Col xs={24}>
              <Card title="数据质量门禁" bordered={false}>
                <List
                  dataSource={lineageReport.data_quality_gates}
                  renderItem={(item, index) => (  // eslint-disable-line @typescript-eslint/no-unused-vars
                    <List.Item>
                      <Space>
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                        <Text>{item}</Text>
                      </Space>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 改进建议标签页 */}
        <TabPane
          tab={
            <span>
              <WarningOutlined />
              改进建议
            </span>
          }
          key="recommendations"
        >
          <Card title="数据质量改进建议" bordered={false}>
            <List
              dataSource={qualityReport.recommendations}
              renderItem={(recommendation, index) => (
                <List.Item>
                  <Space align="start">
                    <WarningOutlined style={{ color: '#faad14', marginTop: 4 }} />
                    <div>
                      <Text strong>建议 {index + 1}:</Text>
                      <Paragraph style={{ margin: '8px 0 0 0' }}>
                        {recommendation}
                      </Paragraph>
                    </div>
                  </Space>
                </List.Item>
              )}
            />

            {qualityReport.recommendations.length === 0 && (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
                <Title level={4}>数据质量良好</Title>
                <Text type="secondary">当前数据质量已达到标准，无需额外改进</Text>
              </div>
            )}
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default DataQualityDashboard;

