import React from 'react';
import { Alert, Tag, Space } from 'antd';
import { WarningOutlined } from '@ant-design/icons';

interface Props {
  stockoutDates: string[];
  stockoutDays: number;
}

const StockoutWarning: React.FC<Props> = ({ stockoutDates, stockoutDays }) => {
  if (stockoutDays === 0) return null;

  return (
    <Alert
      type="error"
      icon={<WarningOutlined />}
      showIcon
      message={`断货预警: 共${stockoutDays}天断货`}
      description={
        <Space wrap>
          {stockoutDates.map((d) => (
            <Tag key={d} color="red">{d}</Tag>
          ))}
        </Space>
      }
      style={{ marginBottom: 16 }}
    />
  );
};

export default StockoutWarning;
