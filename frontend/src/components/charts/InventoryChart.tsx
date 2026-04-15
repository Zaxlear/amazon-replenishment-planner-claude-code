import React from 'react';
import {
  ComposedChart, Area, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine, Brush,
} from 'recharts';
import type { DailyCalculationResult } from '../../types/sales';

interface Props {
  data: DailyCalculationResult[];
}

const InventoryChart: React.FC<Props> = ({ data }) => {
  const chartData = data.map((d) => ({
    date: d.date,
    openingStock: d.opening_stock,
    plannedSales: d.planned_sales,
    actualSales: d.actual_sales,
    arrivals: d.arrivals,
    isStockout: d.is_stockout,
  }));

  // Find arrival dates for reference lines
  const arrivalDates = data.filter((d) => d.arrivals > 0);

  return (
    <ResponsiveContainer width="100%" height={450}>
      <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={60} />
        <YAxis yAxisId="left" label={{ value: '库存', angle: -90, position: 'insideLeft' }} />
        <YAxis yAxisId="right" orientation="right" label={{ value: '销量', angle: 90, position: 'insideRight' }} />
        <Tooltip
          formatter={(value, name) => {
            const labels: Record<string, string> = {
              openingStock: '期初库存',
              plannedSales: '规划销量',
              actualSales: '实际消耗',
            };
            return [String(value), labels[String(name)] || String(name)];
          }}
        />
        <Legend
          formatter={(value: string) => {
            const labels: Record<string, string> = {
              openingStock: '期初库存',
              plannedSales: '规划销量',
              actualSales: '实际消耗',
            };
            return labels[value] || value;
          }}
        />

        <Area
          yAxisId="left"
          type="monotone"
          dataKey="openingStock"
          fill="#91caff"
          stroke="#1890ff"
          fillOpacity={0.3}
        />
        <Bar yAxisId="right" dataKey="plannedSales" fill="#95de64" barSize={8} />
        <Bar yAxisId="right" dataKey="actualSales" fill="#52c41a" barSize={8} />

        {arrivalDates.map((d) => (
          <ReferenceLine
            key={d.date}
            x={d.date}
            yAxisId="left"
            stroke="#fa8c16"
            strokeDasharray="3 3"
            label={{ value: `+${d.arrivals}`, position: 'top', fontSize: 10, fill: '#fa8c16' }}
          />
        ))}

        <Brush dataKey="date" height={30} stroke="#1890ff" />
      </ComposedChart>
    </ResponsiveContainer>
  );
};

export default InventoryChart;
