/**
 * Process Defect Rate Page - Quality Management
 *
 * Displays process defect rate analysis for quality management.
 * Features: filtering, pagination, statistics cards, defect rate charts.
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, Button, Input, Select } from '@/components/common';
import { measurementsApi, processesApi } from '@/api';
import type {
  MeasurementHistory,
  MeasurementHistoryFilters,
  MeasurementSummaryResponse,
  MeasurementHistoryItem,
  Process,
  ProcessResult,
} from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { format, subDays } from 'date-fns';
import {
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Download,
  RefreshCw,
  Filter,
  BarChart3,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

export const ProcessDefectRatePage = () => {
  // Data states
  const [data, setData] = useState<MeasurementHistory[]>([]);
  const [summary, setSummary] = useState<MeasurementSummaryResponse | null>(null);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [total, setTotal] = useState(0);

  // UI states
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [showCharts, setShowCharts] = useState(true);

  // Filter states
  const [startDate, setStartDate] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [selectedProcessId, setSelectedProcessId] = useState<number | undefined>(undefined);
  const [selectedResult, setSelectedResult] = useState<ProcessResult | undefined>(undefined);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Load processes for filter dropdown
  useEffect(() => {
    const loadProcesses = async () => {
      try {
        const processData = await processesApi.getProcesses();
        setProcesses(processData);
      } catch (err) {
        console.error('Failed to load processes:', err);
      }
    };
    loadProcesses();
  }, []);

  // Fetch data
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const filters: MeasurementHistoryFilters = {
        start_date: startDate ? `${startDate}T00:00:00` : undefined,
        end_date: endDate ? `${endDate}T23:59:59` : undefined,
        process_id: selectedProcessId,
        result: selectedResult,
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      };

      const [historyResponse, summaryResponse] = await Promise.all([
        measurementsApi.getMeasurementHistory(filters),
        measurementsApi.getMeasurementSummary({
          start_date: filters.start_date,
          end_date: filters.end_date,
          process_id: selectedProcessId,
        }),
      ]);

      setData(historyResponse.items);
      setTotal(historyResponse.total);
      setSummary(summaryResponse);
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load measurement data.'));
    } finally {
      setIsLoading(false);
    }
  }, [startDate, endDate, selectedProcessId, selectedResult, currentPage, pageSize]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handlers
  const handleApplyFilter = () => {
    setCurrentPage(1);
    fetchData();
  };

  const handleResetFilter = () => {
    setStartDate(format(subDays(new Date(), 30), 'yyyy-MM-dd'));
    setEndDate(format(new Date(), 'yyyy-MM-dd'));
    setSelectedProcessId(undefined);
    setSelectedResult(undefined);
    setCurrentPage(1);
  };

  const handleExportCSV = () => {
    if (data.length === 0) return;

    const headers = ['Time', 'LOT', 'Serial', 'Process', 'Result', 'Operator', 'Measurements'];
    const rows = data.map((item) => [
      format(new Date(item.started_at), 'yyyy-MM-dd HH:mm:ss'),
      item.lot_number,
      item.serial_number || item.wip_id || '-',
      item.process_name,
      item.result,
      item.operator_name,
      item.measurements.map((m) => `${m.name}: ${m.value}${m.unit || ''}`).join('; '),
    ]);

    const csvContent = [headers.join(','), ...rows.map((row) => row.map((cell) => `"${cell}"`).join(','))].join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `defect_rate_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`;
    link.click();
  };

  const totalPages = Math.ceil(total / pageSize);

  // Result badge style
  const getResultBadgeStyle = (result: string) => {
    const baseStyle = {
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: '500' as const,
    };
    if (result === 'PASS') {
      return { ...baseStyle, backgroundColor: 'var(--color-badge-success-bg)', color: 'var(--color-success)' };
    }
    if (result === 'FAIL') {
      return { ...baseStyle, backgroundColor: 'var(--color-badge-error-bg)', color: 'var(--color-error)' };
    }
    return { ...baseStyle, backgroundColor: 'var(--color-badge-warning-bg)', color: 'var(--color-warning)' };
  };

  // Measurement result color
  const getMeasurementResultColor = (result: string) => {
    return result === 'PASS' ? 'var(--color-success)' : 'var(--color-error)';
  };

  // Chart data for process failure rate
  const chartData =
    summary?.by_process.map((p) => ({
      name: p.process_name,
      total: p.total,
      fail: p.fail,
      rate: p.rate,
    })) || [];

  return (
    <div>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0, color: 'var(--color-text-primary)' }}>
            Process Defect Rate Analysis
          </h1>
          <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', margin: '8px 0 0 0' }}>
            Analyze defect rates and quality metrics by process
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button variant="secondary" onClick={() => setShowCharts(!showCharts)}>
            <BarChart3 size={16} style={{ marginRight: '5px' }} />
            {showCharts ? 'Hide Charts' : 'Show Charts'}
          </Button>
          <Button variant="secondary" onClick={handleExportCSV} disabled={data.length === 0}>
            <Download size={16} style={{ marginRight: '5px' }} />
            Export CSV
          </Button>
          <Button onClick={fetchData}>
            <RefreshCw size={16} style={{ marginRight: '5px' }} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filter Section */}
      <Card style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ width: '160px' }}>
            <Input
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <div style={{ width: '160px' }}>
            <Input
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <div style={{ width: '180px' }}>
            <Select
              label="Process"
              value={selectedProcessId?.toString() || ''}
              onChange={(e) => setSelectedProcessId(e.target.value ? Number(e.target.value) : undefined)}
              options={[
                { value: '', label: 'All Processes' },
                ...processes.map((p) => ({
                  value: p.id.toString(),
                  label: p.process_name_ko || p.process_name_en,
                })),
              ]}
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <div style={{ width: '140px' }}>
            <Select
              label="Result"
              value={selectedResult || ''}
              onChange={(e) => setSelectedResult(e.target.value as ProcessResult | undefined)}
              options={[
                { value: '', label: 'All' },
                { value: 'PASS', label: 'PASS' },
                { value: 'FAIL', label: 'FAIL' },
                { value: 'REWORK', label: 'REWORK' },
              ]}
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <Button onClick={handleApplyFilter}>
              <Filter size={16} style={{ marginRight: '5px' }} />
              Search
            </Button>
            <Button variant="secondary" onClick={handleResetFilter}>
              Reset
            </Button>
          </div>
        </div>
      </Card>

      {/* Statistics Cards */}
      {summary && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '15px',
            marginBottom: '20px',
          }}
        >
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                Total Count
              </div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: 'var(--color-brand)' }}>
                {summary.total_count.toLocaleString()}
              </div>
            </div>
          </Card>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>PASS</div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: 'var(--color-success)' }}>
                {summary.pass_count.toLocaleString()}
              </div>
            </div>
          </Card>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>FAIL</div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: 'var(--color-error)' }}>
                {summary.fail_count.toLocaleString()}
              </div>
            </div>
          </Card>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>Pass Rate</div>
              <div
                style={{
                  fontSize: '28px',
                  fontWeight: 'bold',
                  color: summary.pass_rate >= 95 ? 'var(--color-success)' : summary.pass_rate >= 85 ? 'var(--color-warning)' : 'var(--color-error)',
                }}
              >
                {summary.pass_rate.toFixed(1)}%
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Charts Section */}
      {showCharts && summary && chartData.length > 0 && (
        <Card style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: 'var(--color-text-primary)' }}>
            Defect Rate by Process
          </h3>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis
                  yAxisId="left"
                  orientation="left"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Count', angle: -90, position: 'insideLeft', fontSize: 12 }}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  domain={[0, 100]}
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Defect Rate (%)', angle: 90, position: 'insideRight', fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: '8px',
                    backgroundColor: 'var(--color-bg-primary)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-primary)',
                  }}
                  cursor={false}
                />
                <Legend />
                <Bar yAxisId="left" dataKey="total" name="Total" fill="var(--color-brand)" />
                <Bar yAxisId="left" dataKey="fail" name="Defect" fill="var(--color-error)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}

      {/* Data Table */}
      <Card>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            Loading data...
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>{error}</div>
        ) : data.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            No measurement data found.
          </div>
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', fontSize: '13px' }}>Time</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', fontSize: '13px' }}>LOT</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', fontSize: '13px' }}>
                      Serial/WIP
                    </th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', fontSize: '13px' }}>Process</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', fontSize: '13px' }}>Result</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', fontSize: '13px' }}>Operator</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', fontSize: '13px' }}>
                      Measurements
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item) => (
                    <>
                      <tr
                        key={item.id}
                        style={{
                          borderBottom: '1px solid var(--color-border)',
                          cursor: 'pointer',
                          backgroundColor: expandedRow === item.id ? 'var(--color-bg-secondary)' : 'transparent',
                        }}
                        onClick={() => setExpandedRow(expandedRow === item.id ? null : item.id)}
                      >
                        <td style={{ padding: '12px', fontSize: '13px' }}>
                          {format(new Date(item.started_at), 'MM-dd HH:mm')}
                        </td>
                        <td style={{ padding: '12px', fontSize: '13px', fontFamily: 'monospace' }}>
                          {item.lot_number}
                        </td>
                        <td style={{ padding: '12px', fontSize: '13px', fontFamily: 'monospace' }}>
                          {item.serial_number || item.wip_id || '-'}
                        </td>
                        <td style={{ padding: '12px', fontSize: '13px' }}>{item.process_name}</td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <span style={getResultBadgeStyle(item.result)}>{item.result}</span>
                        </td>
                        <td style={{ padding: '12px', fontSize: '13px' }}>{item.operator_name}</td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px' }}>
                            <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                              {item.measurements.length} items
                            </span>
                            {expandedRow === item.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </div>
                        </td>
                      </tr>
                      {/* Expanded Measurement Details */}
                      {expandedRow === item.id && (
                        <tr key={`${item.id}-details`}>
                          <td colSpan={7} style={{ padding: 0 }}>
                            <div
                              style={{
                                backgroundColor: 'var(--color-bg-tertiary)',
                                padding: '15px 20px',
                                borderBottom: '1px solid var(--color-border)',
                              }}
                            >
                              <div style={{ fontSize: '13px', fontWeight: '600', marginBottom: '10px' }}>
                                Measurement Details
                              </div>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                                {item.measurements.map((m: MeasurementHistoryItem, idx: number) => (
                                  <div
                                    key={idx}
                                    style={{
                                      backgroundColor: 'var(--color-bg-primary)',
                                      border: '1px solid var(--color-border)',
                                      borderRadius: '8px',
                                      padding: '10px 15px',
                                      minWidth: '180px',
                                    }}
                                  >
                                    <div
                                      style={{
                                        fontSize: '11px',
                                        color: 'var(--color-text-secondary)',
                                        marginBottom: '4px',
                                      }}
                                    >
                                      {m.name} ({m.code})
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                      <span
                                        style={{
                                          fontSize: '16px',
                                          fontWeight: 'bold',
                                          color: getMeasurementResultColor(m.result),
                                        }}
                                      >
                                        {m.value}
                                        {m.unit && (
                                          <span style={{ fontSize: '12px', fontWeight: 'normal', marginLeft: '2px' }}>
                                            {m.unit}
                                          </span>
                                        )}
                                      </span>
                                      {m.result === 'PASS' ? (
                                        <CheckCircle size={14} color="var(--color-success)" />
                                      ) : (
                                        <XCircle size={14} color="var(--color-error)" />
                                      )}
                                    </div>
                                    {m.spec && (
                                      <div
                                        style={{
                                          fontSize: '11px',
                                          color: 'var(--color-text-secondary)',
                                          marginTop: '4px',
                                        }}
                                      >
                                        {m.spec.min !== undefined && m.spec.max !== undefined
                                          ? `${m.spec.min} ~ ${m.spec.max}`
                                          : m.spec.target !== undefined
                                          ? `Target: ${m.spec.target}`
                                          : ''}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                              {item.duration_seconds !== undefined && (
                                <div
                                  style={{
                                    fontSize: '12px',
                                    color: 'var(--color-text-secondary)',
                                    marginTop: '10px',
                                  }}
                                >
                                  Duration: {Math.floor(item.duration_seconds / 60)}m {item.duration_seconds % 60}s
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '15px 0',
                  borderTop: '1px solid var(--color-border)',
                  marginTop: '15px',
                }}
              >
                <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                  Showing {(currentPage - 1) * pageSize + 1} - {Math.min(currentPage * pageSize, total)} of{' '}
                  {total.toLocaleString()} records
                </div>
                <div style={{ display: 'flex', gap: '5px' }}>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    Prev
                  </Button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum: number;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? 'primary' : 'secondary'}
                        size="sm"
                        onClick={() => setCurrentPage(pageNum)}
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
};

export default ProcessDefectRatePage;
