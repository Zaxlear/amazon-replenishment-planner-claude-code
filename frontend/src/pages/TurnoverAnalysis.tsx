import React, { useState, useEffect } from 'react';
import { Card, Select, Table, Tag, Spin, Empty, message } from 'antd';
import { salesApi } from '../services/api';
import type { SalesPlanListItem, ShipmentTurnoverResult, TurnoverResponse } from '../types/sales';
import TurnoverChart from '../components/charts/TurnoverChart';

const regionColors: Record<string, string> = {
  west: 'blue',
  central: 'gold',
  east: 'red',
};

const regionLabels: Record<string, string> = {
  west: '美西',
  central: '美中',
  east: '美东',
};

const TurnoverAnalysis: React.FC = () => {
  const [plans, setPlans] = useState<SalesPlanListItem[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [turnoverData, setTurnoverData] = useState<TurnoverResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    salesApi.list().then(setPlans);
  }, []);

  const handleSelect = async (planId: number) => {
    setSelectedPlanId(planId);
    setLoading(true);
    try {
      const result = await salesApi.turnover(planId);
      setTurnoverData(result);
    } catch (e: any) {
      message.error(e.response?.data?.detail || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: '货件', dataIndex: 'unit_label' },
    {
      title: '仓库', dataIndex: 'region',
      render: (v: string) => <Tag color={regionColors[v]}>{regionLabels[v] || v}</Tag>,
    },
    { title: '发货日', dataIndex: 'ship_date' },
    { title: '到货日', dataIndex: 'arrival_date' },
    { title: '数量', dataIndex: 'quantity' },
    {
      title: '已售', dataIndex: 'sold_quantity',
      render: (v: number, record: ShipmentTurnoverResult) => `${v}/${record.quantity}`,
    },
    {
      title: '状态', dataIndex: 'fully_sold',
      render: (v: boolean) => v
        ? <Tag color="success">已售罄</Tag>
        : <Tag color="processing">销售中</Tag>,
    },
    {
      title: '平均周转', dataIndex: 'avg_turnover_days',
      render: (v: number | null) => v !== null ? `${v}天` : '-',
    },
    { title: '售罄日', dataIndex: 'sell_through_date', render: (v: string | null) => v || '-' },
  ];

  return (
    <div>
      <Card title="库存周转分析">
        <Select
          placeholder="选择销售规划"
          style={{ width: 300, marginBottom: 16 }}
          onChange={handleSelect}
          value={selectedPlanId}
        >
          {plans.map((p) => (
            <Select.Option key={p.id} value={p.id}>{p.plan_name}</Select.Option>
          ))}
        </Select>

        {loading ? (
          <Spin style={{ display: 'block', margin: '60px auto' }} />
        ) : turnoverData && turnoverData.turnovers.length > 0 ? (
          <>
            <TurnoverChart data={turnoverData.turnovers} />
            <Table
              dataSource={turnoverData.turnovers}
              columns={columns}
              rowKey="unit_id"
              pagination={false}
              size="small"
              style={{ marginTop: 16 }}
            />
          </>
        ) : (
          <Empty description="请选择规划并确保已关联发货计划" />
        )}
      </Card>
    </div>
  );
};

export default TurnoverAnalysis;
