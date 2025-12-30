/**
 * F2X NeuroHub MES - Dashboard Page
 *
 * Features:
 * - Real-time WebSocket updates with polling fallback
 * - TanStack Query for data fetching and caching
 * - Enhanced KPI cards with trends
 * - Equipment status monitoring
 * - Defect trend visualization
 * - Mobile-responsive layout for shop floor tablets
 */

import { useMemo } from 'react';
import { Spin, Typography } from 'antd';
import {
  Package,
  Activity,
  CheckCircle,
  AlertTriangle,
  Gauge,
  Server,
} from 'lucide-react';
import { useRealtimeMetrics } from '@/hooks/useRealtimeMetrics';
import { useCycleTimes, useActiveEquipment } from '@/hooks';
import { RealTimeIndicator } from '@/components/atoms/RealTimeIndicator';
import { EnhancedKPICard } from '@/components/molecules/EnhancedKPICard';
import type { KPIStatus } from '@/components/molecules/EnhancedKPICard';
import { ProcessFlowDiagram, CycleTimeChart, DefectTrendChart } from '@/components/organisms/charts';
import { EquipmentStatusPanel } from '@/components/organisms/dashboard/EquipmentStatusPanel';
import { LotHistoryTabs } from '@/components/organisms/dashboard/LotHistoryTabs';
import styles from './DashboardPage.module.css';

/** Shift duration constant for throughput calculation */
const SHIFT_HOURS = 8;

export const DashboardPage = () => {
  // Real-time metrics via WebSocket with polling fallback
  const { dashboardData, isConnected, lastUpdate } = useRealtimeMetrics();

  // TanStack Query hooks for additional data
  const { data: cycleTimes = [], isLoading: isCycleTimesLoading } = useCycleTimes(7);
  const { data: equipment = [], isLoading: isEquipmentLoading } = useActiveEquipment();

  const isLoading = isCycleTimesLoading || isEquipmentLoading;

  // Calculate KPI values
  const kpiData = useMemo(() => {
    if (!dashboardData) return null;

    const totalWip = dashboardData.process_wip?.reduce((sum, p) => sum + p.wip_count, 0) || 0;
    const passRate = dashboardData.total_completed > 0
      ? ((dashboardData.total_completed - dashboardData.total_defective) / dashboardData.total_completed) * 100
      : 100;

    // Equipment stats
    const equipmentOnline = equipment.filter(e =>
      e.status === 'AVAILABLE' || e.status === 'IN_USE'
    ).length;
    const equipmentTotal = equipment.length;

    // Throughput calculation
    const throughput = dashboardData.total_completed > 0
      ? Math.round(dashboardData.total_completed / SHIFT_HOURS)
      : 0;

    return {
      production: dashboardData.total_completed,
      wip: totalWip,
      passRate: passRate.toFixed(1),
      defectRate: dashboardData.defect_rate.toFixed(1),
      equipmentOnline,
      equipmentTotal,
      throughput,
    };
  }, [dashboardData, equipment]);

  // KPI status color helpers
  const getPassRateStatus = (rate: number): KPIStatus => {
    if (rate >= 98) return 'success';
    if (rate >= 95) return 'warning';
    return 'error';
  };

  const getDefectRateStatus = (rate: number): KPIStatus => {
    if (rate <= 2) return 'success';
    if (rate <= 5) return 'warning';
    return 'error';
  };

  const getEquipmentStatus = (online: number, total: number): KPIStatus => {
    if (total === 0) return 'neutral';
    const ratio = online / total;
    if (ratio >= 1) return 'success';
    if (ratio >= 0.8) return 'warning';
    return 'error';
  };

  // Loading state
  if (isLoading && !dashboardData) {
    return (
      <div className={styles.loadingContainer}>
        <Spin size="large" />
        <span>Loading dashboard...</span>
      </div>
    );
  }

  // Empty state
  if (!dashboardData || !kpiData) {
    return (
      <div className={styles.emptyContainer}>
        No data available
      </div>
    );
  }

  return (
    <div className={styles.page}>
      {/* Header with title and real-time indicator */}
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Production Dashboard</h1>
        <RealTimeIndicator
          isConnected={isConnected}
          lastUpdate={lastUpdate}
        />
      </div>

      {/* KPI Cards Grid */}
      <div className={styles.kpiGrid}>
        <EnhancedKPICard
          title="Production Today"
          value={kpiData.production}
          subtitle="units completed"
          icon={<Package size={18} />}
          status="info"
        />

        <EnhancedKPICard
          title="WIP Total"
          value={kpiData.wip}
          subtitle="units in progress"
          icon={<Activity size={18} />}
          status={kpiData.wip > 50 ? 'warning' : 'neutral'}
        />

        <EnhancedKPICard
          title="Pass Rate"
          value={`${kpiData.passRate}%`}
          subtitle="quality rate"
          icon={<CheckCircle size={18} />}
          status={getPassRateStatus(parseFloat(kpiData.passRate))}
        />

        <EnhancedKPICard
          title="Defect Rate"
          value={`${kpiData.defectRate}%`}
          subtitle={`${dashboardData.total_defective} defects`}
          icon={<AlertTriangle size={18} />}
          status={getDefectRateStatus(parseFloat(kpiData.defectRate))}
        />

        <EnhancedKPICard
          title="Equipment"
          value={`${kpiData.equipmentOnline}/${kpiData.equipmentTotal}`}
          subtitle="online"
          icon={<Server size={18} />}
          status={getEquipmentStatus(kpiData.equipmentOnline, kpiData.equipmentTotal)}
        />

        <EnhancedKPICard
          title="Throughput"
          value={kpiData.throughput}
          subtitle="units/hour"
          icon={<Gauge size={18} />}
          status="neutral"
        />
      </div>

      {/* Real-time Monitoring Section */}
      <div className={styles.monitoringRow}>
        <div className={styles.processFlowSection}>
          <Typography.Title level={4} style={{ margin: '0 0 16px 0' }}>Process Flow Status</Typography.Title>
          <ProcessFlowDiagram data={dashboardData.process_wip} />
        </div>

        <div className={styles.equipmentSection}>
          <EquipmentStatusPanel />
        </div>
      </div>

      {/* Charts Section */}
      <div className={styles.chartsRow}>
        <div className={styles.chartCard}>
          <CycleTimeChart data={cycleTimes} />
        </div>

        <div className={styles.chartCard}>
          <DefectTrendChart days={7} thresholdPercent={5} />
        </div>
      </div>

      {/* LOT History Section */}
      <div className={styles.lotHistorySection}>
        <Typography.Title level={4} style={{ margin: '0 0 16px 0' }}>LOT History</Typography.Title>
        <LotHistoryTabs lots={dashboardData.lots} />
      </div>
    </div>
  );
};
