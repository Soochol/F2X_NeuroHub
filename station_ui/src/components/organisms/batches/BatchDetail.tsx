/**
 * Batch detail component showing full batch information.
 */

import { X, Play, Square } from 'lucide-react';
import { Button } from '../../atoms/Button';
import { StatusBadge } from '../../atoms/StatusBadge';
import { ProgressBar } from '../../atoms/ProgressBar';
import { LoadingSpinner } from '../../atoms/LoadingSpinner';
import type { BatchDetail as BatchDetailType, HardwareStatus } from '../../../types';

export interface BatchDetailProps {
  batch: BatchDetailType | null;
  isLoading?: boolean;
  onClose: () => void;
  onStartSequence: (batchId: string, params?: Record<string, unknown>) => void;
  onStopSequence: (batchId: string) => void;
  isStarting?: boolean;
  isStopping?: boolean;
}

export function BatchDetail({
  batch,
  isLoading,
  onClose,
  onStartSequence,
  onStopSequence,
  isStarting,
  isStopping,
}: BatchDetailProps) {
  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!batch) {
    return (
      <div className="p-8 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
        Select a batch to view details
      </div>
    );
  }

  const isRunning = batch.status === 'running' || batch.status === 'starting';
  const canStart = batch.status === 'idle' || batch.status === 'completed' || batch.status === 'error';

  return (
    <div className="rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>{batch.name}</h3>
          <StatusBadge status={batch.status} />
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6">
        {/* Sequence Info */}
        <Section title="Sequence">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <InfoRow label="Name" value={batch.sequenceName || 'Not assigned'} />
            <InfoRow label="Version" value={batch.sequenceVersion || '-'} />
            <InfoRow label="Package" value={batch.sequencePackage || '-'} />
          </div>
        </Section>

        {/* Execution Status */}
        {batch.execution && (
          <Section title="Execution">
            <div className="space-y-3">
              <div className="flex items-center gap-4">
                <ProgressBar
                  value={batch.execution.progress * 100}
                  variant={batch.status === 'error' ? 'error' : 'default'}
                  className="flex-1"
                />
                <span className="text-sm w-12 text-right" style={{ color: 'var(--color-text-secondary)' }}>
                  {Math.round(batch.execution.progress * 100)}%
                </span>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <InfoRow
                  label="Current Step"
                  value={batch.execution.currentStep || 'Waiting'}
                />
                <InfoRow
                  label="Progress"
                  value={`${batch.execution.stepIndex + 1} / ${batch.execution.totalSteps}`}
                />
                <InfoRow
                  label="Elapsed"
                  value={`${batch.execution.elapsed.toFixed(1)}s`}
                />
              </div>

              {/* Step Results */}
              {batch.execution.steps.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>Step Results</h4>
                  <div className="space-y-1 max-h-48 overflow-y-auto">
                    {batch.execution.steps.map((step) => (
                      <div
                        key={`step-${step.order}-${step.name}`}
                        className={`flex items-center justify-between px-2 py-1 rounded text-sm ${
                          step.status === 'running'
                            ? 'bg-brand-500/10'
                            : step.status === 'failed'
                              ? 'bg-red-500/10'
                              : ''
                        }`}
                      >
                        <span style={{ color: 'var(--color-text-primary)' }}>{step.name}</span>
                        <div className="flex items-center gap-2">
                          {step.duration !== undefined && (
                            <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                              {step.duration.toFixed(2)}s
                            </span>
                          )}
                          <StatusBadge
                            status={step.pass ? 'pass' : step.status === 'pending' ? 'idle' : 'fail'}
                            size="sm"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Hardware Status */}
        {batch.hardwareStatus && Object.keys(batch.hardwareStatus).length > 0 && (
          <Section title="Hardware">
            <div className="space-y-2">
              {Object.entries(batch.hardwareStatus).map(([id, status]) => (
                <HardwareRow key={id} id={id} status={status} />
              ))}
            </div>
          </Section>
        )}

        {/* Parameters */}
        {batch.parameters && Object.keys(batch.parameters).length > 0 && (
          <Section title="Parameters">
            <div className="grid grid-cols-2 gap-2 text-sm">
              {Object.entries(batch.parameters).map(([key, value]) => (
                <InfoRow key={key} label={key} value={String(value)} />
              ))}
            </div>
          </Section>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-2 p-4 border-t" style={{ borderColor: 'var(--color-border-default)' }}>
        {canStart && (
          <Button
            variant="primary"
            onClick={() => onStartSequence(batch.id)}
            isLoading={isStarting}
          >
            <Play className="w-4 h-4 mr-2" />
            Start Sequence
          </Button>
        )}
        {isRunning && (
          <Button
            variant="danger"
            onClick={() => onStopSequence(batch.id)}
            isLoading={isStopping}
          >
            <Square className="w-4 h-4 mr-2" />
            Stop Sequence
          </Button>
        )}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="text-sm font-medium mb-3" style={{ color: 'var(--color-text-secondary)' }}>{title}</h4>
      {children}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span style={{ color: 'var(--color-text-tertiary)' }}>{label}:</span>
      <span className="ml-2" style={{ color: 'var(--color-text-primary)' }}>{value}</span>
    </div>
  );
}

function HardwareRow({ id, status }: { id: string; status: HardwareStatus }) {
  return (
    <div className="flex items-center justify-between p-2 rounded" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
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
