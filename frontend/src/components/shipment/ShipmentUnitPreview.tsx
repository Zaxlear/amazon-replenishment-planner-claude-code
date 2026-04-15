import React from 'react';
import { Table, Tag } from 'antd';
import dayjs from 'dayjs';
import type { ShipmentBatchResponse } from '../../types/shipment';
import { regionLabel } from '../../utils/dateUtils';

interface Props {
  batches: ShipmentBatchResponse[];
}

const regionColors: Record<string, string> = {
  west: 'blue',
  central: 'gold',
  east: 'red',
};

const ShipmentUnitPreview: React.FC<Props> = ({ batches }) => {
  const dataSource = batches.flatMap((batch) =>
    batch.units.map((unit) => ({
      key: unit.id,
      batchIndex: batch.batch_index,
      shipDate: batch.ship_date,
      region: unit.region,
      regionLabel: regionLabel(unit.region),
      quantity: unit.quantity,
      transitDays: unit.transit_days,
      arrivalDate: unit.arrival_date,
      status: unit.status,
    }))
  );

  const columns = [
    { title: '批次', dataIndex: 'batchIndex', width: 60 },
    { title: '发货日', dataIndex: 'shipDate', render: (v: string) => dayjs(v).format('MM/DD') },
    {
      title: '仓库',
      dataIndex: 'region',
      render: (_: string, record: (typeof dataSource)[0]) => (
        <Tag color={regionColors[record.region]}>{record.regionLabel}</Tag>
      ),
    },
    { title: '数量', dataIndex: 'quantity' },
    { title: '时效', dataIndex: 'transitDays', render: (v: number) => `${v}天` },
    { title: '到货日', dataIndex: 'arrivalDate', render: (v: string) => dayjs(v).format('MM/DD') },
    {
      title: '状态',
      dataIndex: 'status',
      render: (v: string) => {
        const map: Record<string, { color: string; text: string }> = {
          pending: { color: 'default', text: '待发货' },
          shipped: { color: 'processing', text: '运输中' },
          arrived: { color: 'success', text: '已到货' },
        };
        const s = map[v] || { color: 'default', text: v };
        return <Tag color={s.color}>{s.text}</Tag>;
      },
    },
  ];

  return (
    <Table
      dataSource={dataSource}
      columns={columns}
      pagination={false}
      size="small"
      scroll={{ x: 600 }}
    />
  );
};

export default ShipmentUnitPreview;
