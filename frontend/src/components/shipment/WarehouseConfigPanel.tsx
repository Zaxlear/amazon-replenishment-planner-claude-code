import React from 'react';
import { InputNumber, Alert, Table } from 'antd';
import type { WarehouseConfigInput, WarehouseConfigItem } from '../../types/shipment';

interface Props {
  value: WarehouseConfigInput;
  onChange: (config: WarehouseConfigInput) => void;
}

const regions: { key: 'west' | 'central' | 'east'; label: string; color: string }[] = [
  { key: 'west', label: '美西', color: '#1890ff' },
  { key: 'central', label: '美中', color: '#faad14' },
  { key: 'east', label: '美东', color: '#f5222d' },
];

const WarehouseConfigPanel: React.FC<Props> = ({ value, onChange }) => {
  const totalPct =
    (value.west.allocation_pct || 0) +
    (value.central.allocation_pct || 0) +
    (value.east.allocation_pct || 0);

  const isValid = totalPct === 100;

  const handleChange = (
    region: 'west' | 'central' | 'east',
    field: keyof WarehouseConfigItem,
    val: number | null
  ) => {
    onChange({
      ...value,
      [region]: { ...value[region], [field]: val || 0 },
    });
  };

  const columns = [
    {
      title: '仓库',
      dataIndex: 'label',
      render: (text: string, record: (typeof regions)[0]) => (
        <span style={{ color: record.color, fontWeight: 'bold' }}>{text}</span>
      ),
    },
    {
      title: '分配比例 (%)',
      dataIndex: 'key',
      render: (key: 'west' | 'central' | 'east') => (
        <InputNumber
          min={0}
          max={100}
          value={value[key].allocation_pct}
          onChange={(v) => handleChange(key, 'allocation_pct', v)}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: '物流时效 (天)',
      dataIndex: 'key',
      key: 'transit',
      render: (key: 'west' | 'central' | 'east') => (
        <InputNumber
          min={1}
          max={90}
          value={value[key].transit_days}
          onChange={(v) => handleChange(key, 'transit_days', v)}
          style={{ width: '100%' }}
        />
      ),
    },
  ];

  return (
    <div>
      <Table
        dataSource={regions}
        columns={columns}
        rowKey="key"
        pagination={false}
        size="small"
        footer={() => (
          <div style={{ textAlign: 'right' }}>
            合计: <strong style={{ color: isValid ? '#52c41a' : '#f5222d' }}>{totalPct}%</strong>
          </div>
        )}
      />
      {!isValid && (
        <Alert
          type="error"
          message={`分配比例之和必须为100%，当前为${totalPct}%`}
          showIcon
          style={{ marginTop: 8 }}
        />
      )}
    </div>
  );
};

export default WarehouseConfigPanel;
