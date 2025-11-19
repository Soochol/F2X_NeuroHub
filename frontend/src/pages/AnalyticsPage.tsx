/**
 * Analytics Page - Production Statistics and Cycle Time Analysis
 * Uses CSS variables for theming support
 */

import { useState, useEffect } from 'react';
import { Card, Button, Input } from '@/components/common';
import { analyticsApi } from '@/api';
import type { ProductionStats, CycleTimeAnalysis } from '@/types/api';
import { format, subDays } from 'date-fns';
import { CheckCircle, AlertTriangle, XCircle, RefreshCw, Lightbulb } from 'lucide-react';

export const AnalyticsPage = () => {
  const [productionStats, setProductionStats] = useState<ProductionStats | null>(null);
  const [cycleTimeAnalysis, setCycleTimeAnalysis] = useState<CycleTimeAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Date range filters
  const [startDate, setStartDate] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    setError('');
    try {
      const [stats, cycleTime] = await Promise.all([
        analyticsApi.getProductionStats(startDate, endDate),
        analyticsApi.getCycleTime(undefined, 30),
      ]);
      setProductionStats(stats);
      setCycleTimeAnalysis(cycleTime);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyFilter = () => {
    fetchData();
  };

  const formatCycleTime = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  const getCompletionColor = (rate: number) => {
    if (rate >= 95) return { bg: 'var(--color-success-bg)', color: 'var(--color-success)', icon: <CheckCircle size={24} /> };
    if (rate >= 80) return { bg: 'var(--color-warning-bg)', color: 'var(--color-warning)', icon: <AlertTriangle size={24} /> };
    return { bg: 'var(--color-error-bg)', color: 'var(--color-error)', icon: <XCircle size={24} /> };
  };

  const completionRate =
    productionStats && productionStats.total_serials > 0
      ? (productionStats.completed_serials / productionStats.total_serials) * 100
      : 0;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>Analytics & Reports</h1>
      </div>

      {/* Date Range Filter */}
      <Card style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ width: '180px' }}>
            <Input
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div style={{ width: '180px' }}>
            <Input label="End Date" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <div style={{ display: 'flex', gap: '10px', paddingBottom: '2px' }}>
            <Button onClick={handleApplyFilter}>Apply</Button>
            <Button
              variant="secondary"
              onClick={() => {
                setStartDate(format(subDays(new Date(), 30), 'yyyy-MM-dd'));
                setEndDate(format(new Date(), 'yyyy-MM-dd'));
              }}
            >
              Reset
            </Button>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>Loading analytics data...</div>
        </Card>
      ) : error ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>{error}</div>
        </Card>
      ) : (
        <>
          {/* Production Statistics Overview */}
          {productionStats && (
            <>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: '20px',
                  marginBottom: '20px',
                }}
              >
                {/* Total LOTs */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Total LOTs</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-brand)', marginBottom: '5px' }}>
                      {productionStats.total_lots}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Batches</div>
                  </div>
                </Card>

                {/* Total Serials */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Total Serials</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-brand-500)', marginBottom: '5px' }}>
                      {productionStats.total_serials}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Units Produced</div>
                  </div>
                </Card>

                {/* Completion Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Completion Rate</div>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        marginBottom: '5px',
                        ...getCompletionColor(completionRate),
                      }}
                    >
                      <span>{getCompletionColor(completionRate).icon}</span>
                      <span>{completionRate.toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                      {productionStats.completed_serials} / {productionStats.total_serials} completed
                    </div>
                  </div>
                </Card>

                {/* Pass Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Pass Rate</div>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        color: 'var(--color-success)',
                        marginBottom: '5px',
                      }}
                    >
                      <CheckCircle size={24} />
                      <span>{productionStats.pass_rate.toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                      {productionStats.pass_count} units passed
                    </div>
                  </div>
                </Card>

                {/* Defect Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Defect Rate</div>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        color: 'var(--color-error)',
                        marginBottom: '5px',
                      }}
                    >
                      <XCircle size={24} />
                      <span>{productionStats.defect_rate.toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                      {productionStats.fail_count} units failed
                    </div>
                  </div>
                </Card>

                {/* Rework Count */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Rework Count</div>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        color: 'var(--color-warning)',
                        marginBottom: '5px',
                      }}
                    >
                      <RefreshCw size={24} />
                      <span>{productionStats.rework_count}</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Units reworked</div>
                  </div>
                </Card>
              </div>
            </>
          )}

          {/* Cycle Time Analysis */}
          {cycleTimeAnalysis && (
            <>
              <Card title="Cycle Time Analysis by Process" style={{ marginBottom: '20px' }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                        <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Process</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Avg Cycle Time</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Min</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Max</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Median</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Total Records</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cycleTimeAnalysis.by_process.map((process, idx) => {
                        return (
                          <tr
                            key={idx}
                            style={{
                              borderBottom: '1px solid var(--color-border)',
                              backgroundColor: idx % 2 === 0 ? 'var(--color-bg-primary)' : 'var(--color-bg-secondary)',
                            }}
                          >
                            <td style={{ padding: '12px', fontWeight: '500' }}>{process.process_name}</td>
                            <td
                              style={{
                                padding: '12px',
                                textAlign: 'center',
                                fontWeight: '600',
                                color: 'var(--color-brand-500)',
                              }}
                            >
                              {formatCycleTime(process.avg_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: 'var(--color-success)' }}>
                              {formatCycleTime(process.min_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: 'var(--color-error)' }}>
                              {formatCycleTime(process.max_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>
                              {formatCycleTime(process.median_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                              {process.total_records}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Bottleneck Analysis */}
              {cycleTimeAnalysis.bottlenecks.length > 0 && (
                <Card title="Bottleneck Analysis" style={{ marginBottom: '20px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {cycleTimeAnalysis.bottlenecks.map((bottleneck, idx) => {
                      const maxCycleTime = Math.max(
                        ...cycleTimeAnalysis.by_process.map((p) => p.avg_cycle_time)
                      );
                      const percentage = (bottleneck.avg_cycle_time / maxCycleTime) * 100;

                      return (
                        <div
                          key={idx}
                          style={{
                            padding: '15px',
                            backgroundColor: 'var(--color-warning-bg)',
                            borderRadius: '6px',
                            border: '1px solid var(--color-warning)',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: '8px',
                            }}
                          >
                            <div>
                              <div style={{ fontWeight: '600', fontSize: '15px', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <AlertTriangle size={16} />
                                {bottleneck.process_name}
                              </div>
                              <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                                WIP Count: {bottleneck.wip_count} units
                              </div>
                            </div>
                            <div
                              style={{
                                fontSize: '20px',
                                fontWeight: 'bold',
                                color: 'var(--color-warning)',
                              }}
                            >
                              {formatCycleTime(bottleneck.avg_cycle_time)}
                            </div>
                          </div>

                          {/* Progress bar showing relative cycle time */}
                          <div
                            style={{
                              width: '100%',
                              height: '8px',
                              backgroundColor: 'var(--color-border)',
                              borderRadius: '4px',
                              overflow: 'hidden',
                            }}
                          >
                            <div
                              style={{
                                width: `${percentage}%`,
                                height: '100%',
                                backgroundColor: idx === 0 ? 'var(--color-error)' : idx === 1 ? 'var(--color-warning)' : 'var(--color-warning)',
                                borderRadius: '4px',
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <div
                    style={{
                      marginTop: '15px',
                      padding: '12px',
                      backgroundColor: 'var(--color-bg-tertiary)',
                      borderRadius: '6px',
                      fontSize: '13px',
                      color: 'var(--color-text-primary)',
                    }}
                  >
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      <Lightbulb size={16} />
                      <strong>Tip:</strong>
                    </span>{' '}
                    Bottlenecks are processes with longer cycle times and higher WIP counts.
                    Focus improvement efforts on these areas to increase throughput.
                  </div>
                </Card>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};
