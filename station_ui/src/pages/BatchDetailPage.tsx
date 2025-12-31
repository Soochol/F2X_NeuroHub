/**
 * Batch Detail Page - Full page view for batch details.
 * Shows sequence metadata, steps with timing, pass/fail status,
 * total elapsed time, final result, and progress bar during testing.
 */

import { useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Play,
  Square,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  Package,
  Layers,
  Timer,
} from 'lucide-react';
import { useBatch, useStartBatch, useStartSequence, useStopSequence, useStopBatch, useWebSocket } from '../hooks';
import { useBatchStore } from '../stores/batchStore';
import { Button } from '../components/atoms/Button';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { ProgressBar } from '../components/atoms/ProgressBar';
import { LoadingOverlay } from '../components/atoms/LoadingSpinner';
import { ROUTES } from '../constants';
import type { Batch, BatchDetail, StepResult } from '../types';

// Type guard to check if batch is a BatchDetail
function isBatchDetail(batch: Batch | BatchDetail): batch is BatchDetail {
  return 'parameters' in batch && 'hardwareStatus' in batch;
}

export function BatchDetailPage() {
  const { batchId } = useParams<{ batchId: string }>();
  const navigate = useNavigate();

  const { data: batch, isLoading } = useBatch(batchId ?? null);
  const { subscribe, unsubscribe } = useWebSocket();
  const getBatchStats = useBatchStore((state) => state.getBatchStats);

  const startBatch = useStartBatch();
  const startSequence = useStartSequence();
  const stopSequence = useStopSequence();
  const stopBatch = useStopBatch();

  // Subscribe to real-time updates for this batch
  useEffect(() => {
    if (batchId) {
      subscribe([batchId]);
      return () => unsubscribe([batchId]);
    }
  }, [batchId, subscribe, unsubscribe]);

  const statistics = useMemo(() => {
    return batchId ? getBatchStats(batchId) : undefined;
  }, [batchId, getBatchStats]);

  // Get steps from BatchDetail or create empty array
  // IMPORTANT: This useMemo must be before any early returns to comply with Rules of Hooks
  const steps: StepResult[] = useMemo(() => {
    if (!batch) return [];
    if (isBatchDetail(batch) && batch.execution?.steps) {
      return batch.execution.steps;
    }
    return [];
  }, [batch]);

  const handleBack = () => {
    navigate(ROUTES.BATCHES);
  };

  const handleStartSequence = async () => {
    if (!batchId || !batch) {
      console.error('[handleStartSequence] Missing batchId or batch');
      return;
    }

    try {
      console.log('[handleStartSequence] Starting sequence for batch:', batchId, 'status:', batch.status);

      // If batch is idle, start batch first then start sequence
      if (batch.status === 'idle') {
        console.log('[handleStartSequence] Starting batch first...');
        await startBatch.mutateAsync(batchId);
        console.log('[handleStartSequence] Batch started');
      }

      // Then start sequence
      console.log('[handleStartSequence] Starting sequence...');
      await startSequence.mutateAsync({ batchId, request: undefined });
      console.log('[handleStartSequence] Sequence started successfully');
    } catch (error) {
      console.error('[handleStartSequence] Error:', error);
    }
  };

  const handleStopSequence = async () => {
    if (batchId) {
      // Stop sequence first, then stop batch
      await stopSequence.mutateAsync(batchId);
      await stopBatch.mutateAsync(batchId);
    }
  };


  // Early returns for loading and not-found states
  if (isLoading) {
    return <LoadingOverlay message="Loading batch details..." />;
  }

  if (!batch) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
        <AlertCircle className="w-16 h-16 mb-4" style={{ color: 'var(--color-text-tertiary)' }} />
        <p className="text-lg mb-4" style={{ color: 'var(--color-text-tertiary)' }}>Batch not found</p>
        <Button variant="secondary" onClick={handleBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Batches
        </Button>
      </div>
    );
  }

  // Computed values that depend on batch being defined
  const isRunning = batch.status === 'running' || batch.status === 'starting';
  const canStart = batch.status === 'idle' || batch.status === 'completed' || batch.status === 'error';

  // Calculate total elapsed time from steps
  const totalStepsTime = steps.reduce((sum, step) => sum + (step.duration || 0), 0);
  const elapsedTime = isBatchDetail(batch) && batch.execution
    ? batch.execution.elapsed
    : batch.elapsed;

  // Calculate progress
  const progress = isBatchDetail(batch) && batch.execution
    ? batch.execution.progress
    : batch.progress;

  // Determine final verdict
  const getFinalVerdict = (): { text: string; color: string; icon: React.ReactNode } | null => {
    if (batch.status === 'running' || batch.status === 'starting') {
      return { text: 'In Progress', color: 'text-brand-500', icon: <Loader2 className="w-6 h-6 animate-spin" /> };
    }
    if (batch.status === 'completed') {
      const hasFailed = steps.some((s) => !s.pass && s.status === 'completed');
      if (hasFailed) {
        return { text: 'FAIL', color: 'text-red-500', icon: <XCircle className="w-6 h-6" /> };
      }
      return { text: 'PASS', color: 'text-green-500', icon: <CheckCircle className="w-6 h-6" /> };
    }
    if (batch.status === 'error') {
      return { text: 'ERROR', color: 'text-red-500', icon: <XCircle className="w-6 h-6" /> };
    }
    return null;
  };

  const verdict = getFinalVerdict();

  return (
    <div className="min-h-full p-6 space-y-6" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
      {/* Header with Back Button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>{batch.name}</h1>
            <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>ID: {batch.id}</p>
          </div>
          <StatusBadge status={batch.status} />
        </div>
        <div className="flex items-center gap-2">
          {canStart && (
            <Button
              variant="primary"
              onClick={handleStartSequence}
              isLoading={startBatch.isPending || startSequence.isPending}
            >
              <Play className="w-4 h-4 mr-2" />
              Start Sequence
            </Button>
          )}
          {isRunning && (
            <Button
              variant="danger"
              onClick={handleStopSequence}
              isLoading={stopSequence.isPending || stopBatch.isPending}
            >
              <Square className="w-4 h-4 mr-2" />
              Stop
            </Button>
          )}
        </div>
      </div>

      {/* Progress Bar (always visible) */}
      <div className="rounded-lg p-4 border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Test Progress</span>
          <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>{Math.round(progress * 100)}%</span>
        </div>
        <ProgressBar
          value={progress * 100}
          variant={batch.status === 'completed' ? (steps.every((s) => s.pass) ? 'success' : 'error') : 'default'}
        />
        {batch.currentStep && isRunning && (
          <p className="mt-2 text-sm text-brand-400">
            Current Step: <span className="font-medium">{batch.currentStep}</span>
          </p>
        )}
      </div>

      {/* Sequence Metadata */}
      <div className="rounded-lg p-6 border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center gap-2 mb-4">
          <Package className="w-5 h-5 text-brand-500" />
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Sequence Information</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetaCard label="Sequence Name" value={batch.sequenceName || 'Not assigned'} />
          <MetaCard label="Version" value={batch.sequenceVersion || '-'} />
          <MetaCard label="Package" value={batch.sequencePackage || '-'} />
          <MetaCard label="Total Steps" value={(batch.totalSteps ?? 0).toString()} />
        </div>
      </div>

      {/* Statistics & Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Execution Statistics */}
        <div className="rounded-lg p-6 border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
          <div className="flex items-center gap-2 mb-4">
            <Layers className="w-5 h-5 text-brand-500" />
            <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Execution Statistics</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <StatCard
              icon={<CheckCircle className="w-5 h-5" style={{ color: 'var(--color-text-secondary)' }} />}
              label="Total Runs"
              value={statistics?.total ?? 0}
            />
            <StatCard
              icon={<CheckCircle className="w-5 h-5 text-green-500" />}
              label="Pass"
              value={statistics?.pass ?? 0}
              color="#4ade80"
            />
            <StatCard
              icon={<XCircle className="w-5 h-5 text-red-500" />}
              label="Fail"
              value={statistics?.fail ?? 0}
              color="#f87171"
            />
            <StatCard
              icon={<AlertCircle className="w-5 h-5 text-brand-500" />}
              label="Pass Rate"
              value={`${((statistics?.passRate ?? 0) * 100).toFixed(1)}%`}
              color="var(--color-brand-500)"
            />
          </div>
        </div>

        {/* Timing & Verdict */}
        <div className="rounded-lg p-6 border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
          <div className="flex items-center gap-2 mb-4">
            <Timer className="w-5 h-5 text-brand-500" />
            <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Timing & Result</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <StatCard
              icon={<Clock className="w-5 h-5" style={{ color: 'var(--color-text-secondary)' }} />}
              label="Total Elapsed"
              value={`${elapsedTime.toFixed(1)}s`}
            />
            <StatCard
              icon={<Timer className="w-5 h-5" style={{ color: 'var(--color-text-secondary)' }} />}
              label="Steps Time"
              value={`${totalStepsTime.toFixed(2)}s`}
            />
          </div>
          {verdict && (
            <div className="mt-4 p-4 rounded-lg flex items-center justify-center gap-3" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
              <span className={verdict.color}>{verdict.icon}</span>
              <span className={`text-2xl font-bold ${verdict.color}`}>{verdict.text}</span>
            </div>
          )}
        </div>
      </div>

      {/* Steps Table */}
      <div className="rounded-lg p-6 border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle className="w-5 h-5 text-brand-500" />
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Step Results</h2>
        </div>
        <StepsTable steps={steps} totalSteps={batch.totalSteps ?? 0} stepNames={batch.stepNames} />
      </div>
    </div>
  );
}

