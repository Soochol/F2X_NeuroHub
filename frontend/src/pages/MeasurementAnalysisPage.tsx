/**
 * Measurement Analysis Page - Quality Management
 *
 * Analyzes and visualizes individual measurement data from processes.
 * Features: measurement trends, distribution charts, spec compliance, outlier detection.
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, Button, Input, Select } from '@/components/common';
import { measurementsApi, processesApi } from '@/api';
import type {
  MeasurementHistory,
  MeasurementHistoryFilters,
  MeasurementHistoryItem,
  MeasurementCodeInfo,
  Process,
} from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { format, subDays } from 'date-fns';
import {
  Download,
  RefreshCw,
  Filter,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Activity,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';

// Measurement item statistics
interface MeasurementStats {
  code: string;
  name: string;
  unit?: string;
  count: number;
  min: number;
  max: number;
  avg: number;
  stdDev: number;
  specMin?: number;
  specMax?: number;
  passCount: number;
  failCount: number;
  passRate: number;
}

// Trend data point
interface TrendDataPoint {
  timestamp: string;
  value: number;
  result: string;
}

export const MeasurementAnalysisPage = () => {
  // Data states
  const [data, setData] = useState<MeasurementHistory[]>([]);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [availableCodes, setAvailableCodes] = useState<MeasurementCodeInfo[]>([]);
  const [measurementStats, setMeasurementStats] = useState<MeasurementStats[]>([]);
  const [selectedMeasurement, setSelectedMeasurement] = useState<string>('');
  const [trendData, setTrendData] = useState<TrendDataPoint[]>([]);

  // UI states
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingCodes, setIsLoadingCodes] = useState(true);
  const [error, setError] = useState('');

  // Filter states
  const [startDate, setStartDate] = useState(format(subDays(new Date(), 7), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [selectedProcessId, setSelectedProcessId] = useState<number | undefined>(undefined);

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

  // Load available measurement codes
  useEffect(() => {
    const loadMeasurementCodes = async () => {
      setIsLoadingCodes(true);
      try {
        const response = await measurementsApi.getMeasurementCodes(selectedProcessId);
        setAvailableCodes(response.codes);
      } catch (err) {
        console.error('Failed to load measurement codes:', err);
      } finally {
        setIsLoadingCodes(false);
      }
    };
    loadMeasurementCodes();
  }, [selectedProcessId]);

  // Calculate statistics for each measurement code
  const calculateStats = useCallback((records: MeasurementHistory[]) => {
    const measurementMap = new Map<string, MeasurementHistoryItem[]>();

    // Group measurements by code
    records.forEach((record) => {
      record.measurements.forEach((m) => {
        if (!measurementMap.has(m.code)) {
          measurementMap.set(m.code, []);
        }
        measurementMap.get(m.code)!.push(m);
      });
    });

    // Calculate statistics for each measurement code
    const stats: MeasurementStats[] = [];
    measurementMap.forEach((items, code) => {
      const values = items.map((i) => i.value);
      const passCount = items.filter((i) => i.result === 'PASS').length;
      const failCount = items.length - passCount;

      const min = Math.min(...values);
      const max = Math.max(...values);
      const avg = values.reduce((a, b) => a + b, 0) / values.length;
      const variance = values.reduce((sum, v) => sum + Math.pow(v - avg, 2), 0) / values.length;
      const stdDev = Math.sqrt(variance);

      const firstItem = items[0];
      stats.push({
        code,
        name: firstItem.name,
        unit: firstItem.unit,
        count: items.length,
        min,
        max,
        avg,
        stdDev,
        specMin: firstItem.spec?.min,
        specMax: firstItem.spec?.max,
        passCount,
        failCount,
        passRate: (passCount / items.length) * 100,
      });
    });

    setMeasurementStats(stats);

    // Auto-select first measurement if none selected
    if (stats.length > 0 && !selectedMeasurement) {
      setSelectedMeasurement(stats[0].code);
    }
  }, [selectedMeasurement]);

  // Build trend data for selected measurement
  const buildTrendData = useCallback((records: MeasurementHistory[], measurementCode: string) => {
    const trend: TrendDataPoint[] = [];

    records.forEach((record) => {
      const measurement = record.measurements.find((m) => m.code === measurementCode);
      if (measurement) {
        trend.push({
          timestamp: format(new Date(record.started_at), 'MM/dd HH:mm'),
          value: measurement.value,
          result: measurement.result,
        });
      }
    });

    // Sort by timestamp
    trend.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
    setTrendData(trend);
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
        skip: 0,
        limit: 500, // Get more data for analysis
      };

      const response = await measurementsApi.getMeasurementHistory(filters);
      setData(response.items);
      calculateStats(response.items);

      if (selectedMeasurement) {
        buildTrendData(response.items, selectedMeasurement);
      }
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load measurement data.'));
    } finally {
      setIsLoading(false);
    }
  }, [startDate, endDate, selectedProcessId, calculateStats, selectedMeasurement, buildTrendData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Update trend when selected measurement changes
  useEffect(() => {
    if (selectedMeasurement && data.length > 0) {
      buildTrendData(data, selectedMeasurement);
    }
  }, [selectedMeasurement, data, buildTrendData]);

  // Get selected measurement stats
  const selectedStats = measurementStats.find((s) => s.code === selectedMeasurement);

  // Handle filter apply
  const handleApplyFilter = () => {
    fetchData();
  };

  // Handle filter reset
  const handleResetFilter = () => {
    setStartDate(format(subDays(new Date(), 7), 'yyyy-MM-dd'));
    setEndDate(format(new Date(), 'yyyy-MM-dd'));
    setSelectedProcessId(undefined);
  };

  // Export CSV
  const handleExportCSV = () => {
    if (measurementStats.length === 0) return;

    const headers = ['Measurement', 'Code', 'Unit', 'Count', 'Min', 'Max', 'Avg', 'StdDev', 'Pass Rate'];
    const rows = measurementStats.map((s) => [
      s.name,
      s.code,
      s.unit || '-',
      s.count,
      s.min.toFixed(3),
      s.max.toFixed(3),
      s.avg.toFixed(3),
      s.stdDev.toFixed(3),
      `${s.passRate.toFixed(1)}%`,
    ]);

    const csvContent = [headers.join(','), ...rows.map((row) => row.map((cell) => `"${cell}"`).join(','))].join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `measurement_analysis_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`;
    link.click();
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0, color: 'var(--color-text-primary)' }}>
            Measurement Data Analysis
          </h1>
          <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)', margin: '8px 0 0 0' }}>
            Analyze measurement trends and statistics by process
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button variant="secondary" onClick={handleExportCSV} disabled={measurementStats.length === 0}>
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
          <div style={{ width: '200px' }}>
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

      {isLoading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            Loading data...
          </div>
        </Card>
      ) : error ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>{error}</div>
        </Card>
      ) : measurementStats.length === 0 ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ color: 'var(--color-text-secondary)', marginBottom: '20px' }}>
              No measurement data found for selected period.
            </div>

            {/* Show available measurement codes if any */}
            {!isLoadingCodes && availableCodes.length > 0 && (
              <div style={{ marginTop: '30px', textAlign: 'left' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '15px', color: 'var(--color-text-primary)' }}>
                  Available Measurement Codes ({availableCodes.length})
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
                  {availableCodes.map((code) => (
                    <div
                      key={code.code}
                      style={{
                        padding: '12px',
                        backgroundColor: 'var(--color-bg-secondary)',
                        borderRadius: '8px',
                        border: '1px solid var(--color-border)',
                      }}
                    >
                      <div style={{ fontWeight: '500', color: 'var(--color-text-primary)', marginBottom: '4px' }}>
                        {code.name}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                        Code: {code.code} | Unit: {code.unit || '-'} | {code.count} records
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--color-text-tertiary)', marginTop: '4px' }}>
                        Process IDs: {code.process_ids.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
                <p style={{ fontSize: '12px', color: 'var(--color-text-tertiary)', marginTop: '15px' }}>
                  * Try expanding the date range or selecting a different process.
                </p>
              </div>
            )}

            {!isLoadingCodes && availableCodes.length === 0 && (
              <div style={{ color: 'var(--color-text-tertiary)', fontSize: '13px' }}>
                No measurement data available. Data will appear here once measurements are sent from the Local PC App.
              </div>
            )}
          </div>
        </Card>
      ) : (
        <>
          {/* Measurement Selection */}
          <Card style={{ marginBottom: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', margin: 0, color: 'var(--color-text-primary)' }}>
                Select Measurement
              </h3>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {measurementStats.map((stat) => (
                <button
                  key={stat.code}
                  onClick={() => setSelectedMeasurement(stat.code)}
                  style={{
                    padding: '10px 16px',
                    border: selectedMeasurement === stat.code ? '2px solid var(--color-brand)' : '1px solid var(--color-border)',
                    borderRadius: '8px',
                    backgroundColor: selectedMeasurement === stat.code ? 'var(--color-brand-bg)' : 'var(--color-bg-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  <div style={{ fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' }}>
                    {stat.name}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    {stat.count} records | Pass Rate {stat.passRate.toFixed(1)}%
                  </div>
                </button>
              ))}
            </div>
          </Card>

          {/* Statistics Cards */}
          {selectedStats && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '15px',
                marginBottom: '20px',
              }}
            >
              <Card>
                <div style={{ textAlign: 'center' }}>
                  <Activity size={20} color="var(--color-brand)" style={{ marginBottom: '8px' }} />
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Average</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                    {selectedStats.avg.toFixed(3)}
                    {selectedStats.unit && <span style={{ fontSize: '14px', marginLeft: '2px' }}>{selectedStats.unit}</span>}
                  </div>
                </div>
              </Card>
              <Card>
                <div style={{ textAlign: 'center' }}>
                  <TrendingUp size={20} color="var(--color-info)" style={{ marginBottom: '8px' }} />
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Std Dev</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                    {selectedStats.stdDev.toFixed(3)}
                  </div>
                </div>
              </Card>
              <Card>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Min ~ Max</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                    {selectedStats.min.toFixed(2)} ~ {selectedStats.max.toFixed(2)}
                  </div>
                </div>
              </Card>
              <Card>
                <div style={{ textAlign: 'center' }}>
                  <CheckCircle size={20} color="var(--color-success)" style={{ marginBottom: '8px' }} />
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Pass Rate</div>
                  <div
                    style={{
                      fontSize: '24px',
                      fontWeight: 'bold',
                      color: selectedStats.passRate >= 95 ? 'var(--color-success)' : selectedStats.passRate >= 85 ? 'var(--color-warning)' : 'var(--color-error)',
                    }}
                  >
                    {selectedStats.passRate.toFixed(1)}%
                  </div>
                </div>
              </Card>
              {selectedStats.specMin !== undefined && selectedStats.specMax !== undefined && (
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <AlertTriangle size={20} color="var(--color-warning)" style={{ marginBottom: '8px' }} />
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Spec Range</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                      {selectedStats.specMin} ~ {selectedStats.specMax}
                    </div>
                  </div>
                </Card>
              )}
            </div>
          )}

          {/* Trend Chart */}
          {trendData.length > 0 && selectedStats && (
            <Card style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: 'var(--color-text-primary)' }}>
                {selectedStats.name} Trend
              </h3>
              <div style={{ width: '100%', height: 350 }}>
                <ResponsiveContainer>
                  <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="timestamp" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={60} />
                    <YAxis
                      tick={{ fontSize: 12 }}
                      domain={['auto', 'auto']}
                      label={{ value: selectedStats.unit || 'Value', angle: -90, position: 'insideLeft', fontSize: 12 }}
                    />
                    <Tooltip
                      contentStyle={{
                        borderRadius: '8px',
                        backgroundColor: 'var(--color-bg-primary)',
                        border: '1px solid var(--color-border)',
                      }}
                    />
                    <Legend />
                    {selectedStats.specMax !== undefined && (
                      <ReferenceLine y={selectedStats.specMax} stroke="var(--color-error)" strokeDasharray="5 5" label="USL" />
                    )}
                    {selectedStats.specMin !== undefined && (
                      <ReferenceLine y={selectedStats.specMin} stroke="var(--color-error)" strokeDasharray="5 5" label="LSL" />
                    )}
                    <ReferenceLine y={selectedStats.avg} stroke="var(--color-brand)" strokeDasharray="3 3" label="AVG" />
                    <Line
                      type="monotone"
                      dataKey="value"
                      name="Value"
                      stroke="var(--color-brand)"
                      strokeWidth={2}
                      dot={(props) => {
                        const { cx, cy, payload } = props;
                        const color = payload.result === 'PASS' ? 'var(--color-success)' : 'var(--color-error)';
                        return <circle cx={cx} cy={cy} r={4} fill={color} stroke={color} />;
                      }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}

          {/* Distribution Chart */}
          {selectedStats && (
            <Card style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: 'var(--color-text-primary)' }}>
                Pass/Fail by Measurement
              </h3>
              <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                  <BarChart
                    data={measurementStats}
                    margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        borderRadius: '8px',
                        backgroundColor: 'var(--color-bg-primary)',
                        border: '1px solid var(--color-border)',
                      }}
                    />
                    <Legend />
                    <Bar dataKey="passCount" name="Pass" stackId="a" fill="var(--color-success)" />
                    <Bar dataKey="failCount" name="Fail" stackId="a" fill="var(--color-error)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}

          {/* Statistics Table */}
          <Card>
            <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: 'var(--color-text-primary)' }}>
              Measurement Statistics
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', fontSize: '13px' }}>Measurement</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', fontSize: '13px' }}>Unit</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', fontSize: '13px' }}>Count</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', fontSize: '13px' }}>Avg</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', fontSize: '13px' }}>Std Dev</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', fontSize: '13px' }}>Min</th>
                    <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600', fontSize: '13px' }}>Max</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', fontSize: '13px' }}>Spec</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', fontSize: '13px' }}>Pass Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {measurementStats.map((stat) => (
                    <tr
                      key={stat.code}
                      style={{
                        borderBottom: '1px solid var(--color-border)',
                        backgroundColor: selectedMeasurement === stat.code ? 'var(--color-bg-secondary)' : 'transparent',
                        cursor: 'pointer',
                      }}
                      onClick={() => setSelectedMeasurement(stat.code)}
                    >
                      <td style={{ padding: '12px', fontSize: '13px' }}>
                        <div style={{ fontWeight: '500' }}>{stat.name}</div>
                        <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>{stat.code}</div>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', fontSize: '13px' }}>{stat.unit || '-'}</td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px' }}>{stat.count}</td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px', fontFamily: 'monospace' }}>
                        {stat.avg.toFixed(3)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px', fontFamily: 'monospace' }}>
                        {stat.stdDev.toFixed(3)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px', fontFamily: 'monospace' }}>
                        {stat.min.toFixed(3)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '13px', fontFamily: 'monospace' }}>
                        {stat.max.toFixed(3)}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', fontSize: '12px' }}>
                        {stat.specMin !== undefined && stat.specMax !== undefined
                          ? `${stat.specMin} ~ ${stat.specMax}`
                          : '-'}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span
                          style={{
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: '500',
                            backgroundColor:
                              stat.passRate >= 95
                                ? 'var(--color-badge-success-bg)'
                                : stat.passRate >= 85
                                ? 'var(--color-badge-warning-bg)'
                                : 'var(--color-badge-error-bg)',
                            color:
                              stat.passRate >= 95
                                ? 'var(--color-success)'
                                : stat.passRate >= 85
                                ? 'var(--color-warning)'
                                : 'var(--color-error)',
                          }}
                        >
                          {stat.passRate.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
};

export default MeasurementAnalysisPage;
