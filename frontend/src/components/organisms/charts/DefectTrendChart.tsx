/**
 * Defect Trend Chart Component
 * Displays defect rate trends over time with threshold line
 */

import { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
} from 'recharts';
import { Card, Typography, Empty, Spin } from 'antd';
import { analyticsApi } from '@/api';
import type { DefectTrend } from '@/types/api';
import Logger from '@/utils/logger';

const { Title } = Typography;

interface DefectTrendChartProps {
  days?: number;
  period?: 'daily' | 'weekly';
  thresholdPercent?: number;
  refreshInterval?: number;
  className?: string;
}

export const DefectTrendChart = ({
  days = 7,
  period = 'daily',
  thresholdPercent = 5,
  refreshInterval = 300000, // 5 minutes
  className,
}: DefectTrendChartProps) => {
  const [data, setData] = useState<DefectTrend[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const response = await analyticsApi.getDefectTrends(period, days);
      setData(response.trends);
      setError(null);
    } catch (err) {
      Logger.error('Failed to fetch defect trends:', err);
      setError('Failed to load defect trends');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [days, period, refreshInterval]);

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
    });
  };

  // Process data for chart
  const chartData = data.map(item => ({
    ...item,
    date: formatDate(item.date),
    defect_rate: Number(item.defect_rate.toFixed(2)),
  }));

  if (isLoading) {
    return (
      <Card className={`h-full flex items-center justify-center min-h-[300px] ${className || ''}`}>
        <Spin tip="Loading defect trends..." />
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`h-full flex items-center justify-center min-h-[300px] ${className || ''}`}>
        <Empty description={error} />
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className={`h-full flex items-center justify-center min-h-[300px] ${className || ''}`}>
        <Empty description="No defect data available" />
      </Card>
    );
  }

  // Calculate average
  const avgDefectRate = data.reduce((sum, item) => sum + item.defect_rate, 0) / data.length;

  return (
    <Card className={`h-full shadow-sm ${className || ''}`}>
      <div className="mb-4">
        <Title level={4} style={{ margin: 0 }}>Defect Rate Trend</Title>
        <Typography.Text type="secondary">
          Last {days} days | Avg: {avgDefectRate.toFixed(2)}%
        </Typography.Text>
      </div>

      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart
            data={chartData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11 }}
              domain={[0, 'auto']}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              contentStyle={{
                borderRadius: '8px',
                border: 'none',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                backgroundColor: 'var(--color-bg-primary)',
                color: 'var(--color-text-primary)',
              }}
              labelStyle={{ color: 'var(--color-text-primary)', fontWeight: 600 }}
              formatter={(value: number) => [`${value}%`, 'Defect Rate']}
            />
            <Legend />

            {/* Threshold line */}
            <ReferenceLine
              y={thresholdPercent}
              stroke="#ff4d4f"
              strokeDasharray="5 5"
              label={{
                value: `Target: ${thresholdPercent}%`,
                position: 'right',
                fill: '#ff4d4f',
                fontSize: 11,
              }}
            />

            <Line
              type="monotone"
              dataKey="defect_rate"
              name="Defect Rate (%)"
              stroke="#1890ff"
              strokeWidth={2}
              dot={{
                fill: '#1890ff',
                strokeWidth: 2,
                r: 4,
              }}
              activeDot={{
                r: 6,
                stroke: '#1890ff',
                strokeWidth: 2,
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
