/**
 * Real-time connection status indicator
 * Shows WebSocket connection state and last update time
 */

import { useMemo } from 'react';
import styles from './RealTimeIndicator.module.css';

interface RealTimeIndicatorProps {
  isConnected: boolean;
  lastUpdate?: Date | null;
  className?: string;
}

export const RealTimeIndicator = ({
  isConnected,
  lastUpdate,
  className,
}: RealTimeIndicatorProps) => {
  const formattedTime = useMemo(() => {
    if (!lastUpdate) return null;
    return lastUpdate.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }, [lastUpdate]);

  return (
    <div className={`${styles.container} ${className || ''}`}>
      <div className={`${styles.dot} ${isConnected ? styles.connected : styles.disconnected}`} />
      <span className={styles.label}>
        {isConnected ? 'Live' : 'Offline'}
      </span>
      {formattedTime && (
        <span className={styles.time}>
          {formattedTime}
        </span>
      )}
    </div>
  );
};
