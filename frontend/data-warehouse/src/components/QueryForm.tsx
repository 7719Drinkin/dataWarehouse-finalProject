import React, { useState } from 'react';
import {
  Form,
  Input,
  Button,
  Select,
  InputNumber,
  Space,
  Card,
  Row,
  Col,
  Divider,
  Radio
} from 'antd';
import { SearchOutlined, ClearOutlined } from '@ant-design/icons';
import { QueryType } from '../types';
import type { QueryParams } from '../types';

const { Option } = Select;

interface QueryFormValues {
  year?: number;
  director?: string;
  actor?: string;
  role_type?: 'starring' | 'participated';
  genre?: string;
  min_score?: number;
  min_reviews?: number;
  min_collaborations?: number;
  limit?: number;
}

interface QueryFormProps {
  onQuery: (queryType: QueryType, params: QueryParams) => void;
  loading?: boolean;
}

const QueryForm: React.FC<QueryFormProps> = ({ onQuery, loading = false }) => {
  const [form] = Form.useForm();
  const [queryType, setQueryType] = useState<QueryType>(QueryType.MOVIES_BY_YEAR);

  const queryOptions = [
    { value: QueryType.MOVIES_BY_YEAR, label: '按年份查询电影' },
    { value: QueryType.MOVIES_BY_DIRECTOR, label: '按导演查询电影' },
    { value: QueryType.MOVIES_BY_ACTOR, label: '按演员查询电影' },
    { value: QueryType.MOVIES_BY_GENRE, label: '按电影类型查询统计' },
    { value: QueryType.HIGH_RATED_MOVIES, label: '查询高评分电影' },
    { value: QueryType.ACTOR_COLLABORATIONS, label: '查询演员合作关系' },
    { value: QueryType.DIRECTOR_ACTOR_COLLABORATIONS, label: '查询导演演员合作关系' },
    { value: QueryType.POPULAR_ACTOR_COMBINATIONS, label: '查询热门演员组合' },
  ];

  const handleQuery = (values: QueryFormValues) => {
    const params: QueryParams = {};

    switch (queryType) {
      case QueryType.MOVIES_BY_YEAR:
        params.year = values.year;
        break;
      case QueryType.MOVIES_BY_DIRECTOR:
        params.director = values.director;
        break;
      case QueryType.MOVIES_BY_ACTOR:
        params.actor = values.actor;
        params.role_type = values.role_type;
        break;
      case QueryType.MOVIES_BY_GENRE:
        params.genre = values.genre;
        break;
      case QueryType.HIGH_RATED_MOVIES:
        params.min_score = values.min_score;
        params.min_reviews = values.min_reviews;
        break;
      case QueryType.ACTOR_COLLABORATIONS:
        params.min_collaborations = values.min_collaborations;
        params.limit = values.limit;
        break;
      case QueryType.DIRECTOR_ACTOR_COLLABORATIONS:
        params.director = values.director;
        params.min_collaborations = values.min_collaborations;
        params.limit = values.limit;
        break;
      case QueryType.POPULAR_ACTOR_COMBINATIONS:
        params.genre = values.genre;
        break;
    }

    onQuery(queryType, params);
  };

  const handleReset = () => {
    form.resetFields();
  };

  const renderFormFields = () => {
    switch (queryType) {
      case QueryType.MOVIES_BY_YEAR:
        return (
          <Form.Item
            name="year"
            label="年份"
            rules={[{ required: true, message: '请选择年份' }]}
          >
            <InputNumber
              min={1900}
              max={2030}
              placeholder="输入年份，如 2020"
              style={{ width: '100%' }}
            />
          </Form.Item>
        );

      case QueryType.MOVIES_BY_DIRECTOR:
        return (
          <Form.Item
            name="director"
            label="导演姓名"
            rules={[{ required: true, message: '请输入导演姓名' }]}
          >
            <Input
              placeholder="输入导演姓名，如 Christopher Nolan"
              allowClear
            />
          </Form.Item>
        );

      case QueryType.MOVIES_BY_ACTOR:
        return (
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                name="actor"
                label="演员姓名"
                rules={[{ required: true, message: '请输入演员姓名' }]}
              >
                <Input
                  placeholder="输入演员姓名，如 Leonardo DiCaprio"
                  allowClear
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="role_type"
                label="角色类型"
                initialValue="starring"
              >
                <Radio.Group>
                  <Radio value="starring">主演</Radio>
                  <Radio value="participated">参演</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
          </Row>
        );

      case QueryType.MOVIES_BY_GENRE:
        return (
          <Form.Item
            name="genre"
            label="电影类型"
            rules={[{ required: true, message: '请选择电影类型' }]}
          >
            <Select placeholder="选择电影类型" allowClear>
              <Option value="Action">动作片</Option>
              <Option value="Adventure">冒险片</Option>
              <Option value="Comedy">喜剧片</Option>
              <Option value="Drama">剧情片</Option>
              <Option value="Horror">恐怖片</Option>
              <Option value="Romance">爱情片</Option>
              <Option value="Sci-Fi">科幻片</Option>
              <Option value="Thriller">惊悚片</Option>
              <Option value="Animation">动画片</Option>
              <Option value="Documentary">纪录片</Option>
            </Select>
          </Form.Item>
        );

      case QueryType.HIGH_RATED_MOVIES:
        return (
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="min_score"
                label="最低评分"
                initialValue={4.0}
              >
                <InputNumber
                  min={0}
                  max={5}
                  step={0.1}
                  placeholder="最低评分"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="min_reviews"
                label="最少评论数"
                initialValue={10}
              >
                <InputNumber
                  min={1}
                  placeholder="最少评论数"
                />
              </Form.Item>
            </Col>
          </Row>
        );

      case QueryType.ACTOR_COLLABORATIONS:
        return (
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="min_collaborations"
                label="最少合作次数"
                initialValue={2}
              >
                <InputNumber
                  min={1}
                  placeholder="最少合作次数"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="limit"
                label="返回数量限制"
                initialValue={20}
              >
                <InputNumber
                  min={1}
                  max={100}
                  placeholder="返回数量限制"
                />
              </Form.Item>
            </Col>
          </Row>
        );

      case QueryType.DIRECTOR_ACTOR_COLLABORATIONS:
        return (
          <>
            <Form.Item
              name="director"
              label="导演姓名"
              rules={[{ required: true, message: '请输入导演姓名' }]}
            >
              <Input
                placeholder="输入导演姓名"
                allowClear
              />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="min_collaborations"
                  label="最少合作次数"
                  initialValue={1}
                >
                  <InputNumber
                    min={1}
                    placeholder="最少合作次数"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="limit"
                  label="返回数量限制"
                  initialValue={10}
                >
                  <InputNumber
                    min={1}
                    max={50}
                    placeholder="返回数量限制"
                  />
                </Form.Item>
              </Col>
            </Row>
          </>
        );

      case QueryType.POPULAR_ACTOR_COMBINATIONS:
        return (
          <Form.Item
            name="genre"
            label="电影类型"
            rules={[{ required: true, message: '请选择电影类型' }]}
          >
            <Select placeholder="选择电影类型" allowClear>
              <Option value="Action">动作片</Option>
              <Option value="Adventure">冒险片</Option>
              <Option value="Comedy">喜剧片</Option>
              <Option value="Drama">剧情片</Option>
              <Option value="Crime">犯罪片</Option>
              <Option value="Thriller">惊悚片</Option>
            </Select>
          </Form.Item>
        );

      default:
        return null;
    }
  };

  return (
    <Card title="数据查询" bordered={false}>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleQuery}
        initialValues={{
          min_score: 4.0,
          min_reviews: 10,
          min_collaborations: 2,
          limit: 20,
          role_type: 'starring'
        }}
      >
        <Form.Item
          name="query_type"
          label="查询类型"
          rules={[{ required: true, message: '请选择查询类型' }]}
          initialValue={QueryType.MOVIES_BY_YEAR}
        >
          <Select
            placeholder="选择查询类型"
            onChange={(value) => setQueryType(value)}
          >
            {queryOptions.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Divider />

        {renderFormFields()}

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SearchOutlined />}
              loading={loading}
            >
              执行查询
            </Button>
            <Button
              icon={<ClearOutlined />}
              onClick={handleReset}
            >
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default QueryForm;

