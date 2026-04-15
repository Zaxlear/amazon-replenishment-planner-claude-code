import React, { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Select,
  Space, message, Popconfirm, Descriptions, Spin, Statistic, Row, Col,
} from 'antd';
import { PlusOutlined, DeleteOutlined, CalculatorOutlined, EyeOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { salesApi, shipmentApi } from '../services/api';
import type { SalesPlanListItem, CalculationResponse } from '../types/sales';
import type { ShipmentPlanListItem } from '../types/shipment';
import SalesInputPanel from '../components/sales/SalesInputPanel';
import DailyInventoryTable from '../components/sales/DailyInventoryTable';
import StockoutWarning from '../components/sales/StockoutWarning';
import InventoryOverrideControl from '../components/sales/InventoryOverrideControl';

const { RangePicker } = DatePicker;

const SalesPlanPage: React.FC = () => {
  const [plans, setPlans] = useState<SalesPlanListItem[]>([]);
  const [shipmentPlans, setShipmentPlans] = useState<ShipmentPlanListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [detailPlanId, setDetailPlanId] = useState<number | null>(null);
  const [calcResult, setCalcResult] = useState<CalculationResponse | null>(null);
  const [calcLoading, setCalcLoading] = useState(false);
  const [overrideState, setOverrideState] = useState<{
    open: boolean; date: string; value: number;
  }>({ open: false, date: '', value: 0 });
  const [form] = Form.useForm();

  const loadPlans = useCallback(async () => {
    setLoading(true);
    try {
      const [sp, shp] = await Promise.all([salesApi.list(), shipmentApi.list()]);
      setPlans(sp);
      setShipmentPlans(shp);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadPlans(); }, [loadPlans]);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await salesApi.create({
        plan_name: values.plan_name,
        sku: values.sku,
        asin: values.asin,
        start_date: values.dateRange[0].format('YYYY-MM-DD'),
        end_date: values.dateRange[1].format('YYYY-MM-DD'),
        initial_inventory: values.initial_inventory || 0,
        shipment_plan_id: values.shipment_plan_id,
      });
      message.success('创建成功');
      setCreateOpen(false);
      form.resetFields();
      loadPlans();
    } catch (e: any) {
      message.error(e.response?.data?.detail || '创建失败');
    }
  };

  const handleDelete = async (id: number) => {
    await salesApi.delete(id);
    message.success('删除成功');
    loadPlans();
  };

  const runCalculation = async (planId: number) => {
    setCalcLoading(true);
    setDetailPlanId(planId);
    try {
      const result = await salesApi.calculate(planId);
      setCalcResult(result);
    } catch (e: any) {
      message.error(e.response?.data?.detail || '计算失败');
    } finally {
      setCalcLoading(false);
    }
  };

  const handleOverrideConfirm = async (value: number, reason: string) => {
    if (!detailPlanId) return;
    try {
      await salesApi.addOverride(detailPlanId, {
        override_date: overrideState.date,
        override_value: value,
        reason,
      });
      message.success('校正成功');
      setOverrideState({ open: false, date: '', value: 0 });
      runCalculation(detailPlanId);
    } catch (e: any) {
      message.error(e.response?.data?.detail || '校正失败');
    }
  };

  const columns = [
    { title: '计划名称', dataIndex: 'plan_name' },
    { title: 'SKU', dataIndex: 'sku' },
    { title: '开始日期', dataIndex: 'start_date' },
    { title: '结束日期', dataIndex: 'end_date' },
    { title: '期初库存', dataIndex: 'initial_inventory' },
    {
      title: '关联发货计划', dataIndex: 'shipment_plan_id',
      render: (v: number | null) => {
        if (!v) return '-';
        const sp = shipmentPlans.find((p) => p.id === v);
        return sp?.plan_name || `#${v}`;
      },
    },
    {
      title: '操作', key: 'actions',
      render: (_: unknown, record: SalesPlanListItem) => (
        <Space>
          <Button size="small" icon={<CalculatorOutlined />} onClick={() => runCalculation(record.id)}>
            计算
          </Button>
          <Popconfirm title="确认删除?" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const detailPlan = plans.find((p) => p.id === detailPlanId);

  return (
    <div>
      <Card
        title="销售/库存规划列表"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
            新建规划
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
        title="新建销售/库存规划"
        open={createOpen}
        onOk={handleCreate}
        onCancel={() => setCreateOpen(false)}
        okText="创建"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="plan_name" label="计划名称" rules={[{ required: true }]}>
            <Input placeholder="例: 2026年5月销量规划" />
          </Form.Item>
          <Space>
            <Form.Item name="sku" label="SKU"><Input /></Form.Item>
            <Form.Item name="asin" label="ASIN"><Input /></Form.Item>
          </Space>
          <Form.Item name="dateRange" label="规划日期范围" rules={[{ required: true }]}>
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="initial_inventory" label="首日期初库存">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="shipment_plan_id" label="关联发货计划">
            <Select allowClear placeholder="选择发货计划（可选）">
              {shipmentPlans.map((sp) => (
                <Select.Option key={sp.id} value={sp.id}>{sp.plan_name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Calculation Result Modal */}
      <Modal
        title={detailPlan ? `${detailPlan.plan_name} - 库存计算结果` : '计算结果'}
        open={!!detailPlanId}
        onCancel={() => { setDetailPlanId(null); setCalcResult(null); }}
        footer={null}
        width={1100}
      >
        {detailPlan && (
          <SalesInputPanel
            planId={detailPlan.id}
            startDate={detailPlan.start_date}
            endDate={detailPlan.end_date}
            onEntriesAdded={() => runCalculation(detailPlan.id)}
            addEntries={salesApi.addEntries}
            batchSetSales={salesApi.batchSetSales}
          />
        )}

        {calcLoading ? (
          <Spin style={{ display: 'block', margin: '40px auto' }} />
        ) : calcResult ? (
          <>
            <Row gutter={16} style={{ marginTop: 16, marginBottom: 16 }}>
              <Col span={6}><Statistic title="总天数" value={calcResult.summary.total_days} /></Col>
              <Col span={6}><Statistic title="总规划销量" value={calcResult.summary.total_planned_sales} /></Col>
              <Col span={6}><Statistic title="总实际消耗" value={calcResult.summary.total_actual_sales} /></Col>
              <Col span={6}>
                <Statistic
                  title="断货天数"
                  value={calcResult.summary.stockout_days}
                  valueStyle={{ color: calcResult.summary.stockout_days > 0 ? '#f5222d' : '#52c41a' }}
                />
              </Col>
            </Row>

            <StockoutWarning
              stockoutDates={calcResult.summary.stockout_dates}
              stockoutDays={calcResult.summary.stockout_days}
            />

            <DailyInventoryTable
              data={calcResult.daily_data}
              onOverrideClick={(date, openingStock) =>
                setOverrideState({ open: true, date, value: openingStock })
              }
            />
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            请先录入销量数据，然后点击"计算"按钮
          </div>
        )}
      </Modal>

      <InventoryOverrideControl
        open={overrideState.open}
        date={overrideState.date}
        currentValue={overrideState.value}
        onCancel={() => setOverrideState({ open: false, date: '', value: 0 })}
        onConfirm={handleOverrideConfirm}
      />
    </div>
  );
};

export default SalesPlanPage;
