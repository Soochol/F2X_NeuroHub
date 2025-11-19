/**
 * Analytics Page - Production Statistics and Cycle Time Analysis
 */

import { useState, useEffect } from 'react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { analyticsApi } from '@/api';
import type { ProductionStats, CycleTimeAnalysis } from '@/types/api';
import { format, subDays } from 'date-fns';

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
    if (rate >= 95) return { bg: '#d5f4e6', color: '#27ae60', icon: '✅' };
    if (rate >= 80) return { bg: '#fff3cd', color: '#f39c12', icon: '⚠️' };
    return { bg: '#fee', color: '#e74c3c', icon: '❌' };
  };

  const completionRate =
    productionStats && productionStats.total_serials > 0
      ? (productionStats.completed_serials / productionStats.total_serials) * 100
      : 0;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>Analytics & Reports</h1>
      </div>

      {/* Date Range Filter */}
      <Card style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
          <div style={{ width: '200px' }}>
            <Input
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div style={{ width: '200px' }}>
            <Input label="End Date" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <Button onClick={handleApplyFilter}>Apply</Button>
          <Button
            variant="secondary"
            onClick={() => {
              setStartDate(format(subDays(new Date(), 30), 'yyyy-MM-dd'));
              setEndDate(format(new Date(), 'yyyy-MM-dd'));
            }}
          >
            Reset (Last 30 Days)
          </Button>
        </div>
      </Card>

      {isLoading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>Loading analytics data...</div>
        </Card>
      ) : error ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: '#e74c3c' }}>{error}</div>
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
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Total LOTs</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#9b59b6', marginBottom: '5px' }}>
                      {productionStats.total_lots}
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Batches</div>
                  </div>
                </Card>

                {/* Total Serials */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Total Serials</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#3498db', marginBottom: '5px' }}>
                      {productionStats.total_serials}
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Units Produced</div>
                  </div>
                </Card>

                {/* Completion Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Completion Rate</div>
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
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                      {productionStats.completed_serials} / {productionStats.total_serials} completed
                    </div>
                  </div>
                </Card>

                {/* Pass Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Pass Rate</div>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        color: '#27ae60',
                        marginBottom: '5px',
                      }}
                    >
                      <span>✅</span>
                      <span>{productionStats.pass_rate.toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                      {productionStats.pass_count} units passed
                    </div>
                  </div>
                </Card>

                {/* Defect Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Defect Rate</div>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        color: '#e74c3c',
                        marginBottom: '5px',
                      }}
                    >
                      <span>❌</span>
                      <span>{productionStats.defect_rate.toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                      {productionStats.fail_count} units failed
                    </div>
                  </div>
                </Card>

                {/* Rework Count */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Rework Count</div>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '32px',
                        fontWeight: 'bold',
                        color: '#f39c12',
                        marginBottom: '5px',
                      }}
                    >
                      <span>🔄</span>
                      <span>{productionStats.rework_count}</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Units reworked</div>
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
                      <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
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
                              borderBottom: '1px solid #f0f0f0',
                              backgroundColor: idx % 2 === 0 ? 'white' : '#f9f9f9',
                            }}
                          >
                            <td style={{ padding: '12px', fontWeight: '500' }}>{process.process_name}</td>
                            <td
                              style={{
                                padding: '12px',
                                textAlign: 'center',
                                fontWeight: '600',
                                color: '#3498db',
                              }}
                            >
                              {formatCycleTime(process.avg_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: '#27ae60' }}>
                              {formatCycleTime(process.min_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: '#e74c3c' }}>
                              {formatCycleTime(process.max_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>
                              {formatCycleTime(process.median_cycle_time)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: '#7f8c8d' }}>
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
                            backgroundColor: '#fff3cd',
                            borderRadius: '6px',
                            border: '1px solid #f39c12',
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
                              <div style={{ fontWeight: '600', fontSize: '15px', marginBottom: '4px' }}>
                                ⚠️ {bottleneck.process_name}
                              </div>
                              <div style={{ fontSize: '13px', color: '#7f8c8d' }}>
                                WIP Count: {bottleneck.wip_count} units
                              </div>
                            </div>
                            <div
                              style={{
                                fontSize: '20px',
                                fontWeight: 'bold',
                                color: '#e67e22',
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
                              backgroundColor: '#e0e0e0',
                              borderRadius: '4px',
                              overflow: 'hidden',
                            }}
                          >
                            <div
                              style={{
                                width: `${percentage}%`,
                                height: '100%',
                                backgroundColor: idx === 0 ? '#e74c3c' : idx === 1 ? '#e67e22' : '#f39c12',
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
                      backgroundColor: '#e3f2fd',
                      borderRadius: '6px',
                      fontSize: '13px',
                      color: '#2c3e50',
                    }}
                  >
                    💡 <strong>Tip:</strong> Bottlenecks are processes with longer cycle times and higher WIP counts.
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
