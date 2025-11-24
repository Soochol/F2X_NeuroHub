import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Card, Typography, Empty, Spin } from 'antd';
import type { ProcessCycleTime } from '@/types/api';

const { Title } = Typography;

interface CycleTimeChartProps {
    data: ProcessCycleTime[];
    isLoading?: boolean;
}

export const CycleTimeChart = ({ data, isLoading = false }: CycleTimeChartProps) => {
    if (isLoading) {
        return (
            <Card className="h-full flex items-center justify-center min-h-[300px]">
                <Spin tip="Loading cycle times..." />
            </Card>
        );
    }

    if (!data || data.length === 0) {
        return (
            <Card className="h-full flex items-center justify-center min-h-[300px]">
                <Empty description="No cycle time data available" />
            </Card>
        );
    }

    return (
        <Card className="h-full shadow-sm">
            <div className="mb-4">
                <Title level={4} style={{ margin: 0 }}>Process Cycle Times</Title>
                <Typography.Text type="secondary">Average duration per process (last 7 days)</Typography.Text>
            </div>

            <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                    <BarChart
                        data={data}
                        margin={{
                            top: 20,
                            right: 30,
                            left: 20,
                            bottom: 5,
                        }}
                    >
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis
                            dataKey="process_name"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 12 }}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fontSize: 12 }}
                            label={{ value: 'Seconds', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip
                            cursor={{ fill: 'transparent' }}
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                        />
                        <Legend />
                        <Bar
                            dataKey="average_cycle_time"
                            name="Avg Cycle Time (sec)"
                            fill="#1890ff"
                            radius={[4, 4, 0, 0]}
                            barSize={40}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </Card>
    );
};
