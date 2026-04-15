import React from 'react';
import { Card, InputNumber, Button, Space, Popconfirm } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import SaturdayDatePicker from './SaturdayDatePicker';
import type { ShipmentBatchInput, WarehouseConfigInput } from '../../types/shipment';
import { regionLabel } from '../../utils/dateUtils';

interface Props {
  batches: ShipmentBatchInput[];
  warehouseConfig: WarehouseConfigInput;
  onChange: (batches: ShipmentBatchInput[]) => void;
}

const calcUnitQty = (batchQty: number, pct: number) => Math.round((batchQty * pct) / 100);

const BatchManager: React.FC<Props> = ({ batches, warehouseConfig, onChange }) => {
  const addBatch = () => {
    const lastDate = batches.length > 0 ? batches[batches.length - 1].ship_date : null;
    const nextDate = lastDate
      ? dayjs(lastDate).add(7, 'day').format('YYYY-MM-DD')
      : dayjs().day(6).format('YYYY-MM-DD');

    onChange([
      ...batches,
      {
        batch_index: batches.length + 1,
        ship_date: nextDate,
        batch_quantity: batches.length > 0 ? batches[batches.length - 1].batch_quantity : 1000,
      },
    ]);
  };

  const removeBatch = (index: number) => {
    const updated = batches
      .filter((_, i) => i !== index)
      .map((b, i) => ({ ...b, batch_index: i + 1 }));
    onChange(updated);
  };

  const updateBatch = (index: number, field: keyof ShipmentBatchInput, value: unknown) => {
    const updated = [...batches];
    updated[index] = { ...updated[index], [field]: value };
    onChange(updated);
  };

  const regions: { key: 'west' | 'central' | 'east'; label: string }[] = [
    { key: 'west', label: '美西' },
    { key: 'central', label: '美中' },
    { key: 'east', label: '美东' },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <span style={{ fontWeight: 'bold' }}>发货批次 ({batches.length}批)</span>
        <Button type="primary" icon={<PlusOutlined />} onClick={addBatch} size="small">
          新增批次
        </Button>
      </Space>

      {batches.map((batch, idx) => (
        <Card
          key={idx}
          size="small"
          title={`批次 ${batch.batch_index}`}
          extra={
            <Popconfirm title="确认删除此批次?" onConfirm={() => removeBatch(idx)}>
              <Button danger size="small" icon={<DeleteOutlined />} />
            </Popconfirm>
          }
          style={{ marginBottom: 12 }}
        >
          <Space wrap>
            <div>
              <div style={{ marginBottom: 4, fontSize: 12, color: '#666' }}>发货日期</div>
              <SaturdayDatePicker
                value={batch.ship_date}
                onChange={(date) => updateBatch(idx, 'ship_date', date)}
              />
            </div>
            <div>
              <div style={{ marginBottom: 4, fontSize: 12, color: '#666' }}>数量</div>
              <InputNumber
                min={1}
                value={batch.batch_quantity}
                onChange={(v) => updateBatch(idx, 'batch_quantity', v || 0)}
                style={{ width: 120 }}
              />
            </div>
          </Space>
          <div style={{ marginTop: 12, padding: 8, background: '#fafafa', borderRadius: 4 }}>
            {regions.map((r) => {
              const qty = calcUnitQty(batch.batch_quantity, warehouseConfig[r.key].allocation_pct);
              const arrivalDate = dayjs(batch.ship_date)
                .add(warehouseConfig[r.key].transit_days, 'day')
                .format('MM/DD');
              return (
                <div key={r.key} style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 0' }}>
                  <span>{r.label}: {qty}件</span>
                  <span style={{ color: '#999' }}>预计到货 {arrivalDate}</span>
                </div>
              );
            })}
          </div>
        </Card>
      ))}
    </div>
  );
};

export default BatchManager;
