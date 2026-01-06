/**
 * Station Monitor Page
 *
 * Displays all registered stations with their status and batch overview.
 * Stations auto-register when they connect to the backend.
 */

import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Spin, Empty, Button, message } from 'antd';
import {
  Server,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertTriangle,
  Activity,
} from 'lucide-react';
import { useRegisteredStations, useDeleteStation } from '@/hooks/useStationMonitor';
import { StationCard } from '@/components/organisms/station';
import styles from './StationMonitorPage.module.css';

export const StationMonitorPage = () => {
  const navigate = useNavigate();
  const { data: stations, isLoading, isError, refetch, isFetching } = useRegisteredStations();
  const deleteStation = useDeleteStation();

  const handleDeleteStation = async (stationId: string) => {
    try {
      await deleteStation.mutateAsync(stationId);
      message.success('Station removed from registry');
    } catch {
      message.error('Failed to remove station');
    }
  };

  // Summary stats
  const summary = useMemo(() => {
    if (!stations) return { total: 0, connected: 0, disconnected: 0, running: 0 };

    const connected = stations.filter((s) => s.status === 'connected').length;
    const running = stations.reduce(
      (sum, s) => sum + (s.batches?.filter((b) => b.status === 'running').length || 0),
      0
    );

    return {
      total: stations.length,
      connected,
      disconnected: stations.length - connected,
      running,
    };
  }, [stations]);

  const handleStationClick = (stationId: string) => {
    const station = stations?.find((s) => s.id === stationId);
    if (station) {
      navigate(`/stations/${stationId}`, { state: { station } });
    }
  };

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <Server size={24} />
          <div>
            <h1 className={styles.title}>Station Monitor</h1>
            <p className={styles.subtitle}>
              Monitor all stations and their batch progress in real-time
            </p>
          </div>
        </div>

        <div className={styles.actions}>
          <Button
            icon={<RefreshCw size={16} className={isFetching ? styles.spinning : ''} />}
            onClick={() => refetch()}
            disabled={isFetching}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary */}
      <div className={styles.summary}>
        <div className={styles.summaryCard}>
          <Server size={20} />
          <div className={styles.summaryContent}>
            <span className={styles.summaryValue}>{summary.total}</span>
            <span className={styles.summaryLabel}>Total Stations</span>
          </div>
        </div>

        <div className={styles.summaryCard}>
          <Wifi size={20} className={styles.connectedIcon} />
          <div className={styles.summaryContent}>
            <span className={styles.summaryValue}>{summary.connected}</span>
            <span className={styles.summaryLabel}>Connected</span>
          </div>
        </div>

        <div className={styles.summaryCard}>
          <WifiOff size={20} className={styles.disconnectedIcon} />
          <div className={styles.summaryContent}>
            <span className={styles.summaryValue}>{summary.disconnected}</span>
            <span className={styles.summaryLabel}>Disconnected</span>
          </div>
        </div>

        <div className={styles.summaryCard}>
          <Activity size={20} className={styles.runningIcon} />
          <div className={styles.summaryContent}>
            <span className={styles.summaryValue}>{summary.running}</span>
            <span className={styles.summaryLabel}>Running Batches</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className={styles.content}>
        {isLoading ? (
          <div className={styles.loading}>
            <Spin size="large" />
            <p>Loading station status...</p>
          </div>
        ) : isError ? (
          <div className={styles.error}>
            <AlertTriangle size={48} />
            <h3>Unable to load station status</h3>
            <p>Check your network connection and try again</p>
            <Button onClick={() => refetch()}>Retry</Button>
          </div>
        ) : !stations || stations.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <div className={styles.emptyDescription}>
                <p>No stations registered</p>
                <p className={styles.emptyHint}>
                  Stations will appear here automatically when they connect to the backend
                </p>
              </div>
            }
          />
        ) : (
          <div className={styles.stationGrid}>
            {stations.map((station) => (
              <StationCard
                key={station.id}
                station={station}
                onClick={() => handleStationClick(station.id)}
                onDelete={handleDeleteStation}
                isDeleting={deleteStation.isPending}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StationMonitorPage;
