/**
 * Batch Detail Page - Full page view for batch details.
 * Shows sequence metadata, steps with timing, pass/fail status,
 * total elapsed time, final result, and progress bar during testing.
 * Includes a debug panel for viewing logs and step data.
 */

import { useEffect, useMemo, useState, useCallback } from 'react';
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
  Trash2,
} from 'lucide-react';
import { useBatch, useBatchStatistics, useStartBatch, useStartSequence, useStopSequence, useStopBatch, useDeleteBatch, useWebSocket, useWorkflowConfig, useSequenceRegistry } from '../hooks';
import { useBatchStore } from '../stores/batchStore';
import { useDebugPanelStore } from '../stores/debugPanelStore';
import { useLogStore } from '../stores/logStore';
import type { BatchStatistics } from '../types';
import { Button } from '../components/atoms/Button';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { ProgressBar } from '../components/atoms/ProgressBar';
import { LoadingOverlay } from '../components/atoms/LoadingSpinner';
import { SplitLayout } from '../components/layout';
import { DebugLogPanel } from '../components/organisms/debug';
import { WipInputModal } from '../components/molecules';
import { ROUTES } from '../constants';
import { toast } from '../utils/toast';
import { createLogger } from '../utils';
import { validateWip } from '../api/endpoints/system';
import type { Batch, BatchDetail, StepResult } from '../types';

const log = createLogger({ prefix: 'BatchDetailPage' });

// Type guard to check if batch is a BatchDetail
function isBatchDetail(batch: Batch | BatchDetail): batch is BatchDetail {
  return 'parameters' in batch && 'hardwareStatus' in batch;
}

