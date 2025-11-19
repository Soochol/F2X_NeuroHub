/**
 * Dashboard Page Component
 */

import { useEffect, useState } from 'react';
import { dashboardApi } from '@/api';
import type { DashboardSummary } from '@/types/api';

export const DashboardPage = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await dashboardApi.getSummary();
        setSummary(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();

    // Poll every 10 seconds
    const interval = setInterval(fetchSummary, 10000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return <div>Loading dashboard...</div>;
  }

  if (error) {
    return <div style={{ color: '#e74c3c' }}>Error: {error}</div>;
  }

  if (!summary) {
    return <div>No data available</div>;
  }

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>
        Production Dashboard
      </h1>

      {/* KPI Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginBottom: '30px',
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}>
          <div style={{ color: '#7f8c8d', fontSize: '14px', marginBottom: '10px' }}>Total Started</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#3498db' }}>
            {summary.total_started}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}>
          <div style={{ color: '#7f8c8d', fontSize: '14px', marginBottom: '10px' }}>Total Completed</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#27ae60' }}>
            {summary.total_completed}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}>
          <div style={{ color: '#7f8c8d', fontSize: '14px', marginBottom: '10px' }}>Total Defective</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#e74c3c' }}>
            {summary.total_defective}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}>
          <div style={{ color: '#7f8c8d', fontSize: '14px', marginBottom: '10px' }}>Defect Rate</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: summary.defect_rate > 5 ? '#e74c3c' : '#f39c12' }}>
            {summary.defect_rate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Active LOTs */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '20px',
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '15px' }}>Active LOTs</h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                <th style={{ padding: '10px', textAlign: 'left' }}>LOT Number</th>
                <th style={{ padding: '10px', textAlign: 'left' }}>Product Model</th>
                <th style={{ padding: '10px', textAlign: 'left' }}>Status</th>
                <th style={{ padding: '10px', textAlign: 'right' }}>Progress</th>
                <th style={{ padding: '10px', textAlign: 'right' }}>Started</th>
                <th style={{ padding: '10px', textAlign: 'right' }}>Completed</th>
                <th style={{ padding: '10px', textAlign: 'right' }}>Defective</th>
              </tr>
            </thead>
            <tbody>
              {summary.lots.map((lot) => (
                <tr key={lot.lot_number} style={{ borderBottom: '1px solid #f0f0f0' }}>
                  <td style={{ padding: '10px' }}>{lot.lot_number}</td>
                  <td style={{ padding: '10px' }}>{lot.product_model_name}</td>
                  <td style={{ padding: '10px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      backgroundColor: lot.status === 'COMPLETED' ? '#d5f4e6' : '#e3f2fd',
                      color: lot.status === 'COMPLETED' ? '#27ae60' : '#3498db',
                    }}>
                      {lot.status}
                    </span>
                  </td>
                  <td style={{ padding: '10px', textAlign: 'right' }}>{lot.progress.toFixed(0)}%</td>
                  <td style={{ padding: '10px', textAlign: 'right' }}>{lot.started_count}</td>
                  <td style={{ padding: '10px', textAlign: 'right' }}>{lot.completed_count}</td>
                  <td style={{ padding: '10px', textAlign: 'right', color: lot.defective_count > 0 ? '#e74c3c' : 'inherit' }}>
                    {lot.defective_count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Process WIP */}
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '15px' }}>Process WIP</h2>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {summary.process_wip.map((process) => (
            <div
              key={process.process_name}
              style={{
                padding: '15px',
                border: '1px solid #e0e0e0',
                borderRadius: '4px',
                minWidth: '150px',
              }}
            >
              <div style={{ fontSize: '14px', color: '#7f8c8d', marginBottom: '5px' }}>
                {process.process_name}
              </div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3498db' }}>
                {process.wip_count}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