// Sub-components

function MetaCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
      <p className="text-xs mb-1" style={{ color: 'var(--color-text-tertiary)' }}>{label}</p>
      <p className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>{value}</p>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="p-3 rounded-lg flex items-center gap-3" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
      {icon}
      <div>
        <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{label}</p>
        <p className="text-lg font-semibold" style={{ color: color || 'var(--color-text-primary)' }}>{value}</p>
      </div>
    </div>
  );
}

function StepsTable({ steps, totalSteps, stepNames }: { steps: StepResult[]; totalSteps: number; stepNames?: string[] }) {
  // Generate display steps - either from actual steps or placeholders
  const displaySteps: StepResult[] =
    steps.length > 0
      ? steps.map((step, i) => ({
          ...step,
          // Use stepNames as fallback if step.name is generic
          name: step.name.startsWith('Step ') && stepNames?.[i] ? stepNames[i] : step.name,
        }))
      : Array.from({ length: totalSteps || 0 }, (_, i) => ({
          order: i + 1,
          name: stepNames?.[i] || `Step ${i + 1}`,
          status: 'pending' as const,
          pass: false,
          duration: undefined,
          result: undefined,
        }));

  if (displaySteps.length === 0) {
    return <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>No steps defined for this sequence</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left border-b" style={{ color: 'var(--color-text-tertiary)', borderColor: 'var(--color-border-default)' }}>
            <th className="pb-3 pr-4 w-12">#</th>
            <th className="pb-3 pr-4">Step Name</th>
            <th className="pb-3 pr-4 w-24">Status</th>
            <th className="pb-3 pr-4 w-20">Result</th>
            <th className="pb-3 pr-4 w-28">Duration</th>
          </tr>
        </thead>
        <tbody>
          {displaySteps.map((step) => (
            <StepRow key={`${step.order}-${step.name}`} step={step} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StepRow({ step }: { step: StepResult }) {
  const getStatusBadge = () => {
    if (step.status === 'completed') return 'completed';
    if (step.status === 'running') return 'running';
    if (step.status === 'failed') return 'error';
    return 'idle';
  };

  const getResultBadge = () => {
    if (step.status === 'pending') {
      return <span className="text-zinc-500">-</span>;
    }
    if (step.status === 'running') {
      return (
        <span className="flex items-center gap-1 text-brand-500">
          <Loader2 className="w-3 h-3 animate-spin" />
        </span>
      );
    }
    return (
      <span className={`font-medium ${step.pass ? 'text-green-500' : 'text-red-500'}`}>
        {step.pass ? 'PASS' : 'FAIL'}
      </span>
    );
  };

  return (
    <tr
      className="border-b transition-colors"
      style={{
        borderColor: 'var(--color-border-subtle)',
        backgroundColor: step.status === 'running'
          ? 'rgba(var(--color-brand-rgb), 0.1)'
          : step.status === 'failed'
            ? 'rgba(239, 68, 68, 0.1)'
            : step.pass === false && step.status === 'completed'
              ? 'rgba(239, 68, 68, 0.05)'
              : 'transparent',
      }}
    >
      <td className="py-3 pr-4" style={{ color: 'var(--color-text-secondary)' }}>{step.order}</td>
      <td className="py-3 pr-4 font-medium" style={{ color: 'var(--color-text-primary)' }}>{step.name}</td>
      <td className="py-3 pr-4">
        <StatusBadge status={getStatusBadge()} size="sm" />
      </td>
      <td className="py-3 pr-4">{getResultBadge()}</td>
      <td className="py-3 pr-4 font-mono" style={{ color: 'var(--color-text-secondary)' }}>
        {step.duration != null ? `${step.duration.toFixed(2)}s` : '-'}
      </td>
    </tr>
  );
}
