/**
 * Process WIP Horizontal Bar Chart Component
 * Shows Work-In-Progress count by process
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { theme } from '@/styles';

interface ProcessWipData {
  process_name: string;
  wip_count: number;
}

interface ProcessWipChartProps {
  data: ProcessWipData[];
  height?: number;
}

export const ProcessWipChart = ({ data, height = 300 }: ProcessWipChartProps) => {
  // Ensure data is an array
  const chartData = Array.isArray(data) ? data : [];

  // Get max WIP for color intensity
  const maxWip = Math.max(...chartData.map((d) => d.wip_count), 1);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
      >
        <CartesianGrid
          strokeDasharray={theme.charts.grid.strokeDasharray}
          stroke={theme.charts.grid.stroke}
          horizontal={false}
        />
        <XAxis
          type="number"
          stroke={theme.charts.axis.stroke}
          tick={{ fill: theme.colors.text.secondary, fontSize: 12 }}
        />
        <YAxis
          type="category"
          dataKey="process_name"
          stroke={theme.charts.axis.stroke}
          tick={{ fill: theme.colors.text.secondary, fontSize: 12 }}
          width={90}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: theme.charts.tooltip.background,
            border: theme.charts.tooltip.border,
            borderRadius: theme.charts.tooltip.borderRadius,
            color: theme.charts.tooltip.color,
          }}
          formatter={(value: number) => [`${value} units`, 'WIP']}
        />
        <Bar dataKey="wip_count" radius={[0, 4, 4, 0]}>
          {chartData.map((entry, index) => {
            // Color intensity based on WIP count
            const intensity = entry.wip_count / maxWip;
            let color = theme.charts.colors[0]; // Green for low
            if (intensity > 0.7) {
              color = theme.charts.colors[3]; // Red for high
            } else if (intensity > 0.4) {
              color = theme.charts.colors[2]; // Orange for medium
            }
            return <Cell key={`cell-${index}`} fill={color} />;
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
