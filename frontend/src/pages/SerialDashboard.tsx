/**
 * Serial Dashboard Page
 * Real-time WIP monitoring and serial tracking
 */

import { useState, useEffect } from 'react';
import { Card, Button, Input, Select } from '@/components/common';
import { dashboardApi, serialsApi, wipItemsApi } from '@/api';
import { SerialStatus, type Serial, type ProcessWIP, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';
import { RefreshCw, Clock, Package, AlertCircle, CheckCircle, XCircle, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface DashboardStats {
  totalWip: number;
  inProgress: number;
  completed: number;
  failed: number;
}

export const SerialDashboard = () => {
  const [processWipData, setProcessWipData] = useState<ProcessWIP[]>([]);
  const [serials, setSerials] = useState<Serial[]>([]);
  const [stats, setStats] = useState<DashboardStats>({ totalWip: 0, inProgress: 0, completed: 0, failed: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Search & filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<SerialStatus | ''>('');

  useEffect(() => {
    fetchDashboardData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000);

    return () => clearInterval(interval);
  }, [statusFilter]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError('');
    try {
      // Fetch process WIP data
      const wipResponse = await dashboardApi.getProcessWIP();
      setProcessWipData(wipResponse.processes);

      // Fetch WIP items instead of serials
      const wipItemsResponse = await wipItemsApi.getWIPItems({ limit: 1000 });

      // For display, we still show serials if available
      const serialsResponse = await serialsApi.getSerials({ limit: 50 });
      const serialsList = Array.isArray(serialsResponse) ? serialsResponse : serialsResponse.items || [];
      setSerials(serialsList);

      // Calculate stats from WIP Items
      setStats({
        totalWip: wipItemsResponse.filter(w => w.status !== 'COMPLETED' && w.status !== 'FAILED' && w.status !== 'CONVERTED').length,
        inProgress: wipItemsResponse.filter(w => w.status === 'IN_PROGRESS').length,
        completed: wipItemsResponse.filter(w => w.status === 'COMPLETED' || w.status === 'CONVERTED').length,
        failed: wipItemsResponse.filter(w => w.status === 'FAILED').length,
      });

      setLastUpdate(new Date());
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load dashboard data'));
    } finally {
      setIsLoading(false);
    }
  };

  const filteredSerials = serials.filter((serial) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      serial.serial_number.toLowerCase().includes(query) ||
      (serial.lot?.lot_number && serial.lot.lot_number.toLowerCase().includes(query))
    );
  });

  const getStatusColor = (status: SerialStatus) => {
    switch (status) {
      case SerialStatus.CREATED:
        return 'var(--color-info)';
      case SerialStatus.IN_PROGRESS:
        return 'var(--color-warning)';
      case SerialStatus.PASS:
        return 'var(--color-success)';
      case SerialStatus.FAIL:
        return 'var(--color-error)';
      default:
        return 'var(--color-text-secondary)';
    }
  };

  const getStatusBgColor = (status: SerialStatus) => {
    switch (status) {
      case SerialStatus.CREATED:
        return 'var(--color-info-bg)';
      case SerialStatus.IN_PROGRESS:
        return 'var(--color-warning-bg)';
      case SerialStatus.PASS:
        return 'var(--color-success-bg)';
      case SerialStatus.FAIL:
        return 'var(--color-error-bg)';
      default:
        return 'var(--color-bg-tertiary)';
    }
  };

  const getStatusIcon = (status: SerialStatus) => {
    switch (status) {
      case SerialStatus.CREATED:
        return <Package size={16} />;
      case SerialStatus.IN_PROGRESS:
        return <Activity size={16} />;
      case SerialStatus.PASS:
        return <CheckCircle size={16} />;
      case SerialStatus.FAIL:
        return <XCircle size={16} />;
      default:
        return <AlertCircle size={16} />;
    }
  };

  // Prepare bottleneck chart data
  const bottleneckData = processWipData
    .map(p => ({
      name: p.process_name,
      wip_count: p.wip_count,
    }))
    .sort((a, b) => b.wip_count - a.wip_count)
    .slice(0, 5);

  // Prepare pie chart data
  const pieData = [
    { name: 'Completed', value: stats.completed, color: 'var(--color-success)' },
    { name: 'In Progress', value: stats.inProgress, color: 'var(--color-warning)' },
    { name: 'Failed', value: stats.failed, color: 'var(--color-error)' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '5px', color: 'var(--color-text-primary)' }}>
            WIP Dashboard
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
            Last Update: {format(lastUpdate, 'yyyy-MM-dd HH:mm:ss')}
          </p>
        </div>
        <Button onClick={fetchDashboardData} variant="secondary">
          <RefreshCw size={16} style={{ marginRight: '6px' }} />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <Card style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
            Total WIP
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-brand)' }}>
            {stats.totalWip}
          </div>
        </Card>

        <Card style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
            In Progress
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-warning)' }}>
            {stats.inProgress}
          </div>
        </Card>

        <Card style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
            Completed
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-success)' }}>
            {stats.completed}
          </div>
        </Card>

        <Card style={{ padding: '20px', textAlign: 'center' }}>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
            Failed
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-error)' }}>
            {stats.failed}
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        {/* Bottleneck Chart */}
        <Card style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: 'var(--color-text-primary)' }}>
            Process Bottleneck Analysis
          </h2>
          {bottleneckData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={bottleneckData} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis type="number" stroke="var(--color-text-secondary)" />
                <YAxis type="category" dataKey="name" stroke="var(--color-text-secondary)" width={90} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--color-bg-secondary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                    color: 'var(--color-text-primary)',
                  }}
                />
                <Bar dataKey="wip_count" fill="var(--color-brand)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              No data available
            </div>
          )}
        </Card>

        {/* Pie Chart */}
        <Card style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: 'var(--color-text-primary)' }}>
            Status Distribution
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={100}
                fill="var(--color-brand-400)"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--color-bg-secondary)',
                  border: '1px solid var(--color-border)',
                  borderRadius: '6px',
                  color: 'var(--color-text-primary)',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Serial Search & List */}
      <Card>
        <div style={{ padding: '20px', borderBottom: '1px solid var(--color-border)' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: 'var(--color-text-primary)' }}>
            Serial Search
          </h2>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div style={{ flex: 1 }}>
              <Input
                placeholder="Search serial number or LOT number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                wrapperStyle={{ marginBottom: 0 }}
              />
            </div>
            <div style={{ width: '200px' }}>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as SerialStatus | '')}
                options={[
                  { value: '', label: 'All Status' },
                  { value: SerialStatus.CREATED, label: 'Created' },
                  { value: SerialStatus.IN_PROGRESS, label: 'In Progress' },
                  { value: SerialStatus.PASS, label: 'Pass' },
                  { value: SerialStatus.FAIL, label: 'Fail' },
                ]}
                wrapperStyle={{ marginBottom: 0 }}
              />
            </div>
          </div>
        </div>

        <div style={{ padding: '20px' }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              Loading serials...
            </div>
          ) : error ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
              {error}
            </div>
          ) : filteredSerials.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              No serials found
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '12px' }}>
              {filteredSerials.slice(0, 20).map((serial) => (
                <div
                  key={serial.id}
                  style={{
                    padding: '15px',
                    border: '1px solid var(--color-border)',
                    borderRadius: '6px',
                    backgroundColor: 'var(--color-bg-secondary)',
                    transition: 'all 0.2s',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-brand)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                        <span style={{ fontSize: '16px', fontWeight: 'bold', fontFamily: 'monospace', color: 'var(--color-text-primary)' }}>
                          {serial.serial_number}
                        </span>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            backgroundColor: getStatusBgColor(serial.status),
                            color: getStatusColor(serial.status),
                          }}
                        >
                          {getStatusIcon(serial.status)}
                          {serial.status}
                        </span>
                      </div>
                      {serial.lot && (
                        <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                          LOT: {serial.lot.lot_number}
                        </div>
                      )}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      {serial.completed_at && (
                        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                          <Clock size={12} style={{ marginRight: '4px', display: 'inline', verticalAlign: 'middle' }} />
                          {format(new Date(serial.completed_at), 'yyyy-MM-dd HH:mm')}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
