/**
 * Dashboard Page Component with improved layout and Process Flow visualization
 */

import { useEffect, useState } from 'react';
import { dashboardApi } from '@/api';
import type { DashboardSummary } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { ProductionBarChart, DefectPieChart, ProcessFlowDiagram } from '@/components/charts';
import { LotHistoryTabs } from '@/components/organisms/dashboard/LotHistoryTabs';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

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

  // Mock trend data (in real app, compare with previous period)
  const trends = {
    completion: 0,
    completed: 0,
    defectRate: 0,
  };

  const productionChartData = summary.lots.slice(0, 5).map((lot) => ({
    name: lot.lot_number.slice(-6),
    started: lot.started_count,
    completed: lot.completed_count,
    defective: lot.defective_count,
  }));

  const TrendIndicator = ({ value, suffix = '' }: { value: number; suffix?: string }) => {
    if (value === 0) {
      return (
        <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '2px', justifyContent: 'center' }}>
          <Minus size={12} /> 0{suffix}
        </span>
      );
    }
    if (value > 0) {
      return (
        <span style={{ fontSize: '12px', color: 'var(--color-success)', display: 'flex', alignItems: 'center', gap: '2px', justifyContent: 'center' }}>
          <TrendingUp size={12} /> +{value}{suffix}
        </span>
      );
    }
    return (
      <span style={{ fontSize: '12px', color: 'var(--color-error)', display: 'flex', alignItems: 'center', gap: '2px', justifyContent: 'center' }}>
        <TrendingDown size={12} /> {value}{suffix}
      </span>
    );
  };

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
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '16px',
        marginBottom: '24px',
      }}>
        {/* Completion Rate */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '16px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginBottom: '8px' }}>
            생산 진행률
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--color-brand-500)', marginBottom: '4px' }}>
            {completionRate.toFixed(1)}%
          </div>
          <TrendIndicator value={trends.completion} suffix="%" />
        </div>

        {/* Total Completed */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '16px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginBottom: '8px' }}>
            완료 수량
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--color-success)', marginBottom: '4px' }}>
            {summary.total_completed}
          </div>
          <TrendIndicator value={trends.completed} />
        </div>

        {/* Total Started */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '16px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginBottom: '8px' }}>
            시작 수량
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--color-info)', marginBottom: '4px' }}>
            {summary.total_started}
          </div>
        </div>

        {/* Defect Rate */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '16px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginBottom: '8px' }}>
            불량률
          </div>
          <div style={{
            fontSize: '28px',
            fontWeight: 700,
            color: summary.defect_rate > 5 ? 'var(--color-error)' : 'var(--color-warning)',
            marginBottom: '4px',
          }}>
            {summary.defect_rate.toFixed(1)}%
          </div>
          <TrendIndicator value={trends.defectRate} suffix="%" />
        </div>

        {/* Total Defective */}
        <div style={{
          backgroundColor: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '16px',
          textAlign: 'center',
        }}>
          <div style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginBottom: '8px' }}>
            불량 수량
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--color-error)', marginBottom: '4px' }}>
            {summary.total_defective}
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
          공정 흐름 현황
        </h2>
        <ProcessFlowDiagram data={summary.process_wip} />
      </div>

      {/* Charts Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '20px',
        marginBottom: '24px',
      }}>
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
            LOT별 생산 현황
          </h2>
          <ProductionBarChart data={productionChartData} height={250} />
        </div>

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
            합격/불합격 분포
          </h2>
          <DefectPieChart
            passed={summary.total_completed - summary.total_defective}
            failed={summary.total_defective}
            height={250}
          />
        </div>
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
          LOT 이력
        </h2>
        <LotHistoryTabs lots={summary.lots} />
      </div>
    </div>
  );
};
