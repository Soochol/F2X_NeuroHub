/**
 * Manual Control page - Direct hardware control.
 */

import { useState } from 'react';
import { Wrench, AlertTriangle, Send, History, Cpu } from 'lucide-react';
import { useBatchList, useBatch, useManualControl } from '../hooks';
import { Button } from '../components/atoms/Button';
import { Input } from '../components/atoms/Input';
import { Select } from '../components/atoms/Select';
import { LoadingOverlay } from '../components/atoms/LoadingSpinner';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { getErrorMessage } from '../utils';
import type { ManualControlRequest, ManualControlResponse, HardwareStatus, BatchDetail } from '../types';

// Type guard to check if data is a BatchDetail
function isBatchDetail(data: unknown): data is BatchDetail {
  return data !== null && typeof data === 'object' && 'hardwareStatus' in data;
}

interface CommandHistoryItem {
  id: number;
  batchId: string;
  hardware: string;
  command: string;
  params: Record<string, unknown>;
  result: Record<string, unknown>;
  timestamp: Date;
  success: boolean;
}

export function ManualControlPage() {
  const { data: batches, isLoading } = useBatchList();
  const [selectedBatchId, setSelectedBatchId] = useState<string>('');
  const { data: batchDetail } = useBatch(selectedBatchId || null);

  const [selectedHardware, setSelectedHardware] = useState<string>('');
  const [command, setCommand] = useState<string>('');
  const [params, setParams] = useState<string>('{}');
  const [commandHistory, setCommandHistory] = useState<CommandHistoryItem[]>([]);
  const [lastResult, setLastResult] = useState<ManualControlResponse | null>(null);

  const manualControl = useManualControl();

  const handleExecute = async () => {
    if (!selectedBatchId || !selectedHardware || !command) return;

    try {
      const parsedParams = JSON.parse(params);
      const request: ManualControlRequest = {
        hardware: selectedHardware,
        command,
        params: parsedParams,
      };

      const result = await manualControl.mutateAsync({
        batchId: selectedBatchId,
        request,
      });

      setLastResult(result);
      setCommandHistory((prev) => [
        {
          id: Date.now(),
          batchId: selectedBatchId,
          hardware: selectedHardware,
          command,
          params: parsedParams,
          result: result.result,
          timestamp: new Date(),
          success: true,
        },
        ...prev.slice(0, 19), // Keep last 20 commands
      ]);
    } catch (error: unknown) {
      const errorMessage = getErrorMessage(error);
      setCommandHistory((prev) => [
        {
          id: Date.now(),
          batchId: selectedBatchId,
          hardware: selectedHardware,
          command,
          params: JSON.parse(params) as Record<string, unknown>,
          result: { error: errorMessage },
          timestamp: new Date(),
          success: false,
        },
        ...prev.slice(0, 19),
      ]);
    }
  };

  const batchOptions =
    batches?.map((b) => ({
      value: b.id,
      label: `${b.name} (${b.status})`,
    })) ?? [];

  const hardwareOptions = isBatchDetail(batchDetail) && batchDetail.hardwareStatus
    ? Object.entries(batchDetail.hardwareStatus).map(([id, status]) => ({
        value: id,
        label: `${id} (${(status as HardwareStatus).status})`,
      }))
    : [];

  if (isLoading) {
    return <LoadingOverlay message="Loading batches..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Wrench className="w-6 h-6 text-brand-500" />
        <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Manual Control</h2>
      </div>

      {/* Warning Banner */}
      <div className="flex items-center gap-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
        <AlertTriangle className="w-5 h-5 text-yellow-500" />
        <span className="text-yellow-400 text-sm">
          Manual control mode. Use with caution - direct hardware access can affect system state.
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Command Panel */}
        <div className="space-y-4">
          <div className="p-4 rounded-lg border space-y-4" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
            <h3 className="text-lg font-semibold flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
              <Send className="w-5 h-5" />
              Command Executor
            </h3>

            <Select
              label="Batch"
              options={batchOptions}
              value={selectedBatchId}
              onChange={(e) => {
                setSelectedBatchId(e.target.value);
                setSelectedHardware('');
              }}
              placeholder="Select a batch"
            />

            <Select
              label="Hardware Device"
              options={hardwareOptions}
              value={selectedHardware}
              onChange={(e) => setSelectedHardware(e.target.value)}
              placeholder="Select hardware"
              disabled={!selectedBatchId}
            />

            <Input
              label="Command"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="e.g., move, read, write"
              disabled={!selectedHardware}
            />

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
                Parameters (JSON)
              </label>
              <textarea
                className="w-full px-3 py-2 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                style={{ backgroundColor: 'var(--color-bg-tertiary)', borderColor: 'var(--color-border-default)', color: 'var(--color-text-primary)' }}
                rows={4}
                value={params}
                onChange={(e) => setParams(e.target.value)}
                placeholder='{"key": "value"}'
                disabled={!selectedHardware}
              />
            </div>

            <Button
              variant="primary"
              className="w-full"
              onClick={handleExecute}
              isLoading={manualControl.isPending}
              disabled={!selectedBatchId || !selectedHardware || !command}
            >
              <Send className="w-4 h-4 mr-2" />
              Execute Command
            </Button>
          </div>

          {/* Hardware Status */}
          {isBatchDetail(batchDetail) && batchDetail.hardwareStatus && Object.keys(batchDetail.hardwareStatus).length > 0 && (
            <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-4" style={{ color: 'var(--color-text-primary)' }}>
                <Cpu className="w-5 h-5" />
                Hardware Status
              </h3>
              <div className="space-y-2">
                {Object.entries(batchDetail.hardwareStatus).map(([id, status]) => (
                  <HardwareStatusRow
                    key={id}
                    id={id}
                    status={status as HardwareStatus}
                    isSelected={selectedHardware === id}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Result & History Panel */}
        <div className="space-y-4">
          {/* Last Result */}
          {lastResult && (
            <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
              <h3 className="text-lg font-semibold mb-3" style={{ color: 'var(--color-text-primary)' }}>Last Result</h3>
              <div className="p-3 rounded font-mono text-sm overflow-x-auto" style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}>
                <pre>{JSON.stringify(lastResult.result, null, 2)}</pre>
              </div>
            </div>
          )}

          {/* Command History */}
          <div className="p-4 rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
            <h3 className="text-lg font-semibold flex items-center gap-2 mb-4" style={{ color: 'var(--color-text-primary)' }}>
              <History className="w-5 h-5" />
              Command History
            </h3>

            {commandHistory.length === 0 ? (
              <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>No commands executed yet</p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {commandHistory.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 rounded-lg text-sm"
                    style={{ backgroundColor: item.success ? 'var(--color-bg-tertiary)' : 'rgba(239, 68, 68, 0.1)' }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono" style={{ color: 'var(--color-text-primary)' }}>
                          {item.hardware}.{item.command}
                        </span>
                        <StatusBadge
                          status={item.success ? 'pass' : 'fail'}
                          size="sm"
                        />
                      </div>
                      <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                        {item.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    {Object.keys(item.params).length > 0 && (
                      <div className="mt-1 text-xs font-mono" style={{ color: 'var(--color-text-secondary)' }}>
                        Params: {JSON.stringify(item.params)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

interface HardwareStatusRowProps {
  id: string;
  status: HardwareStatus;
  isSelected: boolean;
}

function HardwareStatusRow({ id, status, isSelected }: HardwareStatusRowProps) {
  return (
    <div
      className="flex items-center justify-between p-2 rounded"
      style={{
        backgroundColor: isSelected ? 'rgba(var(--color-brand-rgb), 0.1)' : 'var(--color-bg-tertiary)',
        border: isSelected ? '1px solid rgba(var(--color-brand-rgb), 0.3)' : 'none',
      }}
    >
      <div>
        <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{id}</span>
        <span className="ml-2 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{status.driver}</span>
      </div>
      <StatusBadge
        status={status.status === 'connected' ? 'connected' : 'disconnected'}
        size="sm"
      />
    </div>
  );
}
