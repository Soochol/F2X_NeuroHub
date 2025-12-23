/**
 * F2X NeuroHub MES - Dashboard Page (Refactored)
 *
 * Features:
 * - Real-time WebSocket updates with polling fallback
 * - Enhanced KPI cards with trends
 * - Equipment status monitoring
 * - Defect trend visualization
 * - Mobile-responsive layout for shop floor tablets
 */

import { useEffect, useState, useMemo } from 'react';
import { Spin, Typography } from 'antd';
import {
  Package,
  Activity,
  CheckCircle,
  AlertTriangle,
  Gauge,
  Server,
} from 'lucide-react';
import { dashboardApi, equipmentApi } from '@/api';
import type { DashboardSummary, ProcessCycleTime, Equipment } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { useRealtimeMetrics } from '@/hooks/useRealtimeMetrics';
import { RealTimeIndicator } from '@/components/atoms/RealTimeIndicator';
import { EnhancedKPICard } from '@/components/molecules/EnhancedKPICard';
import type { KPIStatus } from '@/components/molecules/EnhancedKPICard';
import { ProcessFlowDiagram } from '@/components/charts';
import { CycleTimeChart } from '@/components/charts/CycleTimeChart';
import { DefectTrendChart } from '@/components/charts/DefectTrendChart';
import { EquipmentStatusPanel } from '@/components/organisms/dashboard/EquipmentStatusPanel';
import { LotHistoryTabs } from '@/components/organisms/dashboard/LotHistoryTabs';
import styles from './DashboardPage.module.css';

export const DashboardPage = () => {
  const { dashboardData, isConnected, lastUpdate, error: wsError, refetch } = useRealtimeMetrics();
  const [cycleTimes, setCycleTimes] = useState<ProcessCycleTime[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch additional data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cycleTimeData, equipmentData] = await Promise.all([
          dashboardApi.getCycleTimes(),
          equipmentApi.getActiveEquipment(),
        ]);
        setCycleTimes(cycleTimeData);
        setEquipment(equipmentData);
        setError(null);
      } catch (err: unknown) {
        setError(getErrorMessage(err, 'Failed to load dashboard data'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Refresh cycle times every 60 seconds
    const cycleTimeInterval = setInterval(async () => {
      try {
        const data = await dashboardApi.getCycleTimes();
        setCycleTimes(data);
      } catch (err) {
        console.error('Failed to refresh cycle times:', err);
      }
    }, 60000);

    return () => clearInterval(cycleTimeInterval);
  }, []);

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

    // Throughput (simplified - units per hour based on recent data)
    const throughput = dashboardData.total_completed > 0
      ? Math.round(dashboardData.total_completed / 8) // Assuming 8-hour shift
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

  // Determine KPI status colors
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

  if (isLoading && !dashboardData) {
    return (
      <div className={styles.loadingContainer}>
        <Spin size="large" />
        <span>Loading dashboard...</span>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className={styles.errorContainer}>
        Error: {error}
      </div>
    );
  }

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
