/**
 * Dashboard Page Component with improved layout and Process Flow visualization
 */

import { useEffect, useState } from 'react';
import { dashboardApi } from '@/api';
import type { DashboardSummary } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { ProcessFlowDiagram } from '@/components/charts';
import { LotHistoryTabs } from '@/components/organisms/dashboard/LotHistoryTabs';

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

  // Calculate metrics
  const completionRate = summary.total_started > 0
    ? (summary.total_completed / summary.total_started) * 100
    : 0;



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
        gap: '16px',
        marginBottom: '24px',
      }}>
        {/* Started */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>
            Started
          </div>
          <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-info)', marginBottom: '8px' }}>
            {summary.total_started}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
            units in production
          </div>
        </div>

        {/* In Progress */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>
            In Progress
          </div>
          <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-warning)', marginBottom: '8px' }}>
            {summary.total_in_progress}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
            units being processed
          </div>
        </div>

        {/* Completed */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>
            Completed
          </div>
          <div style={{ fontSize: '36px', fontWeight: 700, color: 'var(--color-success)', marginBottom: '8px' }}>
            {summary.total_completed}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
            units finished
          </div>
        </div>

        {/* Completion Rate */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>
            Completion Rate
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-brand)', marginBottom: '4px' }}>
            {summary.total_completed} / {summary.total_started}
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-brand)', marginBottom: '8px' }}>
            ({completionRate.toFixed(1)}%)
          </div>
        </div>

        {/* Defect Rate */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>
            Defect Rate
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: summary.defect_rate > 5 ? 'var(--color-error)' : 'var(--color-warning)', marginBottom: '4px' }}>
            {summary.total_defective} / {summary.total_completed}
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: 700,
            color: summary.defect_rate > 5 ? 'var(--color-error)' : 'var(--color-warning)',
            marginBottom: '8px',
          }}>
            ({summary.defect_rate.toFixed(1)}%)
          </div>
        </div>
      </div>

      {/* Process Flow Diagram */}
      <div style={{
        backgroundColor: 'var(--color-bg-secondary)',
        border: '1px solid var(--color-border)',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '24px',
      }}>
        <h2 style={{
          fontSize: '1rem',
          fontWeight: 600,
          marginBottom: '12px',
          color: 'var(--color-text-primary)',
        }}>
          Process Flow Status
        </h2>
        <ProcessFlowDiagram data={summary.process_wip} />
      </div>



      {/* LOT History Tabs */}
      <div style={{
        backgroundColor: 'var(--color-bg-secondary)',
        border: '1px solid var(--color-border)',
        borderRadius: '8px',
        padding: '20px',
      }}>
        <h2 style={{
          fontSize: '1rem',
          fontWeight: 600,
          marginBottom: '16px',
          color: 'var(--color-text-primary)',
        }}>
          LOT History
        </h2>
        <LotHistoryTabs lots={summary.lots} />
      </div>
    </div>
  );
};
