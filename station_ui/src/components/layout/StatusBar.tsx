/**
 * Status bar component displaying connection status and running batches.
 */

import { useEffect, useState } from 'react';
import { Circle, Wifi, WifiOff } from 'lucide-react';
import { useConnectionStore } from '../../stores/connectionStore';
import { useBatchStore } from '../../stores/batchStore';

export function StatusBar() {
  const [currentTime, setCurrentTime] = useState(new Date());

  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const backendStatus = useConnectionStore((state) => state.backendStatus);
  const batches = useBatchStore((state) => state.batches);

  // Calculate running batches
  const runningBatches = Array.from(batches.values()).filter(
    (b) => b.status === 'running' || b.status === 'starting'
  ).length;

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  // Determine connection status colors
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'fill-green-500 text-green-500';
      case 'connecting':
        return 'fill-yellow-500 text-yellow-500 animate-pulse';
      case 'error':
        return 'fill-red-500 text-red-500';
      default:
        return 'fill-zinc-500 text-zinc-500';
    }
  };

  const isConnected = websocketStatus === 'connected';

  return (
    <footer
      className="flex items-center justify-between px-4 py-2 text-sm transition-colors"
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderTop: '1px solid var(--color-border-default)',
      }}
    >
      <div className="flex items-center gap-4">
        {/* WebSocket Status */}
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Wifi className="w-4 h-4" style={{ color: 'var(--color-success)' }} />
          ) : (
            <WifiOff className="w-4 h-4" style={{ color: 'var(--color-text-disabled)' }} />
          )}
          <span style={{ color: 'var(--color-text-secondary)' }}>WS</span>
          <Circle className={`w-2.5 h-2.5 ${getStatusColor(websocketStatus)}`} />
        </div>

        {/* Backend Status */}
        <div className="flex items-center gap-2">
          <span style={{ color: 'var(--color-text-secondary)' }}>Backend</span>
          <Circle className={`w-2.5 h-2.5 ${getStatusColor(backendStatus)}`} />
        </div>

        {/* Running Batches */}
        <div style={{ color: 'var(--color-text-secondary)' }}>
          Batches:{' '}
          <span
            className={runningBatches > 0 ? 'font-medium' : ''}
            style={{
              color: runningBatches > 0 ? 'var(--color-brand-400)' : 'var(--color-text-primary)',
            }}
          >
            {runningBatches} running
          </span>
        </div>
      </div>

      <div className="font-mono" style={{ color: 'var(--color-text-secondary)' }}>
        {formatTime(currentTime)}
      </div>
    </footer>
  );
}
