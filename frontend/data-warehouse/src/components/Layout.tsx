import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Breadcrumb, Typography, Space, Button, Spin } from 'antd';
import {
  DatabaseOutlined,
  BarChartOutlined,
  SettingOutlined,
  ExperimentOutlined,
  DashboardOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  breadcrumb?: string[];
  loading?: boolean;
}

const StyledLayout = styled(AntLayout)`
  min-height: 100vh;
`;

const StyledHeader = styled(Header)`
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
`;

const StyledSider = styled(Sider)`
  background: #fff;
  border-right: 1px solid #f0f0f0;
`;

const StyledContent = styled(Content)`
  margin: 24px 16px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  min-height: 280px;
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Logo = styled.div`
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #1890ff, #52c41a);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
`;

const menuItems = [
  {
    key: 'query',
    icon: <DatabaseOutlined />,
    label: '数据查询',
    children: [
      { key: 'movies-by-year', label: '按年份查询' },
      { key: 'movies-by-director', label: '按导演查询' },
      { key: 'movies-by-actor', label: '按演员查询' },
      { key: 'movies-by-genre', label: '按类型查询' },
      { key: 'high-rated', label: '高评分电影' },
      { key: 'collaborations', label: '合作关系查询' },
    ]
  },
  {
    key: 'analytics',
    icon: <BarChartOutlined />,
    label: '数据分析',
    children: [
      { key: 'performance', label: '性能对比' },
      { key: 'visualization', label: '数据可视化' },
    ]
  },
  {
    key: 'governance',
    icon: <ExperimentOutlined />,
    label: '数据治理',
    children: [
      { key: 'quality', label: '数据质量' },
      { key: 'lineage', label: '数据血缘' },
    ]
  },
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: '仪表板'
  }
];

const AppLayout: React.FC<LayoutProps> = ({
  children,
  title = '电影数据仓库',
  breadcrumb = [],
  loading = false
}) => {
  const [collapsed, setCollapsed] = useState(false);

  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };

  return (
    <StyledLayout>
      <StyledSider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={260}
        trigger={null}
      >
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #f0f0f0' }}>
          <LogoContainer>
            <Logo>DW</Logo>
            {!collapsed && (
              <div>
                <Title level={5} style={{ margin: 0, color: '#262626' }}>
                  电影数据仓库
                </Title>
                <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                  Movie Data Warehouse
                </div>
              </div>
            )}
          </LogoContainer>
        </div>

        <Menu
          mode="inline"
          defaultSelectedKeys={['dashboard']}
          defaultOpenKeys={['query']}
          style={{ height: '100%', borderRight: 0 }}
          items={menuItems}
        />
      </StyledSider>

      <AntLayout>
        <StyledHeader>
          <Space>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={toggleCollapsed}
              style={{ fontSize: '16px', width: 64, height: 64 }}
            />
            <Breadcrumb style={{ margin: '16px 0' }}>
              <Breadcrumb.Item>
                <DatabaseOutlined style={{ marginRight: 8 }} />
                电影数据仓库
              </Breadcrumb.Item>
              {breadcrumb.map((item, index) => (
                <Breadcrumb.Item key={index}>{item}</Breadcrumb.Item>
              ))}
            </Breadcrumb>
          </Space>

          <Space>
            <Button icon={<SettingOutlined />} type="text">
              设置
            </Button>
          </Space>
        </StyledHeader>

        <StyledContent>
          {title && (
            <div style={{ marginBottom: 24 }}>
              <Title level={3} style={{ margin: 0 }}>
                {title}
              </Title>
            </div>
          )}

          {loading ? (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: 200
            }}>
              <Spin size="large" tip="加载中..." />
            </div>
          ) : (
            children
          )}
        </StyledContent>
      </AntLayout>
    </StyledLayout>
  );
};

export default AppLayout;

