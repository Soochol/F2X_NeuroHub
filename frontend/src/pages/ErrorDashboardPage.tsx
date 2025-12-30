/**
 * Error Dashboard Page
 *
 * Provides comprehensive error monitoring and debugging capabilities:
 * - Error statistics (total count, trends, distribution)
 * - Visualizations (LineChart for trends, PieChart for distribution)
 * - Paginated error log table with filtering
 * - Trace ID lookup for debugging
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Select,
  Input,
  Button,
  Statistic,
  Row,
  Col,
  Space,
  Tag,
  Tooltip,
  message,
  DatePicker,
  theme,
} from 'antd';
import {
  ReloadOutlined,
  SearchOutlined,
  CopyOutlined,
  WarningOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { errorLogsApi } from '@/api';
import type { ErrorLog, ErrorLogStats, ErrorLogFilters } from '@/api';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { Dayjs } from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { useToken } = theme;

/**
 * Time range presets
 */
const TIME_RANGES = {
  '24h': 24,
  '7d': 168,
  '30d': 720,
};

const ErrorDashboardPage: React.FC = () => {
  const { token } = useToken();

  /**
   * Color palette for charts - using theme tokens
   */
  const COLORS = [
    token.colorPrimary,
    token.colorSuccess,
    token.colorWarning,
    token.colorError,
    token.colorInfo,
    token.colorLink,
    token.colorTextSecondary,
  ];

  /**
   * Status code color mapping using theme-aware colors
   */
  const getStatusCodeColor = (statusCode: number): string => {
    if (statusCode >= 500) return 'red';
    if (statusCode >= 400) return 'orange';
    return 'green';
  };
  // State for statistics
  const [stats, setStats] = useState<ErrorLogStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [timeRange, setTimeRange] = useState<number>(24);

  // State for error logs
  const [errorLogs, setErrorLogs] = useState<ErrorLog[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Filters
  const [errorCodeFilter, setErrorCodeFilter] = useState<string | undefined>();
  const [statusCodeFilter, setStatusCodeFilter] = useState<number | undefined>();
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);
  const [pathFilter, setPathFilter] = useState<string | undefined>();
  const [methodFilter, setMethodFilter] = useState<string | undefined>();

  /**
   * Fetch error statistics
   */
  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const data = await errorLogsApi.getErrorStats(timeRange);
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch error stats:', error);
      message.error('Failed to load error statistics');
    } finally {
      setLoadingStats(false);
    }
  };

  /**
   * Fetch error logs with filters
   */
  const fetchErrorLogs = async () => {
    setLoadingLogs(true);
    try {
      const filters: ErrorLogFilters = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      };

      if (errorCodeFilter) filters.error_code = errorCodeFilter;
      if (statusCodeFilter) {
        filters.min_status_code = statusCodeFilter;
        filters.max_status_code = statusCodeFilter;
      }
      if (dateRange && dateRange[0] && dateRange[1]) {
        filters.start_date = dateRange[0].toISOString();
        filters.end_date = dateRange[1].toISOString();
      }
      if (pathFilter) filters.path = pathFilter;
      if (methodFilter) filters.method = methodFilter;

      const data = await errorLogsApi.getErrorLogs(filters);
      setErrorLogs(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch error logs:', error);
      message.error('Failed to load error logs');
    } finally {
      setLoadingLogs(false);
    }
  };

  /**
   * Copy trace ID to clipboard
   */
  const copyTraceId = (traceId: string) => {
    navigator.clipboard.writeText(traceId);
    message.success('Trace ID copied to clipboard');
  };

  /**
   * Reset filters
   */
  const resetFilters = () => {
    setErrorCodeFilter(undefined);
    setStatusCodeFilter(undefined);
    setDateRange(null);
    setPathFilter(undefined);
    setMethodFilter(undefined);
    setCurrentPage(1);
  };

  // Initial load and refresh on time range change
  useEffect(() => {
    fetchStats();
  }, [timeRange]);

  // Fetch logs when filters or pagination changes
  useEffect(() => {
    fetchErrorLogs();
  }, [currentPage, pageSize, errorCodeFilter, statusCodeFilter, dateRange, pathFilter, methodFilter]);

  /**
   * Table columns configuration
   */
  const columns: ColumnsType<ErrorLog> = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string) => dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss'),
      sorter: (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix(),
    },
    {
      title: 'Error Code',
      dataIndex: 'error_code',
      key: 'error_code',
      width: 120,
      render: (errorCode: string) => <Tag color="red">{errorCode}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status_code',
      key: 'status_code',
      width: 100,
      render: (statusCode: number) => (
        <Tag color={getStatusCodeColor(statusCode)}>{statusCode}</Tag>
      ),
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (message: string) => (
        <Tooltip title={message}>
          <span>{message}</span>
        </Tooltip>
      ),
    },
    {
      title: 'Path',
      dataIndex: 'path',
      key: 'path',
      width: 200,
      ellipsis: true,
      render: (path?: string) => path || '-',
    },
    {
      title: 'Method',
      dataIndex: 'method',
      key: 'method',
      width: 80,
      render: (method?: string) => method ? <Tag>{method}</Tag> : '-',
    },
    {
      title: 'User',
      dataIndex: 'username',
      key: 'username',
      width: 120,
      render: (username?: string) => username || '-',
    },
    {
      title: 'Trace ID',
      dataIndex: 'trace_id',
      key: 'trace_id',
      width: 120,
      render: (traceId: string) => (
        <Tooltip title="Click to copy">
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => copyTraceId(traceId)}
          >
            {traceId.slice(0, 8)}...
          </Button>
        </Tooltip>
      ),
    },
  ];

  /**
   * Prepare data for hourly trend chart
   */
  const hourlyTrendData = stats?.by_hour.map((item) => ({
    hour: dayjs(item.hour).format('MM-DD HH:mm'),
    count: item.count,
  })) || [];

  /**
   * Prepare data for error code distribution pie chart
   */
  const errorCodeDistributionData = stats?.by_error_code.map((item) => ({
    name: item.error_code,
    value: item.count,
  })) || [];

  /**
   * Custom label renderer for Pie chart with theme support
   */
  interface PieLabelProps {
    cx?: number;
    cy?: number;
    midAngle?: number;
    innerRadius?: number;
    outerRadius?: number;
    name?: string;
    value?: number;
  }
  const renderPieLabel = (props: PieLabelProps) => {
    const { cx = 0, cy = 0, midAngle = 0, innerRadius = 0, outerRadius = 0, name = '', value = 0 } = props;
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill={token.colorText}
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={12}
      >
        {`${name}: ${value}`}
      </text>
    );
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>Error Dashboard</h1>
      </div>

      {/* Time Range Selector */}
      <Card style={{ marginBottom: '24px' }}>
        <Space>
          <span style={{ fontWeight: 500 }}>Time Range:</span>
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Option value={TIME_RANGES['24h']}>Last 24 Hours</Option>
            <Option value={TIME_RANGES['7d']}>Last 7 Days</Option>
            <Option value={TIME_RANGES['30d']}>Last 30 Days</Option>
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchStats}
            loading={loadingStats}
          >
            Refresh
          </Button>
        </Space>
      </Card>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Errors"
              value={stats?.total_errors || 0}
              prefix={<WarningOutlined style={{ color: token.colorError }} />}
              valueStyle={{ color: token.colorError }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Top Error Code"
              value={stats?.by_error_code[0]?.error_code || 'N/A'}
              suffix={`(${stats?.by_error_code[0]?.count || 0})`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Error-Prone Paths"
              value={stats?.top_paths.length || 0}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Monitoring"
              value="Active"
              prefix={<CheckCircleOutlined style={{ color: token.colorSuccess }} />}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={14}>
          <Card title="Error Trend (Hourly)" loading={loadingStats}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={hourlyTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke={token.colorBorder} />
                <XAxis
                  dataKey="hour"
                  stroke={token.colorTextSecondary}
                  tick={{ fill: token.colorText }}
                />
                <YAxis
                  stroke={token.colorTextSecondary}
                  tick={{ fill: token.colorText }}
                />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: token.colorBgElevated,
                    borderColor: token.colorBorder,
                    borderRadius: token.borderRadius,
                  }}
                  labelStyle={{ color: token.colorText }}
                  itemStyle={{ color: token.colorText }}
                />
                <Legend
                  wrapperStyle={{ color: token.colorText }}
                  iconType="line"
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke={token.colorError}
                  strokeWidth={2}
                  name="Error Count"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="Error Code Distribution" loading={loadingStats}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={errorCodeDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderPieLabel}
                  outerRadius={80}
                  fill={token.colorPrimary}
                  dataKey="value"
                >
                  {errorCodeDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: token.colorBgElevated,
                    borderColor: token.colorBorder,
                    borderRadius: token.borderRadius,
                    color: token.colorText,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Top Error-Prone Paths */}
      {stats && stats.top_paths.length > 0 && (
        <Card title="Top Error-Prone Endpoints" style={{ marginBottom: '24px' }}>
          <Table
            dataSource={stats.top_paths}
            pagination={false}
            size="small"
            columns={[
              {
                title: 'Method',
                dataIndex: 'method',
                key: 'method',
                width: 100,
                render: (method: string) => <Tag>{method}</Tag>,
              },
              {
                title: 'Path',
                dataIndex: 'path',
                key: 'path',
                ellipsis: true,
              },
              {
                title: 'Error Count',
                dataIndex: 'count',
                key: 'count',
                width: 120,
                render: (count: number) => (
                  <Tag color="red">{count}</Tag>
                ),
              },
            ]}
          />
        </Card>
      )}

      {/* Error Logs Table */}
      <Card
        title="Error Logs"
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchErrorLogs}
              loading={loadingLogs}
            >
              Refresh
            </Button>
            <Button onClick={resetFilters}>Reset Filters</Button>
          </Space>
        }
      >
        {/* Filters */}
        <Space wrap style={{ marginBottom: '16px' }}>
          <Input
            placeholder="Error Code"
            value={errorCodeFilter}
            onChange={(e) => setErrorCodeFilter(e.target.value || undefined)}
            style={{ width: 150 }}
            allowClear
            prefix={<SearchOutlined />}
          />
          <Select
            placeholder="Status Code"
            value={statusCodeFilter}
            onChange={setStatusCodeFilter}
            style={{ width: 150 }}
            allowClear
          >
            <Option value={400}>400 Bad Request</Option>
            <Option value={401}>401 Unauthorized</Option>
            <Option value={403}>403 Forbidden</Option>
            <Option value={404}>404 Not Found</Option>
            <Option value={500}>500 Server Error</Option>
            <Option value={503}>503 Unavailable</Option>
          </Select>
          <Input
            placeholder="Path"
            value={pathFilter}
            onChange={(e) => setPathFilter(e.target.value || undefined)}
            style={{ width: 200 }}
            allowClear
            prefix={<SearchOutlined />}
          />
          <Select
            placeholder="Method"
            value={methodFilter}
            onChange={setMethodFilter}
            style={{ width: 120 }}
            allowClear
          >
            <Option value="GET">GET</Option>
            <Option value="POST">POST</Option>
            <Option value="PUT">PUT</Option>
            <Option value="DELETE">DELETE</Option>
            <Option value="PATCH">PATCH</Option>
          </Select>
          <RangePicker
            value={dateRange}
            onChange={setDateRange}
            showTime
            format="YYYY-MM-DD HH:mm"
          />
        </Space>

        <Table
          columns={columns}
          dataSource={errorLogs}
          rowKey="id"
          loading={loadingLogs}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} errors`,
            onChange: (page, pageSize) => {
              setCurrentPage(page);
              setPageSize(pageSize);
            },
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default ErrorDashboardPage;
