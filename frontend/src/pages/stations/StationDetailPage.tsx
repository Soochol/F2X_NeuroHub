/**
 * Station Detail Page
 *
 * Displays detailed information for a single station including batches and health metrics.
 * Uses the station registry from backend - stations auto-register on connection.
 */

import { useState, useMemo, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Spin, Button, Tabs, Empty, Badge, Select } from 'antd';
import {
  ArrowLeft,
  Server,
  Activity,
  Package,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertTriangle,
} from 'lucide-react';
import {
  useRegisteredStation,
  useStationBatches,
  useStationBatchStatistics,
  useStationWebSocket,
} from '@/hooks/useStationMonitor';
import { BatchCard, HealthMetrics } from '@/components/organisms/station';
import type { Station, StationWebSocketMessage } from '@/types/station';
import styles from './StationDetailPage.module.css';

type BatchFilter = 'all' | 'running' | 'idle' | 'completed' | 'error';

export const StationDetailPage = () => {
  const { stationId } = useParams<{ stationId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  // Get station from navigation state or fetch from backend
  const stationFromState = location.state?.station as Station | undefined;

  const [batchFilter, setBatchFilter] = useState<BatchFilter>('all');
  const [activeTab, setActiveTab] = useState('batches');

  // Fetch station from registry if not in state
  const { data: registeredStation, isLoading: isStationLoading, refetch: refetchStation } =
    useRegisteredStation(stationFromState ? null : stationId || null);

  // Use station from state or fetched data
  const station = stationFromState || registeredStation;

  // Queries for batches
  const { data: batches, isLoading: isBatchesLoading, refetch: refetchBatches } =
    useStationBatches(station?.host || '', station?.port || 0);

  const { data: statistics } = useStationBatchStatistics(
    station?.host || '',
    station?.port || 0
  );

  // WebSocket for real-time updates
  const batchIds = useMemo(() => batches?.map((b) => b.id) || [], [batches]);

  const handleWebSocketMessage = useCallback(
    (wsMessage: StationWebSocketMessage) => {
      // Refetch on important events
      if (
        wsMessage.type === 'batch_status' ||
        wsMessage.type === 'step_complete' ||
        wsMessage.type === 'sequence_complete'
      ) {
        refetchBatches();
      }
    },
    [refetchBatches]
  );

  const { isConnected: wsConnected } = useStationWebSocket(
    station?.host || '',
    station?.port || 0,
    {
      onMessage: handleWebSocketMessage,
      batchIds,
    }
  );

  // Filter batches
  const filteredBatches = useMemo(() => {
    if (!batches) return [];
    if (batchFilter === 'all') return batches;
    return batches.filter((b) => {
      switch (batchFilter) {
        case 'running':
          return b.status === 'running' || b.status === 'starting';
        case 'idle':
          return b.status === 'idle';
        case 'completed':
          return b.status === 'completed';
        case 'error':
          return b.status === 'error';
        default:
          return true;
      }
    });
  }, [batches, batchFilter]);

  // Count by status
  const statusCounts = useMemo(() => {
    if (!batches) return { all: 0, running: 0, idle: 0, completed: 0, error: 0 };
    return {
      all: batches.length,
      running: batches.filter((b) => b.status === 'running' || b.status === 'starting').length,
      idle: batches.filter((b) => b.status === 'idle').length,
      completed: batches.filter((b) => b.status === 'completed').length,
      error: batches.filter((b) => b.status === 'error').length,
    };
  }, [batches]);

  if (!station && !isStationLoading) {
    return (
      <div className={styles.notFound}>
        <AlertTriangle size={48} />
        <h2>Station not found</h2>
        <p>The requested station does not exist or has not registered</p>
        <Button type="primary" onClick={() => navigate('/stations')}>
          Back to Station List
        </Button>
      </div>
    );
  }

  const isLoading = isStationLoading || isBatchesLoading;
  const isConnected = station?.status === 'connected';

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <Button
            type="text"
            icon={<ArrowLeft size={20} />}
            onClick={() => navigate('/stations')}
            className={styles.backButton}
          />

          <div className={styles.stationInfo}>
            <div className={styles.iconWrapper}>
              <Server size={20} />
            </div>
            <div>
              <div className={styles.titleRow}>
                <h1 className={styles.title}>{station?.name || 'Loading...'}</h1>
                <Badge
                  status={isConnected ? 'success' : 'error'}
                  text={
                    <span className={styles.connectionBadge}>
                      {isConnected ? (
                        <>
                          <Wifi size={14} />
                          Connected
                        </>
                      ) : (
                        <>
                          <WifiOff size={14} />
                          Disconnected
                        </>
                      )}
                    </span>
                  }
                />
                {wsConnected && (
                  <Badge
                    status="processing"
                    text={<span className={styles.wsBadge}>Live</span>}
                  />
                )}
              </div>
              <span className={styles.subtitle}>
                {station?.host}:{station?.port}
              </span>
            </div>
          </div>
        </div>

        <div className={styles.headerActions}>
          <Button
            icon={<RefreshCw size={16} />}
            onClick={() => {
              refetchStation();
              refetchBatches();
            }}
            loading={isLoading}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className={styles.loading}>
          <Spin size="large" />
          <p>Loading station information...</p>
        </div>
      ) : !isConnected ? (
        <div className={styles.disconnected}>
          <WifiOff size={48} />
          <h2>Cannot connect to station</h2>
          <p>Check your network connection and ensure the station service is running</p>
          <Button onClick={() => refetchStation()}>Retry Connection</Button>
        </div>
      ) : (
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          className={styles.tabs}
          items={[
            {
              key: 'batches',
              label: (
                <span className={styles.tabLabel}>
                  <Package size={16} />
                  Batches ({batches?.length || 0})
                </span>
              ),
              children: (
                <div className={styles.batchesTab}>
                  {/* Filter Bar */}
                  <div className={styles.filterBar}>
                    <Select
                      value={batchFilter}
                      onChange={setBatchFilter}
                      style={{ width: 180 }}
                      options={[
                        { value: 'all', label: `All (${statusCounts.all})` },
                        { value: 'running', label: `Running (${statusCounts.running})` },
                        { value: 'idle', label: `Idle (${statusCounts.idle})` },
                        { value: 'completed', label: `Completed (${statusCounts.completed})` },
                        { value: 'error', label: `Error (${statusCounts.error})` },
                      ]}
                    />
                  </div>

                  {/* Batch Grid */}
                  {filteredBatches.length === 0 ? (
                    <Empty
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                      description={
                        batchFilter === 'all'
                          ? 'No batches registered'
                          : 'No batches with this status'
                      }
                    />
                  ) : (
                    <div className={styles.batchGrid}>
                      {filteredBatches.map((batch) => (
                        <BatchCard
                          key={batch.id}
                          batch={batch}
                          statistics={statistics?.[batch.id]}
                          // NOTE: All controls removed - manage batches from Station UI only
                        />
                      ))}
                    </div>
                  )}
                </div>
              ),
            },
            {
              key: 'health',
              label: (
                <span className={styles.tabLabel}>
                  <Activity size={16} />
                  Health
                </span>
              ),
              children: (
                <div className={styles.healthTab}>
                  {station?.health ? (
                    <HealthMetrics health={station.health} showDetails />
                  ) : (
                    <Empty description="Unable to load health information" />
                  )}
                </div>
              ),
            },
          ]}
        />
      )}
    </div>
  );
};

export default StationDetailPage;
