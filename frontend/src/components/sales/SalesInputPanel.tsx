import React, { useState } from 'react';
import { Tabs, DatePicker, InputNumber, Button, Table, Space, message } from 'antd';
import dayjs from 'dayjs';
import type { DailySalesInput, DailySalesBatchInput } from '../../types/sales';

const { RangePicker } = DatePicker;

interface Props {
  planId: number;
  startDate: string;
  endDate: string;
  onEntriesAdded: () => void;
  addEntries: (planId: number, entries: DailySalesInput[]) => Promise<void>;
  batchSetSales: (planId: number, data: DailySalesBatchInput) => Promise<void>;
}

const SalesInputPanel: React.FC<Props> = ({
  planId, startDate, endDate, onEntriesAdded, addEntries, batchSetSales,
}) => {
  // Batch input state
  const [batchRange, setBatchRange] = useState<[string, string]>([startDate, endDate]);
  const [batchSales, setBatchSales] = useState<number>(50);
  const [batchLoading, setBatchLoading] = useState(false);

  // Single entry state
  const [singleEntries, setSingleEntries] = useState<DailySalesInput[]>([
    { entry_date: startDate, planned_sales: 50 },
  ]);

  const handleBatchSubmit = async () => {
    setBatchLoading(true);
    try {
      await batchSetSales(planId, {
        start_date: batchRange[0],
        end_date: batchRange[1],
        daily_sales: batchSales,
      });
      message.success('批量设置成功');
      onEntriesAdded();
    } catch (e: any) {
      message.error(e.response?.data?.detail || '设置失败');
    } finally {
      setBatchLoading(false);
    }
  };

  const handleSingleSubmit = async () => {
    try {
      await addEntries(planId, singleEntries);
      message.success('添加成功');
      onEntriesAdded();
    } catch (e: any) {
      message.error(e.response?.data?.detail || '添加失败');
    }
  };

  const addRow = () => {
    const last = singleEntries[singleEntries.length - 1];
    const nextDate = dayjs(last?.entry_date || startDate).add(1, 'day').format('YYYY-MM-DD');
    setSingleEntries([...singleEntries, { entry_date: nextDate, planned_sales: last?.planned_sales || 50 }]);
  };

  const updateRow = (idx: number, field: keyof DailySalesInput, value: unknown) => {
    const updated = [...singleEntries];
    updated[idx] = { ...updated[idx], [field]: value };
    setSingleEntries(updated);
  };

  return (
    <Tabs
      items={[
        {
          key: 'batch',
          label: '批量输入',
          children: (
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <div style={{ marginBottom: 4 }}>日期范围</div>
                <RangePicker
                  value={[dayjs(batchRange[0]), dayjs(batchRange[1])]}
                  onChange={(dates) => {
                    if (dates) {
                      setBatchRange([
                        dates[0]!.format('YYYY-MM-DD'),
                        dates[1]!.format('YYYY-MM-DD'),
                      ]);
                    }
                  }}
                />
              </div>
              <div>
                <div style={{ marginBottom: 4 }}>每日销量</div>
                <InputNumber min={0} value={batchSales} onChange={(v) => setBatchSales(v || 0)} />
              </div>
              <Button type="primary" onClick={handleBatchSubmit} loading={batchLoading}>
                应用到选定日期范围
              </Button>
            </Space>
          ),
        },
        {
          key: 'single',
          label: '逐日输入',
          children: (
            <div>
              <Table
                dataSource={singleEntries.map((e, i) => ({ ...e, key: i }))}
                columns={[
                  {
                    title: '日期',
                    dataIndex: 'entry_date',
                    render: (v: string, _: unknown, idx: number) => (
                      <DatePicker
                        value={dayjs(v)}
                        onChange={(d) => d && updateRow(idx, 'entry_date', d.format('YYYY-MM-DD'))}
                        size="small"
                      />
                    ),
                  },
                  {
                    title: '规划销量',
                    dataIndex: 'planned_sales',
                    render: (v: number, _: unknown, idx: number) => (
                      <InputNumber
                        min={0}
                        value={v}
                        onChange={(val) => updateRow(idx, 'planned_sales', val || 0)}
                        size="small"
                      />
                    ),
                  },
                ]}
                pagination={false}
                size="small"
              />
              <Space style={{ marginTop: 8 }}>
                <Button size="small" onClick={addRow}>添加一行</Button>
                <Button type="primary" size="small" onClick={handleSingleSubmit}>提交</Button>
              </Space>
            </div>
          ),
        },
      ]}
    />
  );
};

export default SalesInputPanel;
