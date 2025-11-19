/**
 * Quality Management Page
 */

import { useState, useEffect } from 'react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { analyticsApi } from '@/api';
import type { QualityMetrics, DefectAnalysis } from '@/types/api';
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
    } catch (err: any) {
      setError(err.message || 'Failed to load quality data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyFilter = () => {
    fetchData();
  };

  const getPassRateColor = (rate: number) => {
    if (rate >= 95) return { bg: '#d5f4e6', color: '#27ae60', icon: '✅' };
    if (rate >= 85) return { bg: '#fff3cd', color: '#f39c12', icon: '⚠️' };
    return { bg: '#fee', color: '#e74c3c', icon: '❌' };
  };

  const getDefectRateColor = (rate: number) => {
    if (rate <= 5) return { bg: '#d5f4e6', color: '#27ae60', icon: '✅' };
    if (rate <= 15) return { bg: '#fff3cd', color: '#f39c12', icon: '⚠️' };
    return { bg: '#fee', color: '#e74c3c', icon: '❌' };
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>Quality Management</h1>
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
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>Loading quality metrics...</div>
        </Card>
      ) : error ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px', color: '#e74c3c' }}>{error}</div>
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
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Total Inspected</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#3498db', marginBottom: '5px' }}>
                      {qualityMetrics.total_inspected}
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>Units</div>
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
                        marginBottom: '5px',
                        ...getPassRateColor(qualityMetrics.pass_rate),
                      }}
                    >
                      <span>{getPassRateColor(qualityMetrics.pass_rate).icon}</span>
                      <span>{qualityMetrics.pass_rate.toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                      {qualityMetrics.pass_count} / {qualityMetrics.total_inspected} passed
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
                        marginBottom: '5px',
                        ...getDefectRateColor(qualityMetrics.defect_rate),
                      }}
                    >
                      <span>{getDefectRateColor(qualityMetrics.defect_rate).icon}</span>
                      <span>{qualityMetrics.defect_rate.toFixed(1)}%</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                      {qualityMetrics.fail_count} defects found
                    </div>
                  </div>
                </Card>

                {/* Rework Rate */}
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '10px' }}>Rework Rate</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f39c12', marginBottom: '5px' }}>
                      {qualityMetrics.rework_rate.toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                      {qualityMetrics.rework_count} units reworked
                    </div>
                  </div>
                </Card>
              </div>

              {/* Quality by Process */}
              <Card title="Quality Metrics by Process" style={{ marginBottom: '20px' }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                        <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Process</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Total</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Pass</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Fail</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Rework</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Pass Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {qualityMetrics.by_process.map((process, idx) => {
                        const passRateStyle = getPassRateColor(process.pass_rate);
                        return (
                          <tr
                            key={idx}
                            style={{
                              borderBottom: '1px solid #f0f0f0',
                              backgroundColor: idx % 2 === 0 ? 'white' : '#f9f9f9',
                            }}
                          >
                            <td style={{ padding: '12px', fontWeight: '500' }}>{process.process_name}</td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>{process.total}</td>
                            <td style={{ padding: '12px', textAlign: 'center', color: '#27ae60' }}>
                              {process.pass}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: '#e74c3c' }}>
                              {process.fail}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'center', color: '#f39c12' }}>
                              {process.rework}
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
                                {passRateStyle.icon} {process.pass_rate.toFixed(1)}%
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
                  {defectAnalysis.by_process.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>
                      No defects found in this period 🎉
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
                            backgroundColor: '#f8f9fa',
                            borderRadius: '6px',
                            border: '1px solid #e0e0e0',
                          }}
                        >
                          <div>
                            <div style={{ fontWeight: '500', marginBottom: '4px' }}>{process.process_name}</div>
                            <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                              {process.defect_count} defects ({process.defect_rate.toFixed(1)}% rate)
                            </div>
                          </div>
                          <div
                            style={{
                              width: '60px',
                              height: '60px',
                              borderRadius: '50%',
                              backgroundColor: '#fee',
                              color: '#e74c3c',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 'bold',
                              fontSize: '18px',
                            }}
                          >
                            {process.defect_count}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>

                {/* Top Defect Types */}
                <Card title="Top Defect Types">
                  {defectAnalysis.top_defects.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>
                      No defects recorded 🎉
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {defectAnalysis.top_defects.slice(0, 10).map((defect, idx) => {
                        const percentage =
                          defectAnalysis.total_defects > 0
                            ? (defect.count / defectAnalysis.total_defects) * 100
                            : 0;
                        return (
                          <div key={idx}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                              <span style={{ fontSize: '14px', fontWeight: '500' }}>{defect.defect_code}</span>
                              <span style={{ fontSize: '14px', color: '#7f8c8d' }}>
                                {defect.count} ({percentage.toFixed(1)}%)
                              </span>
                            </div>
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
