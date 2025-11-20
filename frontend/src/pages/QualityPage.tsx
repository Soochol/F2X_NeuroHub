/**
 * Quality Management Page
 */

import { useState, useEffect } from 'react';
import { Card, Button, Input } from '@/components/common';
import { analyticsApi } from '@/api';
import type { QualityMetrics, DefectAnalysis } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { format, subDays } from 'date-fns';

export const QualityPage = () => {
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null);
  const [defectAnalysis, setDefectAnalysis] = useState<DefectAnalysis | null>(null);
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
      const [quality, defects] = await Promise.all([
        analyticsApi.getQualityMetrics(startDate, endDate),
        analyticsApi.getDefects(startDate, endDate),
      ]);
      setQualityMetrics(quality);
      setDefectAnalysis(defects);
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load quality data'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyFilter = () => {
    fetchData();
  };

  const getPassRateColor = (rate: number) => {
    if (rate >= 95) return { bg: 'var(--color-success-light)', color: 'var(--color-success)', icon: '' };
    if (rate >= 85) return { bg: 'var(--color-warning-light)', color: 'var(--color-warning)', icon: '' };
    return { bg: 'var(--color-error-light)', color: 'var(--color-error)', icon: '' };
  };

  const getDefectRateColor = (rate: number) => {
    if (rate <= 5) return { bg: 'var(--color-success-light)', color: 'var(--color-success)', icon: '' };
    if (rate <= 15) return { bg: 'var(--color-warning-light)', color: 'var(--color-warning)', icon: '' };
    return { bg: 'var(--color-error-light)', color: 'var(--color-error)', icon: '' };
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>Quality Management</h1>
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
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <div style={{ width: '180px' }}>
            <Input
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
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
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>Loading quality metrics...</div>
        </Card>
      ) : error ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>{error}</div>
        </Card>
      ) : (
        <>
          {/* Quality Metrics Overview */}
          {qualityMetrics && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
                {/* Total Inspected */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Total Inspected</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-brand-500)', marginBottom: '5px' }}>
                      {qualityMetrics.total_inspected ?? 0}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>Units</div>
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
                        marginBottom: '5px',
                        ...getPassRateColor(qualityMetrics.pass_rate ?? 0),
                      }}
                    >
                      <span>{getPassRateColor(qualityMetrics.pass_rate ?? 0).icon}</span>
                      <span>{(qualityMetrics.pass_rate ?? 0).toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                      {qualityMetrics.pass_count ?? 0} / {qualityMetrics.total_inspected ?? 0} passed
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
                        marginBottom: '5px',
                        ...getDefectRateColor(qualityMetrics.defect_rate ?? 0),
                      }}
                    >
                      <span>{getDefectRateColor(qualityMetrics.defect_rate ?? 0).icon}</span>
                      <span>{(qualityMetrics.defect_rate ?? 0).toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                      {qualityMetrics.fail_count ?? 0} defects found
                    </div>
                  </div>
                </Card>

                {/* Rework Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Rework Rate</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--color-warning)', marginBottom: '5px' }}>
                      {(qualityMetrics.rework_rate ?? 0).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                      {qualityMetrics.rework_count ?? 0} units reworked
                    </div>
                  </div>
                </Card>
              </div>

              {/* Quality by Process */}
              <Card title="Quality Metrics by Process" style={{ marginBottom: '20px' }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                        <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Process</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Total</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Pass</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Fail</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Rework</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Pass Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(qualityMetrics.by_process ?? []).map((process, idx) => {
                        const passRateStyle = getPassRateColor(process.pass_rate ?? 0);
                        return (
                          <tr
                            key={idx}
                            style={{
                              borderBottom: '1px solid var(--color-border)',
                              backgroundColor: idx % 2 === 0 ? 'var(--color-bg-primary)' : 'var(--color-bg-secondary)',
                            }}
                          >
                            <td style={{ padding: '12px', fontWeight: '500' }}>{process.process_name}</td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>{process.total ?? 0}</td>
                            <td style={{ padding: '12px', textAlign: 'center', color: 'var(--color-success)' }}>
                              {process.pass ?? 0}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: 'var(--color-error)' }}>
                              {process.fail ?? 0}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: 'var(--color-warning)' }}>
                              {process.rework ?? 0}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>
                              <span
                                style={{
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  fontSize: '13px',
                                  fontWeight: '500',
                                  backgroundColor: passRateStyle.bg,
                                  color: passRateStyle.color,
                                }}
                              >
                                {passRateStyle.icon} {(process.pass_rate ?? 0).toFixed(1)}%
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          )}

          {/* Defect Analysis */}
          {defectAnalysis && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
                {/* Defects by Process */}
                <Card title="Defects by Process">
                  {!Array.isArray(defectAnalysis.by_process) || defectAnalysis.by_process.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-text-secondary)' }}>
                      No defects found in this period
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {defectAnalysis.by_process.map((process, idx) => (
                        <div
                          key={idx}
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '12px',
                            backgroundColor: 'var(--color-bg-secondary)',
                            borderRadius: '6px',
                            border: '1px solid var(--color-border)',
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: '500', marginBottom: '4px' }}>{process.process_name}</div>
                            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                              {process.defect_count ?? 0} defects ({(process.defect_rate ?? 0).toFixed(1)}% rate)
                            </div>
                          </div>
                          <div
                            style={{
                              width: '60px',
                              height: '60px',
                              borderRadius: '50%',
                              backgroundColor: 'var(--color-error-light)',
                              color: 'var(--color-error)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 'bold',
                              fontSize: '18px',
                            }}
                          >
                            {process.defect_count ?? 0}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>

                {/* Top Defect Types */}
                <Card title="Top Defect Types">
                  {!Array.isArray(defectAnalysis.top_defects) || defectAnalysis.top_defects.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px', color: 'var(--color-text-secondary)' }}>
                      No defects recorded
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {defectAnalysis.top_defects.slice(0, 10).map((defect, idx) => {
                        const percentage =
                          (defectAnalysis.total_defects ?? 0) > 0
                            ? ((defect.count ?? 0) / (defectAnalysis.total_defects ?? 1)) * 100
                            : 0;
                        return (
                          <div key={idx}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                              <span style={{ fontSize: '14px', fontWeight: '500' }}>{defect.defect_code}</span>
                              <span style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                                {defect.count} ({percentage.toFixed(1)}%)
                              </span>
                            </div>
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
                  )}
                </Card>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};
