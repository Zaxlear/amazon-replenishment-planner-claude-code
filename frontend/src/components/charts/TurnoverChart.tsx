import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell,
} from 'recharts';
import type { ShipmentTurnoverResult } from '../../types/sales';

interface Props {
  data: ShipmentTurnoverResult[];
}

const regionColors: Record<string, string> = {
  west: '#1890ff',
  central: '#faad14',
  east: '#f5222d',
};

const TurnoverChart: React.FC<Props> = ({ data }) => {
  const chartData = data.map((d) => ({
    name: d.unit_label,
    turnover: d.avg_turnover_days || 0,
    region: d.region,
    fullySold: d.fully_sold,
  }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" angle={-45} textAnchor="end" tick={{ fontSize: 11 }} height={80} />
        <YAxis label={{ value: '平均周转天数', angle: -90, position: 'insideLeft' }} />
        <Tooltip
          formatter={(value) => [`${value}天`, '平均周转']}
        />
        <Bar dataKey="turnover" name="平均周转天数">
          {chartData.map((entry, index) => (
            <Cell key={index} fill={regionColors[entry.region] || '#8884d8'} opacity={entry.fullySold ? 1 : 0.5} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export default TurnoverChart;
