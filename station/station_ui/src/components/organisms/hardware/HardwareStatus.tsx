/**
 * HardwareStatus - Displays hardware device status and configuration.
 */

import { Cpu, RefreshCw, AlertCircle, CheckCircle, XCircle, Settings } from 'lucide-react';
import { StatusBadge } from '../../atoms/StatusBadge';
import { Button } from '../../atoms/Button';
import type { HardwareStatus as HardwareStatusType } from '../../../types';

interface HardwareStatusProps {
  /** List of hardware devices */
  hardware: HardwareStatusType[];
  /** Show configuration details */
  showConfig?: boolean;
  /** Called when reconnect is requested */
  onReconnect?: (hardwareId: string) => void;
  /** Show reconnect button */
  showReconnect?: boolean;
  /** Loading state */
  isLoading?: boolean;
  /** Additional CSS classes */
  className?: string;
}

interface HardwareCardProps {
  hardware: HardwareStatusType;
  showConfig?: boolean;
  onReconnect?: () => void;
  showReconnect?: boolean;
}

function HardwareCard({
  hardware,
  showConfig = false,
  onReconnect,
  showReconnect = true,
}: HardwareCardProps) {
  const statusIcon = {
    connected: <CheckCircle className="w-4 h-4 text-green-400" />,
    disconnected: <XCircle className="w-4 h-4 text-red-400" />,
    error: <AlertCircle className="w-4 h-4 text-red-400" />,
  };

  return (
    <div className="bg-zinc-800/50 rounded-lg border border-zinc-700 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-zinc-400" />
          <span className="text-sm font-medium text-zinc-100">{hardware.id}</span>
          <span className="text-xs text-zinc-500">({hardware.driver})</span>
        </div>
        <StatusBadge
          status={hardware.status === 'connected' ? 'connected' : 'disconnected'}
          size="sm"
        />
      </div>

      {/* Status Details */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          {statusIcon[hardware.status]}
          <span
            className={`text-sm ${
              hardware.status === 'connected' ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {hardware.status === 'connected'
              ? 'Connected'
              : hardware.status === 'error'
                ? 'Error'
                : 'Disconnected'}
          </span>
        </div>

        {/* Error Message */}
        {hardware.lastError && (
          <div className="flex items-start gap-2 text-xs text-red-400 bg-red-500/10 rounded px-2 py-1.5">
            <AlertCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
            <span>{hardware.lastError}</span>
          </div>
        )}

        {/* Device Info */}
        {hardware.info && Object.keys(hardware.info).length > 0 && (
          <div className="mt-2 pt-2 border-t border-zinc-700">
            <p className="text-xs text-zinc-500 mb-1">Device Info:</p>
            <div className="text-xs text-zinc-400 space-y-0.5">
              {Object.entries(hardware.info).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-zinc-500">{key}:</span>
                  <span className="truncate max-w-[200px]">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Configuration */}
        {showConfig && hardware.config && Object.keys(hardware.config).length > 0 && (
          <div className="mt-2 pt-2 border-t border-zinc-700">
            <div className="flex items-center gap-1 text-xs text-zinc-500 mb-1">
              <Settings className="w-3 h-3" />
              <span>Configuration:</span>
            </div>
            <div className="text-xs font-mono text-zinc-400 bg-zinc-900 rounded px-2 py-1.5 space-y-0.5">
              {Object.entries(hardware.config).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-zinc-500">{key}:</span>
                  <span className="truncate max-w-[200px]">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Reconnect Button */}
        {showReconnect && hardware.status !== 'connected' && onReconnect && (
          <div className="mt-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={onReconnect}
              className="w-full"
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
              Reconnect
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

export function HardwareStatus({
  hardware,
  showConfig = false,
  onReconnect,
  showReconnect = true,
  isLoading = false,
  className = '',
}: HardwareStatusProps) {
  const connectedCount = hardware.filter((h) => h.status === 'connected').length;
  const totalCount = hardware.length;

  if (isLoading) {
    return (
      <div className={`bg-zinc-900 rounded-lg border border-zinc-800 p-4 ${className}`}>
        <div className="animate-pulse space-y-3">
          <div className="h-5 bg-zinc-800 rounded w-32" />
          <div className="h-20 bg-zinc-800 rounded" />
          <div className="h-20 bg-zinc-800 rounded" />
        </div>
      </div>
    );
  }

  if (hardware.length === 0) {
    return (
      <div className={`bg-zinc-900 rounded-lg border border-zinc-800 p-4 ${className}`}>
        <div className="text-center py-4 text-zinc-500">
          <Cpu className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No hardware configured</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-zinc-900 rounded-lg border border-zinc-800 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-brand-400" />
          <h3 className="text-sm font-medium text-zinc-100">Hardware Status</h3>
        </div>
        <span
          className={`text-xs font-medium ${
            connectedCount === totalCount ? 'text-green-400' : 'text-yellow-400'
          }`}
        >
          {connectedCount}/{totalCount} Connected
        </span>
      </div>

      {/* Hardware List */}
      <div className="p-4 space-y-3">
        {hardware.map((hw) => (
          <HardwareCard
            key={hw.id}
            hardware={hw}
            showConfig={showConfig}
            onReconnect={onReconnect ? () => onReconnect(hw.id) : undefined}
            showReconnect={showReconnect}
          />
        ))}
      </div>
    </div>
  );
}
