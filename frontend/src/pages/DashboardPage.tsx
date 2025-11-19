/**
 * Dashboard Page Component with CSS variable theming and Recharts
 */

import { useEffect, useState } from 'react';
import { dashboardApi } from '@/api';
import type { DashboardSummary } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { ProductionBarChart, DefectPieChart, ProcessWipChart } from '@/components/charts';

export const DashboardPage = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await dashboardApi.getSummary();
        setSummary(data);
      } catch (err: unknown) {
        setError(getErrorMessage(err, 'Failed to load dashboard data'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();

    const interval = setInterval(fetchSummary, 10000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '200px',
        color: 'var(--color-text-secondary)',
      }}>
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '24px',
        backgroundColor: 'var(--color-badge-error-bg)',
        color: 'var(--color-error)',
        borderRadius: '6px',
      }}>
        Error: {error}
      </div>
    );
  }

  if (!summary) {
    return (
      <div style={{ color: 'var(--color-text-secondary)', padding: '24px' }}>
        No data available
      </div>
    );
  }

  const productionChartData = summary.lots.slice(0, 5).map((lot) => ({
    name: lot.lot_number.slice(-6),
    started: lot.started_count,
    completed: lot.completed_count,
    defective: lot.defective_count,
  }));

  return (
    <div>
      <h1 style={{
        fontSize: '1.5rem',
        fontWeight: 700,
        marginBottom: '24px',
        color: 'var(--color-text-primary)',
      }}>
        Production Dashboard
      </h1>

      {/* KPI Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginBottom: '32px',
      }}>
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '12px' }}>
            Total Started
          </div>
          <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-brand)' }}>
            {summary.total_started}
          </div>
        </div>

        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '12px' }}>
            Total Completed
          </div>
          <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-success)' }}>
            {summary.total_completed}
          </div>
        </div>

        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '12px' }}>
            Total Defective
          </div>
          <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-error)' }}>
            {summary.total_defective}
          </div>
        </div>

        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '12px' }}>
            Defect Rate
          </div>
          <div style={{
            fontSize: '36px',
            fontWeight: 700,
            color: summary.defect_rate > 5 ? 'var(--color-error)' : 'var(--color-warning)',
          }}>
            {summary.defect_rate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '20px',
        marginBottom: '32px',
      }}>
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
        }}>
          <h2 style={{
            fontSize: '1.125rem',
            fontWeight: 600,
            marginBottom: '16px',
            color: 'var(--color-text-primary)',
          }}>
            Production by LOT
          </h2>
          <ProductionBarChart data={productionChartData} height={280} />
        </div>

        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
        }}>
          <h2 style={{
            fontSize: '1.125rem',
            fontWeight: 600,
            marginBottom: '16px',
            color: 'var(--color-text-primary)',
          }}>
            Pass/Fail Distribution
          </h2>
          <DefectPieChart
            passed={summary.total_completed - summary.total_defective}
            failed={summary.total_defective}
            height={280}
          />
        </div>
      </div>

      {/* Process WIP Chart */}
      <div style={{
        backgroundColor: 'var(--color-bg-secondary)',
        border: '1px solid var(--color-border)',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '24px',
      }}>
        <h2 style={{
          fontSize: '1.125rem',
          fontWeight: 600,
          marginBottom: '16px',
          color: 'var(--color-text-primary)',
        }}>
          Work In Progress by Process
        </h2>
        <ProcessWipChart data={summary.process_wip} height={300} />
      </div>

      {/* Active LOTs Table */}
      <div style={{
        backgroundColor: 'var(--color-bg-secondary)',
        border: '1px solid var(--color-border)',
        borderRadius: '8px',
        padding: '20px',
      }}>
        <h2 style={{
          fontSize: '1.125rem',
          fontWeight: 600,
          marginBottom: '16px',
          color: 'var(--color-text-primary)',
        }}>
          Active LOTs
        </h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>LOT Number</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Product Model</th>
                <th style={{ padding: '12px', textAlign: 'left', color: 'var(--color-text-secondary)' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Progress</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Started</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Completed</th>
                <th style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>Defective</th>
              </tr>
            </thead>
            <tbody>
              {summary.lots.map((lot, index) => (
                <tr
                  key={lot.lot_number}
                  style={{
                    borderBottom: '1px solid var(--color-border)',
                    backgroundColor: index % 2 === 0 ? 'transparent' : 'var(--color-bg-tertiary)',
                  }}
                >
                  <td style={{ padding: '12px', color: 'var(--color-text-primary)' }}>{lot.lot_number}</td>
                  <td style={{ padding: '12px', color: 'var(--color-text-primary)' }}>{lot.product_model_name}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: 500,
                      backgroundColor: lot.status === 'COMPLETED'
                        ? 'var(--color-badge-success-bg)'
                        : 'var(--color-brand-500)',
                      color: lot.status === 'COMPLETED'
                        ? 'var(--color-success)'
                        : 'var(--color-text-primary)',
                    }}>
                      {lot.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-primary)' }}>{lot.progress.toFixed(0)}%</td>
                  <td style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-primary)' }}>{lot.started_count}</td>
                  <td style={{ padding: '12px', textAlign: 'right', color: 'var(--color-text-primary)' }}>{lot.completed_count}</td>
                  <td style={{
                    padding: '12px',
                    textAlign: 'right',
                    color: lot.defective_count > 0 ? 'var(--color-error)' : 'var(--color-text-primary)',
                  }}>
                    {lot.defective_count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