export function BatchDetailPage() {
  const { batchId } = useParams<{ batchId: string }>();
  const navigate = useNavigate();

  const { data: batch, isLoading } = useBatch(batchId ?? null);
  const { data: apiStatistics } = useBatchStatistics(batchId ?? null);
  const { subscribe } = useWebSocket();
  const getBatchStats = useBatchStore((state) => state.getBatchStats);
  const setBatchStatistics = useBatchStore((state) => state.setBatchStatistics);

  const startBatch = useStartBatch();
  const startSequence = useStartSequence();
  const stopSequence = useStopSequence();
  const stopBatch = useStopBatch();
  const deleteBatch = useDeleteBatch();

  // Debug panel state - must be called before any early returns
  const { isCollapsed, panelWidth, setPanelWidth, toggleCollapsed, setSelectedStep } = useDebugPanelStore();

  // Workflow configuration
  const { data: workflowConfig } = useWorkflowConfig();

  // Sequence registry for update check
  const { data: registryResponse } = useSequenceRegistry();

  // WIP input modal state
  const [showWipModal, setShowWipModal] = useState(false);
  const [wipError, setWipError] = useState<string | null>(null);

  // Track unsaved changes in config/params editors
  const [hasPendingChanges, setHasPendingChanges] = useState(false);

  // Callback for DebugLogPanel to notify about pending changes
  const handlePendingChangesChange = useCallback((hasPending: boolean) => {
    setHasPendingChanges(hasPending);
  }, []);

  // Subscribe to real-time updates for this batch
  // NOTE: We intentionally don't unsubscribe on cleanup because:
  // 1. React's cleanup runs BEFORE new component's effect, causing a gap
  // 2. BatchesPage will re-subscribe to all batches anyway
  // 3. Subscriptions are idempotent and cleaned up on WebSocket disconnect
  useEffect(() => {
    if (batchId) {
      log.debug(`useEffect: subscribing to batch ${batchId.slice(0, 8)}...`);
      subscribe([batchId]);
      // No cleanup - subscriptions persist across navigation
    }
  }, [batchId, subscribe]);

  // Sync API statistics to store (for persistence across page refreshes)
  useEffect(() => {
    if (batchId && apiStatistics) {
      setBatchStatistics(batchId, apiStatistics);
    }
  }, [batchId, apiStatistics, setBatchStatistics]);

  // Get statistics from store (includes real-time updates from WebSocket)
  const storeStatistics = useMemo(() => {
    return batchId ? getBatchStats(batchId) : undefined;
  }, [batchId, getBatchStats]);

  // Merge: prefer store (has real-time updates) but fall back to API
  const statistics: BatchStatistics | undefined = storeStatistics ?? apiStatistics;

  // Get steps from store (real-time updates) or API (batch.execution.steps)
  // IMPORTANT: This useMemo must be before any early returns to comply with Rules of Hooks
  // Priority: batch.steps (from store, real-time) > batch.execution.steps (from API)
  const steps: StepResult[] = useMemo(() => {
    if (!batch) return [];
    // Prefer store steps for real-time updates during execution
    if (batch.steps && batch.steps.length > 0) {
      return batch.steps;
    }
    // Fall back to API data for historical execution details
    if (isBatchDetail(batch) && batch.execution?.steps) {
      return batch.execution.steps;
    }
    return [];
  }, [batch]);

  const handleBack = () => {
    navigate(ROUTES.BATCHES);
  };

  // Handle clicking "Start Sequence" button
  const handleStartSequence = async () => {
    if (!batchId || !batch) {
      log.error('handleStartSequence: Missing batchId or batch');
      return;
    }

    // Check sequence update status and show warning (non-blocking)
    if (batch.sequencePackage && registryResponse?.items) {
      const sequenceName = batch.sequencePackage.replace(/^sequences\//, '');
      const registryItem = registryResponse.items.find(r => r.name === sequenceName);

      if (registryItem?.status === 'update_available') {
        toast.warning(
          `시퀀스 업데이트가 가능합니다. 현재: v${registryItem.localVersion} → 최신: v${registryItem.remoteVersion}`
        );
      }
    }

    // If workflow is enabled, show WIP input modal first
    if (workflowConfig?.enabled) {
      setShowWipModal(true);
      return;
    }

    // Otherwise, start sequence directly
    await doStartSequence();
  };

  // Actually start the sequence (with optional WIP ID and pre-validated int ID)
  const doStartSequence = async (wipId?: string, wipIntId?: number) => {
    if (!batchId || !batch) {
      log.error('doStartSequence: Missing batchId or batch');
      return;
    }

    // Clear logs before starting new sequence
    useLogStore.getState().clearLogs();

    // Track if we started the batch so we can stop it on error
    let batchWasStarted = false;

    try {
      log.debug('doStartSequence: Starting sequence for batch:', batchId, 'status:', batch.status, 'wipId:', wipId || '(none)');

      // If batch is idle, start batch first then start sequence
      if (batch.status === 'idle') {
        log.debug('doStartSequence: Starting batch first...');
        await startBatch.mutateAsync(batchId);
        batchWasStarted = true;
        log.debug('doStartSequence: Batch started');
      }

      // Prepare request with WIP ID and pre-validated int ID if provided
      const request = wipId ? {
        parameters: { wip_id: wipId },
        wip_int_id: wipIntId,  // Skip lookup in worker if provided
      } : undefined;

      // Then start sequence
      log.debug('doStartSequence: Starting sequence...');
      await startSequence.mutateAsync({ batchId, request });
      log.debug('doStartSequence: Sequence started successfully');
    } catch (error) {
      log.error('doStartSequence: Error:', error);

      // If we started the batch but sequence failed, stop the batch
      if (batchWasStarted) {
        log.debug('doStartSequence: Stopping batch due to sequence start failure...');
        try {
          await stopBatch.mutateAsync(batchId);
          log.debug('doStartSequence: Batch stopped');
        } catch (stopError) {
          log.error('doStartSequence: Failed to stop batch:', stopError);
        }
      }

      throw error; // Re-throw to allow caller to handle
    }
  };

  // Handle WIP input modal submit
  const handleWipSubmit = async (wipId: string) => {
    setWipError(null);

    try {
      // Step 1: Validate WIP first (fast check, ~100ms)
      // Get processId from BatchDetail - check both legacy field and config
      const processId = batch && isBatchDetail(batch)
        ? (batch.processId ?? (batch.config?.processId as number | undefined))
        : undefined;

      // Step 1.1: Ensure processId is set for WIP validation
      if (processId === undefined || processId === null) {
        setWipError('MES Process가 설정되지 않았습니다. Config 탭에서 MES Process를 선택하고 저장해주세요.');
        return;
      }

      const validationResult = await validateWip(wipId, processId);

      if (!validationResult.valid) {
        // Show error in modal, don't close
        setWipError(validationResult.message || `WIP '${wipId}' not found`);
        return;
      }

      // Step 1.5: Check if WIP already PASS for this process (BR-004 pre-check)
      if (validationResult.hasPassForProcess) {
        setWipError(validationResult.passWarningMessage || '이 WIP는 이미 해당 공정을 PASS했습니다.');
        return;
      }

      // Step 2: WIP is valid - close modal immediately
      setShowWipModal(false);

      // Step 3: Start batch and sequence with pre-validated int ID (runs in background)
      await doStartSequence(wipId, validationResult.intId);
    } catch (error) {
      // Network error during validation - show in modal
      const errorMessage = error instanceof Error
        ? error.message
        : (error as { message?: string })?.message || 'Failed to validate WIP';

      // If modal is still open (validation failed), show error there
      // Otherwise show as toast
      if (showWipModal) {
        setWipError(errorMessage);
      } else {
        toast.error(errorMessage);
      }
    }
  };

  // Handle closing the WIP modal
  const handleWipModalClose = () => {
    setShowWipModal(false);
    setWipError(null);
  };

  const handleStopSequence = async () => {
    if (batchId) {
      // Stop sequence first, then stop batch
      await stopSequence.mutateAsync(batchId);
      await stopBatch.mutateAsync(batchId);
    }
  };

  const handleDeleteBatch = async () => {
    if (batchId && window.confirm('Are you sure you want to delete this batch?')) {
      await deleteBatch.mutateAsync(batchId);
      navigate(ROUTES.BATCHES);
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
  // Include 'stopping' in isRunning so stop button remains visible during stop transition
  const isRunning = batch.status === 'running' || batch.status === 'starting' || batch.status === 'stopping';
  // Disable start during transitions (starting/stopping) for better UX
  const canStart = batch.status === 'idle' || batch.status === 'completed' || batch.status === 'error';

  // Prefer batch.elapsed (from store, updated via WebSocket) over batch.execution.elapsed (from API)
  // Store's elapsed is updated in real-time when sequence_complete is received
  // When running/starting: always show batch.elapsed (even if 0)
  // When idle/completed with no recent elapsed: fall back to lastDuration from statistics
  const elapsedTime = isRunning
    ? batch.elapsed
    : batch.elapsed > 0
      ? batch.elapsed
      : (isBatchDetail(batch) && batch.execution && batch.execution.elapsed > 0)
        ? batch.execution.elapsed
        : (statistics?.lastDuration ?? 0);

  // Calculate progress - prefer batch.progress which is merged from store for real-time updates
  // batch.execution.progress is only updated via API polling, which is slower
  const progress = batch.progress ?? (isBatchDetail(batch) && batch.execution
    ? batch.execution.progress
    : 0);

  // Determine final verdict
  const getFinalVerdict = (): { text: string; color: string; icon: React.ReactNode } | null => {
    if (batch.status === 'running' || batch.status === 'starting') {
      return { text: 'In Progress', color: 'text-brand-500', icon: <Loader2 className="w-6 h-6 animate-spin" /> };
    }
    if (batch.status === 'completed') {
      if (batch.lastRunPassed) {
        return { text: 'PASS', color: 'text-green-500', icon: <CheckCircle className="w-6 h-6" /> };
      }
      return { text: 'FAIL', color: 'text-red-500', icon: <XCircle className="w-6 h-6" /> };
    }
    if (batch.status === 'error') {
      return { text: 'ERROR', color: 'text-red-500', icon: <XCircle className="w-6 h-6" /> };
    }
    return null;
  };

  const verdict = getFinalVerdict();

  // Handle step row click to filter logs
  const handleStepRowClick = (stepName: string) => {
    setSelectedStep(stepName);
  };

  return (
    <SplitLayout
      panel={
        <DebugLogPanel
          batchId={batchId || ''}
          steps={steps}
          isRunning={isRunning}
          onPendingChangesChange={handlePendingChangesChange}
        />
      }
      panelWidth={panelWidth}
      isCollapsed={isCollapsed}
      onResize={setPanelWidth}
      onToggle={toggleCollapsed}
      panelTitle="Batch Panel"
    >
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
          {/* Inline Statistics */}
          <div className="hidden md:flex items-center gap-4 ml-4 pl-4 border-l" style={{ borderColor: 'var(--color-border-default)' }}>
            <div className="flex items-center gap-1.5 text-sm">
              <span style={{ color: 'var(--color-text-tertiary)' }}>Runs:</span>
              <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{statistics?.total ?? 0}</span>
            </div>
            <div className="flex items-center gap-1.5 text-sm">
              <CheckCircle className="w-3.5 h-3.5 text-green-500" />
              <span className="font-medium text-green-500">{statistics?.passCount ?? 0}</span>
            </div>
            <div className="flex items-center gap-1.5 text-sm">
              <XCircle className="w-3.5 h-3.5 text-red-500" />
              <span className="font-medium text-red-500">{statistics?.fail ?? 0}</span>
            </div>
            <div className="flex items-center gap-1.5 text-sm">
              <span style={{ color: 'var(--color-text-tertiary)' }}>Rate:</span>
              <span className="font-medium text-brand-500">{((statistics?.passRate ?? 0) * 100).toFixed(0)}%</span>
            </div>
            <div className="flex items-center gap-1.5 text-sm">
              <Clock className="w-3.5 h-3.5" style={{ color: 'var(--color-text-tertiary)' }} />
              <span className="font-mono" style={{ color: 'var(--color-text-secondary)' }}>{elapsedTime.toFixed(2)}s</span>
            </div>
            {verdict && (
              <div className={`flex items-center gap-1 font-bold ${verdict.color}`}>
                {verdict.icon}
                <span className="text-sm">{verdict.text}</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {canStart && (
            <Button
              variant="primary"
              onClick={handleStartSequence}
              isLoading={startBatch.isPending || startSequence.isPending}
              disabled={hasPendingChanges}
              title={hasPendingChanges ? 'Save changes in Config/Params tabs first' : undefined}
            >
              <Play className="w-4 h-4 mr-2" />
              {hasPendingChanges ? 'Save Changes First' : 'Start Sequence'}
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
          {!isRunning && (
            <Button
              variant="ghost"
              onClick={handleDeleteBatch}
              isLoading={deleteBatch.isPending}
              className="text-red-500 hover:text-red-400 hover:bg-red-500/10"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
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
          variant={batch.status === 'completed' ? (batch.lastRunPassed ? 'success' : 'error') : 'default'}
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


      {/* Steps Table */}
      <div className="rounded-lg p-6 border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle className="w-5 h-5 text-brand-500" />
          <h2 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Step Results</h2>
        </div>
        <StepsTable steps={steps} totalSteps={batch.totalSteps ?? 0} stepNames={batch.stepNames} onStepClick={handleStepRowClick} />
      </div>
    </div>

      {/* WIP Input Modal */}
      <WipInputModal
        isOpen={showWipModal}
        onClose={handleWipModalClose}
        onSubmit={handleWipSubmit}
        isLoading={startBatch.isPending || startSequence.isPending}
        batchName={batch.name}
        errorMessage={wipError}
      />
    </SplitLayout>
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

function StepsTable({ steps, totalSteps, stepNames, onStepClick }: { steps: StepResult[]; totalSteps: number; stepNames?: string[]; onStepClick?: (stepName: string) => void }) {
  // Always generate placeholders from stepNames/totalSteps, then overlay actual results
  // This ensures all steps are shown even when some are skipped (e.g., SETUP_ERROR)
  const stepCount = Math.max(totalSteps || 0, stepNames?.length || 0, steps.length);

  // Create a map of actual step results by name for quick lookup
  const stepResultMap = new Map<string, StepResult>();
  for (const step of steps) {
    stepResultMap.set(step.name, step);
  }

  // Generate display steps: placeholders with actual results overlaid
  const displaySteps: StepResult[] = Array.from({ length: stepCount }, (_, i) => {
    const placeholderName = stepNames?.[i] || `Step ${i + 1}`;
    const actualStep = stepResultMap.get(placeholderName);

    if (actualStep) {
      // Use actual step result
      return {
        ...actualStep,
        order: actualStep.order ?? i + 1,
      };
    }

    // Return placeholder for steps that haven't run
    return {
      order: i + 1,
      name: placeholderName,
      status: 'pending' as const,
      pass: false,
      duration: undefined,
      result: undefined,
    };
  });

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
            <th className="pb-3 pr-4">Measurements</th>
            <th className="pb-3 pr-4 w-28">Duration</th>
          </tr>
        </thead>
        <tbody>
          {displaySteps.map((step) => (
            <StepRow key={`${step.order}-${step.name}`} step={step} onClick={onStepClick ? () => onStepClick(step.name) : undefined} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface MeasurementValue {
  value?: number | string;
  unit?: string;
  passed?: boolean;
  min?: number;
  max?: number;
}

function MeasurementsCell({ measurements }: { measurements?: Record<string, unknown> }) {
  if (!measurements || Object.keys(measurements).length === 0) {
    return <span style={{ color: 'var(--color-text-tertiary)' }}>-</span>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {Object.entries(measurements).map(([key, val]) => {
        const m = val as MeasurementValue;
        const value = m?.value ?? val;
        const unit = m?.unit ?? '';
        const passed = m?.passed;
        const hasLimits = m?.min !== undefined || m?.max !== undefined;

        // Format display value
        const displayValue = typeof value === 'number' ? value.toFixed(2) : String(value);

        // Determine color based on pass/fail
        const valueColor = passed === true
          ? 'text-green-500'
          : passed === false
            ? 'text-red-500'
            : '';

        return (
          <span
            key={key}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono"
            style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
            title={hasLimits ? `${key}: ${displayValue}${unit} (${m.min ?? '-'} ~ ${m.max ?? '-'})` : `${key}: ${displayValue}${unit}`}
          >
            <span style={{ color: 'var(--color-text-tertiary)' }}>{key}:</span>
            <span className={valueColor} style={!valueColor ? { color: 'var(--color-text-primary)' } : undefined}>
              {displayValue}{unit}
            </span>
          </span>
        );
      })}
    </div>
  );
}

function StepRow({ step, onClick }: { step: StepResult; onClick?: () => void }) {
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
      onClick={onClick}
      className={`border-b transition-colors ${onClick ? 'cursor-pointer hover:bg-zinc-800/50' : ''}`}
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
      <td className="py-3 pr-4">
        <MeasurementsCell measurements={step.result?.measurements as Record<string, unknown> | undefined} />
      </td>
      <td className="py-3 pr-4 font-mono" style={{ color: 'var(--color-text-secondary)' }}>
        {step.duration != null ? `${step.duration.toFixed(2)}s` : '-'}
      </td>
    </tr>
  );
}
