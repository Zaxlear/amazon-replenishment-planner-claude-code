import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, InputNumber, Space, message,
  Popconfirm, Tag, Descriptions, Tabs, Spin,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { shipmentApi } from '../services/api';
import type {
  ShipmentPlanListItem, ShipmentPlanResponse, ShipmentPlanCreate,
  WarehouseConfigInput, ShipmentBatchInput,
} from '../types/shipment';
import WarehouseConfigPanel from '../components/shipment/WarehouseConfigPanel';
import BatchManager from '../components/shipment/BatchManager';
import ShipmentUnitPreview from '../components/shipment/ShipmentUnitPreview';

const defaultWarehouseConfig: WarehouseConfigInput = {
  west: { allocation_pct: 40, transit_days: 15 },
  central: { allocation_pct: 35, transit_days: 18 },
  east: { allocation_pct: 25, transit_days: 22 },
};

const ShipmentPlanPage: React.FC = () => {
  const [plans, setPlans] = useState<ShipmentPlanListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [viewPlan, setViewPlan] = useState<ShipmentPlanResponse | null>(null);
  const [form] = Form.useForm();
  const [warehouseConfig, setWarehouseConfig] = useState<WarehouseConfigInput>(defaultWarehouseConfig);
  const [batches, setBatches] = useState<ShipmentBatchInput[]>([]);

  const loadPlans = useCallback(async () => {
    setLoading(true);
    try {
      setPlans(await shipmentApi.list());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadPlans(); }, [loadPlans]);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      const data: ShipmentPlanCreate = {
        plan_name: values.plan_name,
        sku: values.sku,
        asin: values.asin,
        total_quantity: values.total_quantity,
        batch_count: batches.length,
        warehouse_config: warehouseConfig,
        batches,
        notes: values.notes,
      };
      await shipmentApi.create(data);
      message.success('发货计划创建成功');
      setCreateOpen(false);
      form.resetFields();
      setBatches([]);
      setWarehouseConfig(defaultWarehouseConfig);
      loadPlans();
    } catch (e: any) {
      message.error(e.response?.data?.detail || '创建失败');
    }
  };

  const handleDelete = async (id: number) => {
    await shipmentApi.delete(id);
    message.success('删除成功');
    loadPlans();
  };

  const viewDetail = async (id: number) => {
    const plan = await shipmentApi.get(id);
    setViewPlan(plan);
  };

  const statusMap: Record<string, { color: string; text: string }> = {
    draft: { color: 'default', text: '草稿' },
    confirmed: { color: 'blue', text: '已确认' },
    in_transit: { color: 'processing', text: '运输中' },
    completed: { color: 'success', text: '已完成' },
  };

  const columns = [
    { title: '计划名称', dataIndex: 'plan_name', key: 'plan_name' },
    { title: 'SKU', dataIndex: 'sku', key: 'sku' },
    { title: 'ASIN', dataIndex: 'asin', key: 'asin' },
    { title: '总数量', dataIndex: 'total_quantity', key: 'total_quantity' },
    { title: '批次数', dataIndex: 'batch_count', key: 'batch_count' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (v: string) => {
        const s = statusMap[v] || { color: 'default', text: v };
        return <Tag color={s.color}>{s.text}</Tag>;
      },
    },
    {
      title: '创建时间', dataIndex: 'created_at', key: 'created_at',
      render: (v: string) => dayjs(v).format('YYYY-MM-DD'),
    },
    {
      title: '操作', key: 'actions',
      render: (_: unknown, record: ShipmentPlanListItem) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />} onClick={() => viewDetail(record.id)}>
            查看
          </Button>
          <Popconfirm title="确认删除?" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const totalPct = warehouseConfig.west.allocation_pct + warehouseConfig.central.allocation_pct + warehouseConfig.east.allocation_pct;

  return (
    <div>
      <Card
        title="发货计划列表"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
            新建发货计划
          </Button>
        }
      >
        <Table
          dataSource={plans}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Create Modal */}
      <Modal
        title="新建发货计划"
        open={createOpen}
        onOk={handleCreate}
        onCancel={() => setCreateOpen(false)}
        width={800}
        okText="创建"
        cancelText="取消"
        okButtonProps={{ disabled: totalPct !== 100 || batches.length === 0 }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="plan_name" label="计划名称" rules={[{ required: true }]}>
            <Input placeholder="例: 2026年5月补货" />
          </Form.Item>
          <Space style={{ width: '100%' }}>
            <Form.Item name="sku" label="SKU">
              <Input placeholder="SKU 编码" />
            </Form.Item>
            <Form.Item name="asin" label="ASIN">
              <Input placeholder="ASIN 编码" />
            </Form.Item>
            <Form.Item name="total_quantity" label="总发货数量" rules={[{ required: true }]}>
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
          </Space>
          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>

        <Tabs
          items={[
            {
              key: 'warehouse',
              label: '仓库配置',
              children: <WarehouseConfigPanel value={warehouseConfig} onChange={setWarehouseConfig} />,
            },
            {
              key: 'batches',
              label: `批次管理 (${batches.length})`,
              children: <BatchManager batches={batches} warehouseConfig={warehouseConfig} onChange={setBatches} />,
            },
          ]}
        />
      </Modal>

      {/* View Detail Modal */}
      <Modal
        title={viewPlan?.plan_name}
        open={!!viewPlan}
        onCancel={() => setViewPlan(null)}
        footer={null}
        width={900}
      >
        {viewPlan && (
          <>
            <Descriptions size="small" column={2} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="SKU">{viewPlan.sku || '-'}</Descriptions.Item>
              <Descriptions.Item label="ASIN">{viewPlan.asin || '-'}</Descriptions.Item>
              <Descriptions.Item label="总数量">{viewPlan.total_quantity}</Descriptions.Item>
              <Descriptions.Item label="批次数">{viewPlan.batch_count}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={statusMap[viewPlan.status]?.color}>
                  {statusMap[viewPlan.status]?.text || viewPlan.status}
                </Tag>
              </Descriptions.Item>
            </Descriptions>
            <h4>货件明细</h4>
            <ShipmentUnitPreview batches={viewPlan.batches} />
          </>
        )}
      </Modal>
    </div>
  );
};

export default ShipmentPlanPage;
