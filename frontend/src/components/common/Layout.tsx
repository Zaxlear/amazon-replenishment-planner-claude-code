import React from 'react';
import { Layout, Menu } from 'antd';
import {
  SendOutlined,
  BarChartOutlined,
  LineChartOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';

const { Sider, Content, Header } = Layout;

const menuItems = [
  { key: '/shipments', icon: <SendOutlined />, label: '发货规划' },
  { key: '/sales', icon: <BarChartOutlined />, label: '销售/库存规划' },
  { key: '/charts', icon: <LineChartOutlined />, label: '图表面板' },
  { key: '/turnover', icon: <SyncOutlined />, label: '周转分析' },
];

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const selectedKey = menuItems.find((item) =>
    location.pathname.startsWith(item.key)
  )?.key || '/shipments';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} theme="light" breakpoint="lg" collapsedWidth={60}>
        <div style={{ height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: 16 }}>
          FBA 补货规划
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <h3 style={{ margin: 0, lineHeight: '64px' }}>
            Amazon 补货与销售规划系统
          </h3>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
