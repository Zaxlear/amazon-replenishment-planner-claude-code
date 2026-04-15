import React, { useState, useEffect } from 'react';
import { Card, Select, Spin, Empty, message } from 'antd';
import { salesApi } from '../services/api';
import type { SalesPlanListItem, CalculationResponse } from '../types/sales';
import InventoryChart from '../components/charts/InventoryChart';
import StockoutWarning from '../components/sales/StockoutWarning';

const ChartDashboard: React.FC = () => {
  const [plans, setPlans] = useState<SalesPlanListItem[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [calcResult, setCalcResult] = useState<CalculationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    salesApi.list().then(setPlans);
  }, []);

  const handleSelect = async (planId: number) => {
    setSelectedPlanId(planId);
    setLoading(true);
    try {
      const result = await salesApi.calculate(planId);
      setCalcResult(result);
    } catch (e: any) {
      message.error(e.response?.data?.detail || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="图表面板">
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
        ) : calcResult && calcResult.daily_data.length > 0 ? (
          <>
            <StockoutWarning
              stockoutDates={calcResult.summary.stockout_dates}
              stockoutDays={calcResult.summary.stockout_days}
            />
            <InventoryChart data={calcResult.daily_data} />
          </>
        ) : (
          <Empty description="请选择规划并确保已有销量数据" />
        )}
      </Card>
    </div>
  );
};

export default ChartDashboard;
