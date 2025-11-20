/**
 * Production Bar Chart Component
 * Shows production statistics (started, completed, defective)
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { theme } from '@/styles';

interface ProductionData {
  name: string;
  started: number;
  completed: number;
  defective: number;
}

interface ProductionBarChartProps {
  data: ProductionData[];
  height?: number;
}

export const ProductionBarChart = ({ data, height = 300 }: ProductionBarChartProps) => {
  // Ensure data is an array
  const chartData = Array.isArray(data) ? data : [];

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid
          strokeDasharray={theme.charts.grid.strokeDasharray}
          stroke={theme.charts.grid.stroke}
        />
        <XAxis
          dataKey="name"
          stroke={theme.charts.axis.stroke}
          tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }}
        />
        <YAxis
          stroke={theme.charts.axis.stroke}
          tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }}
        />
        <Tooltip
          cursor={false}
          contentStyle={{
            backgroundColor: theme.charts.tooltip.background,
            border: theme.charts.tooltip.border,
            borderRadius: theme.charts.tooltip.borderRadius,
            color: theme.charts.tooltip.color,
          }}
          itemStyle={{
            color: theme.charts.tooltip.color,
          }}
          labelStyle={{
            color: theme.charts.tooltip.color,
          }}
        />
        <Legend
          wrapperStyle={{ paddingTop: '10px' }}
          formatter={(value) => <span style={{ color: 'var(--color-text-secondary)' }}>{value}</span>}
        />
        <Bar
          dataKey="started"
          name="Started"
          fill={theme.charts.colors[1]}
          radius={[4, 4, 0, 0]}
          cursor={false}
        />
        <Bar
          dataKey="completed"
          name="Completed"
          fill={theme.charts.colors[0]}
          radius={[4, 4, 0, 0]}
          cursor={false}
        />
        <Bar
          dataKey="defective"
          name="Defective"
          fill={theme.charts.colors[3]}
          radius={[4, 4, 0, 0]}
          cursor={false}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};
