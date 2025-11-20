/**
 * Defect Distribution Pie Chart Component
 * Shows pass/fail distribution
 */

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { theme } from '@/styles';

interface DefectData {
  name: string;
  value: number;
  color?: string;
  [key: string]: string | number | undefined;
}

interface DefectPieChartProps {
  passed: number;
  failed: number;
  height?: number;
}

export const DefectPieChart = ({ passed, failed, height = 300 }: DefectPieChartProps) => {
  const data: DefectData[] = [
    { name: 'Passed', value: passed, color: theme.colors.status.success },
    { name: 'Failed', value: failed, color: theme.colors.status.error },
  ];

  // Ensure data is an array
  const chartData = Array.isArray(data) ? data : [];

  const total = passed + failed;
  const passRate = total > 0 ? ((passed / total) * 100).toFixed(1) : 0;

  return (
    <div style={{ position: 'relative' }}>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
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
            formatter={(value: number) => [`${value} units`, '']}
          />
          <Legend
            verticalAlign="bottom"
            formatter={(value) => <span style={{ color: 'var(--color-text-secondary)' }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -70%)',
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
          {passRate}%
        </div>
        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
          Pass Rate
        </div>
      </div>
    </div>
  );
};
