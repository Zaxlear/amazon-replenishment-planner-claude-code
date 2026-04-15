import React from 'react';
import { Table, Tag, Tooltip } from 'antd';
import { WarningOutlined } from '@ant-design/icons';
import type { DailyCalculationResult } from '../../types/sales';
import { formatNumber } from '../../utils/formatting';

interface Props {
  data: DailyCalculationResult[];
  onOverrideClick?: (date: string, openingStock: number) => void;
}

const DailyInventoryTable: React.FC<Props> = ({ data, onOverrideClick }) => {
  const columns = [
    {
      title: '日期',
      dataIndex: 'date',
      width: 100,
      fixed: 'left' as const,
    },
    {
      title: '期初库存',
      dataIndex: 'opening_stock',
      render: (v: number, record: DailyCalculationResult) => (
        <span
          style={{
            cursor: onOverrideClick ? 'pointer' : 'default',
            color: record.has_override ? '#1890ff' : undefined,
            background: record.has_override ? '#e6f7ff' : undefined,
            padding: '2px 6px',
            borderRadius: 4,
          }}
          onClick={() => onOverrideClick?.(record.date, v)}
        >
          {formatNumber(v)}
          {record.has_override && (
            <Tooltip title="已校正">
              <span style={{ marginLeft: 4, fontSize: 10 }}>校</span>
            </Tooltip>
          )}
        </span>
      ),
    },
    {
      title: '到货量',
      dataIndex: 'arrivals',
      render: (v: number, record: DailyCalculationResult) => {
        if (v === 0) return '-';
        const details = record.arrival_details.map((d) => `${d.unit_label}: ${d.quantity}`).join(', ');
        return <Tooltip title={details}><Tag color="green">+{formatNumber(v)}</Tag></Tooltip>;
      },
    },
    {
      title: '可用库存',
      dataIndex: 'available_stock',
      render: (v: number) => formatNumber(v),
    },
    {
      title: '规划销量',
      dataIndex: 'planned_sales',
      render: (v: number) => formatNumber(v),
    },
    {
      title: '实际消耗',
      dataIndex: 'actual_sales',
      render: (v: number, record: DailyCalculationResult) => (
        <span style={{ color: v < record.planned_sales ? '#f5222d' : undefined }}>
          {formatNumber(v)}
        </span>
      ),
    },
    {
      title: '期末库存',
      dataIndex: 'closing_stock',
      render: (v: number) => formatNumber(v),
    },
    {
      title: '断货',
      dataIndex: 'is_stockout',
      width: 60,
      render: (v: boolean) =>
        v ? (
          <Tag color="red" icon={<WarningOutlined />}>断货</Tag>
        ) : null,
    },
  ];

  return (
    <Table
      dataSource={data.map((d) => ({ ...d, key: d.date }))}
      columns={columns}
      pagination={{ pageSize: 15, showSizeChanger: true, pageSizeOptions: ['15', '30', '60'] }}
      size="small"
      scroll={{ x: 800 }}
      rowClassName={(record) => (record.is_stockout ? 'stockout-row' : '')}
    />
  );
};

export default DailyInventoryTable;
