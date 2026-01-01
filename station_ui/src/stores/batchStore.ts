/**
 * Batch state store.
 * Manages batch data, statistics, and real-time updates from WebSocket.
 * All batches are server-managed - local batch creation is not supported.
 */

import { create } from 'zustand';
import type { Batch, BatchStatus, StepResult, BatchStatistics } from '../types';

// Legacy storage keys - will be cleaned up on initialization
const LEGACY_LOCAL_BATCHES_KEY = 'station-ui-local-batches';
const LEGACY_LOCAL_STATS_KEY = 'station-ui-local-batch-stats';
const LEGACY_LOCAL_STEPS_KEY = 'station-ui-local-batch-steps';

// Clean up legacy local batches from localStorage
function cleanupLegacyLocalBatches(): void {
  try {
    const removedKeys: string[] = [];
    if (localStorage.getItem(LEGACY_LOCAL_BATCHES_KEY)) {
      localStorage.removeItem(LEGACY_LOCAL_BATCHES_KEY);
      removedKeys.push(LEGACY_LOCAL_BATCHES_KEY);
    }
    if (localStorage.getItem(LEGACY_LOCAL_STATS_KEY)) {
      localStorage.removeItem(LEGACY_LOCAL_STATS_KEY);
      removedKeys.push(LEGACY_LOCAL_STATS_KEY);
    }
    if (localStorage.getItem(LEGACY_LOCAL_STEPS_KEY)) {
      localStorage.removeItem(LEGACY_LOCAL_STEPS_KEY);
      removedKeys.push(LEGACY_LOCAL_STEPS_KEY);
    }
    if (removedKeys.length > 0) {
      console.info('Cleaned up legacy local batch data:', removedKeys);
    }
  } catch (e) {
    console.warn('Failed to cleanup legacy local batches:', e);
  }
}

// Run cleanup on module load
cleanupLegacyLocalBatches();

/**
 * Ensures a batch exists in the store, creating a minimal entry if needed.
 * This handles WebSocket events arriving before API data.
 *
 * @param batches - Current batches Map
 * @param batchId - Batch ID to ensure exists
 * @param options - Optional fields to set on new batch
 * @returns Tuple of [updated batches Map, batch object guaranteed to exist]
 */
function ensureBatchExists(
  batches: Map<string, Batch>,
  batchId: string,
  options?: {
    status?: BatchStatus;
    executionId?: string;
    progress?: number;
  }
): [Map<string, Batch>, Batch] {
  const existing = batches.get(batchId);
  if (existing) {
    return [batches, existing];
  }

  // Create minimal batch entry for WebSocket events arriving before API data
  const newBatches = new Map(batches);
  const newBatch: Batch = {
    id: batchId,
    name: 'Loading...',
    status: options?.status ?? 'running',
    progress: options?.progress ?? 0,
    executionId: options?.executionId,
    sequencePackage: '',
    elapsed: 0,
    hardwareConfig: {},
    autoStart: false,
    steps: [],
  };
  newBatches.set(batchId, newBatch);
  console.log(`[batchStore] ensureBatchExists: Created minimal batch for ${batchId.slice(0, 8)}...`);

  return [newBatches, newBatch];
}

interface BatchState {
  // State
  batches: Map<string, Batch>;
  batchesVersion: number; // Version counter to trigger re-renders when batches change
  selectedBatchId: string | null;
  batchStatistics: Map<string, BatchStatistics>;
  isWizardOpen: boolean;

  // Actions
  setBatches: (batches: Batch[]) => void;
  updateBatch: (batch: Batch) => void;
  removeBatch: (batchId: string) => void;
  updateBatchStatus: (batchId: string, status: BatchStatus, executionId?: string, elapsed?: number, force?: boolean) => void;
  setLastRunResult: (batchId: string, passed: boolean) => void;
  updateStepProgress: (
    batchId: string,
    currentStep: string,
    stepIndex: number,
    progress: number,
    executionId?: string
  ) => void;
  updateStepResult: (batchId: string, stepResult: StepResult) => void;
  startStep: (batchId: string, stepName: string, stepIndex: number, totalSteps: number, executionId?: string) => void;
  completeStep: (batchId: string, stepName: string, stepIndex: number, duration: number, pass: boolean, result?: Record<string, unknown>, executionId?: string) => void;
  clearSteps: (batchId: string) => void;
  selectBatch: (batchId: string | null) => void;
  clearBatches: () => void;

  // Statistics actions
  setBatchStatistics: (batchId: string, stats: BatchStatistics) => void;
  setAllBatchStatistics: (stats: Record<string, BatchStatistics>) => void;
  incrementBatchStats: (batchId: string, passed: boolean) => void;

  // Wizard actions
  openWizard: () => void;
  closeWizard: () => void;

  // Selectors
  getBatch: (batchId: string) => Batch | undefined;
  getAllBatches: () => Batch[];
  getRunningBatches: () => Batch[];
  getSelectedBatch: () => Batch | undefined;
  getBatchStats: (batchId: string) => BatchStatistics | undefined;
  getTotalStats: () => BatchStatistics;
}

export const useBatchStore = create<BatchState>((set, get) => ({
  // Initial state
  batches: new Map(),
  batchesVersion: 0,
  selectedBatchId: null,
  batchStatistics: new Map(),
  isWizardOpen: false,

  // Actions
  setBatches: (batches) =>
    set((state) => {
      const newBatches = new Map<string, Batch>();
      for (const batch of batches) {
        const existing = state.batches.get(batch.id);

        if (existing) {
          // Never allow completed state to be reverted by stale API data
          // This prevents the bug where navigating between pages causes status regression
          // After sequence completes, worker sets status to 'idle' but we want to keep 'completed'
          if (existing.status === 'completed' && batch.status !== 'completed') {
            console.log(`[batchStore] setBatches: BLOCKED status regression ${existing.status} -> ${batch.status} for ${batch.id.slice(0, 8)}...`);
            newBatches.set(batch.id, existing);
            continue;
          }

          // === Clear Ownership Model for Steps ===
          // - Running/starting/stopping: WebSocket is Source of Truth (real-time events)
          // - Completed: API is Source of Truth (persisted in DB)
          // This is simpler and more predictable than merge logic

          // Preserve real-time WebSocket updates for running/starting/stopping batches
          // WebSocket owns ALL data during active execution
          if (existing.status === 'running' || existing.status === 'starting' || existing.status === 'stopping') {
            newBatches.set(batch.id, {
              ...batch,
              status: existing.status,
              currentStep: existing.currentStep,
              stepIndex: existing.stepIndex,
              progress: existing.progress,
              lastRunPassed: existing.lastRunPassed,
              executionId: existing.executionId,
              steps: existing.steps || [],  // WebSocket owns steps during execution
            });
            continue;
          }

          // For completed batches: API owns steps (persisted data)
          // Fallback to existing steps only if API returns empty (shouldn't happen normally)
          if (existing.status === 'completed' && batch.status === 'completed') {
            const apiSteps = batch.steps || [];
            const existingSteps = existing.steps || [];
            newBatches.set(batch.id, {
              ...batch,
              steps: apiSteps.length > 0 ? apiSteps : existingSteps,
            });
            continue;
          }
        }

        // Default: use API data for new batches or stable states (idle, completed, error)
        newBatches.set(batch.id, batch);
      }
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  updateBatch: (batch) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      newBatches.set(batch.id, batch);
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  removeBatch: (batchId) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      newBatches.delete(batchId);
      const newStats = new Map(state.batchStatistics);
      newStats.delete(batchId);
      return { batches: newBatches, batchStatistics: newStats, batchesVersion: state.batchesVersion + 1 };
    }),

  updateBatchStatus: (batchId, status, executionId?, elapsed?, force?) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      const batch = state.batches.get(batchId);
      console.log(`[batchStore] updateBatchStatus: ${batchId.slice(0, 8)}... status=${status}, exec=${executionId}, elapsed=${elapsed}, exists=${!!batch}, currentStatus=${batch?.status}, force=${!!force}`);

      // Prevent status regression from stale messages
      // Protect transitional states (starting, stopping) and completed state
      // Exception: force=true bypasses guards for authoritative server updates (e.g., initial status push after subscribe)
      if (batch && !force) {
        const currentStatus = batch.status;

        // Don't allow completed to be reverted (except to error)
        if (currentStatus === 'completed' && status !== 'completed' && status !== 'error' && status !== 'starting') {
          console.log(`[batchStore] updateBatchStatus: BLOCKED regression ${currentStatus} -> ${status}`);
          return state;
        }

        // Don't allow starting to be reverted to idle (optimistic update protection)
        if (currentStatus === 'starting' && status === 'idle') {
          console.log(`[batchStore] updateBatchStatus: BLOCKED regression ${currentStatus} -> ${status} (optimistic protection)`);
          return state;
        }

        // Don't allow stopping to be reverted to running (optimistic update protection)
        if (currentStatus === 'stopping' && status === 'running') {
          console.log(`[batchStore] updateBatchStatus: BLOCKED regression ${currentStatus} -> ${status} (optimistic protection)`);
          return state;
        }
      }

      if (batch) {
        // When transitioning to 'completed', also set progress to 100%
        const updates: Partial<typeof batch> = { status };
        if (status === 'completed') {
          updates.progress = 1.0;
        }
        // Track execution ID for race condition detection
        if (executionId) {
          updates.executionId = executionId;
        }
        // Update elapsed time when sequence completes
        if (elapsed !== undefined) {
          updates.elapsed = elapsed;
        }
        newBatches.set(batchId, { ...batch, ...updates });
      } else {
        // Create minimal batch entry for WebSocket updates that arrive before API data
        newBatches.set(batchId, {
          id: batchId,
          name: 'Loading...',
          status,
          progress: status === 'completed' ? 1.0 : 0,
          executionId,
          sequencePackage: '',
          elapsed: elapsed ?? 0,
          hardwareConfig: {},
          autoStart: false,
        });
      }
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  setLastRunResult: (batchId, passed) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      const batch = state.batches.get(batchId);
      if (batch) {
        newBatches.set(batchId, { ...batch, lastRunPassed: passed });
      } else {
        // Create minimal batch entry for WebSocket updates that arrive before API data
        newBatches.set(batchId, {
          id: batchId,
          name: 'Loading...',
          status: 'completed',
          progress: 1,
          lastRunPassed: passed,
          sequencePackage: '',
          elapsed: 0,
          hardwareConfig: {},
          autoStart: false,
        });
      }
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  updateStepProgress: (batchId, currentStep, stepIndex, progress, executionId?) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      const batch = state.batches.get(batchId);
      console.log(`[batchStore] updateStepProgress: ${batchId.slice(0, 8)}... step=${currentStep}, progress=${progress.toFixed(2)}, exec=${executionId}, exists=${!!batch}, currentStatus=${batch?.status}`);

      // Race condition guard: ignore updates from old executions
      if (batch && executionId && batch.executionId && batch.executionId !== executionId) {
        console.log(`[batchStore] IGNORED: executionId mismatch (batch=${batch.executionId}, event=${executionId})`);
        return state;
      }

      if (batch) {
        // Prevent progress regression - step_complete calculates accurate progress from completed steps
        // Stale batch_status messages may arrive with lower progress values
        const newProgress = Math.max(batch.progress, progress);
        if (progress < batch.progress) {
          console.log(`[batchStore] updateStepProgress: BLOCKED progress regression ${batch.progress.toFixed(2)} -> ${progress.toFixed(2)} for ${batchId.slice(0, 8)}...`);
        }
        newBatches.set(batchId, {
          ...batch,
          currentStep,
          stepIndex,
          progress: newProgress,
          executionId: executionId || batch.executionId,
        });
      } else {
        // Create minimal batch entry for WebSocket updates that arrive before API data
        newBatches.set(batchId, {
          id: batchId,
          name: 'Loading...',
          status: 'running',
          currentStep,
          stepIndex,
          progress,
          executionId,
          sequencePackage: '',
          elapsed: 0,
          hardwareConfig: {},
          autoStart: false,
        });
      }
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  updateStepResult: (batchId, stepResult) =>
    set((state) => {
      const batch = state.batches.get(batchId);
      if (!batch) return state;

      const newBatches = new Map(state.batches);
      newBatches.set(batchId, {
        ...batch,
        stepIndex: stepResult.order,
        progress: (batch.totalSteps ?? 0) > 0 ? stepResult.order / batch.totalSteps! : 0,
      });
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  startStep: (batchId, stepName, stepIndex, totalSteps, executionId?) =>
    set((state) => {
      // Ensure batch exists (handles WS events before API data)
      const [batchesWithEntry, batch] = ensureBatchExists(
        state.batches,
        batchId,
        { status: 'running', executionId }
      );

      // Race condition guard - only check if both have executionId
      if (executionId && batch.executionId && batch.executionId !== executionId) {
        console.log(`[batchStore] startStep IGNORED: executionId mismatch`);
        return state;
      }

      const newBatches = new Map(batchesWithEntry);
      const currentSteps = batch.steps || [];

      // Check if step already exists
      const existingIndex = currentSteps.findIndex(s => s.name === stepName && s.order === stepIndex + 1);
      let newSteps: StepResult[];

      if (existingIndex >= 0) {
        // Update existing step to running
        newSteps = [...currentSteps];
        const existingStep = newSteps[existingIndex]!;
        newSteps[existingIndex] = {
          order: existingStep.order,
          name: existingStep.name,
          status: 'running' as const,
          pass: existingStep.pass,
          duration: existingStep.duration,
          result: existingStep.result,
        };
      } else {
        // Add new running step
        newSteps = [
          ...currentSteps,
          {
            order: stepIndex + 1,
            name: stepName,
            status: 'running' as const,
            pass: false,
            duration: undefined,
            result: undefined,
          },
        ];
      }

      newBatches.set(batchId, {
        ...batch,
        currentStep: stepName,
        stepIndex,
        totalSteps,
        steps: newSteps,
        executionId: executionId || batch.executionId,
      });

      console.log(`[batchStore] startStep: ${batchId.slice(0, 8)}... step=${stepName} index=${stepIndex}`);
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  completeStep: (batchId, stepName, stepIndex, duration, pass, result?, executionId?) =>
    set((state) => {
      // Ensure batch exists (handles WS events before API data)
      const [batchesWithEntry, batch] = ensureBatchExists(
        state.batches,
        batchId,
        { status: 'running', executionId }
      );

      // Race condition guard - only check if both have executionId
      if (executionId && batch.executionId && batch.executionId !== executionId) {
        console.log(`[batchStore] completeStep IGNORED: executionId mismatch`);
        return state;
      }

      const newBatches = new Map(batchesWithEntry);
      const currentSteps = batch.steps || [];

      // Find and update the step
      const existingIndex = currentSteps.findIndex(s => s.name === stepName);
      let newSteps: StepResult[];

      if (existingIndex >= 0) {
        newSteps = [...currentSteps];
        newSteps[existingIndex] = {
          order: stepIndex + 1,
          name: stepName,
          status: 'completed' as const,
          pass,
          duration,
          result,
        };
      } else {
        // Add completed step if not found
        newSteps = [
          ...currentSteps,
          {
            order: stepIndex + 1,
            name: stepName,
            status: 'completed' as const,
            pass,
            duration,
            result,
          },
        ];
      }

      // Calculate new progress
      const totalSteps = batch.totalSteps || newSteps.length;
      const completedSteps = newSteps.filter(s => s.status === 'completed').length;
      const progress = totalSteps > 0 ? completedSteps / totalSteps : 0;

      newBatches.set(batchId, {
        ...batch,
        stepIndex: stepIndex + 1,
        steps: newSteps,
        progress,
        executionId: executionId || batch.executionId,
      });

      console.log(`[batchStore] completeStep: ${batchId.slice(0, 8)}... step=${stepName} pass=${pass} progress=${progress.toFixed(2)}`);
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  clearSteps: (batchId) =>
    set((state) => {
      const batch = state.batches.get(batchId);
      if (!batch) return state;

      const newBatches = new Map(state.batches);
      newBatches.set(batchId, {
        ...batch,
        steps: [],
        stepIndex: 0,
        progress: 0,
        currentStep: undefined,
      });
      return { batches: newBatches, batchesVersion: state.batchesVersion + 1 };
    }),

  selectBatch: (batchId) => set({ selectedBatchId: batchId }),

  clearBatches: () => set((state) => ({ batches: new Map(), batchesVersion: state.batchesVersion + 1 })),

  // Statistics actions
  setBatchStatistics: (batchId, stats) =>
    set((state) => {
      const newStats = new Map(state.batchStatistics);
      newStats.set(batchId, stats);
      return { batchStatistics: newStats };
    }),

  setAllBatchStatistics: (stats) =>
    set({
      batchStatistics: new Map(Object.entries(stats)),
    }),

  incrementBatchStats: (batchId, passed) =>
    set((state) => {
      const newStats = new Map(state.batchStatistics);
      const current = newStats.get(batchId) || { total: 0, pass: 0, fail: 0, passRate: 0 };
      const updated = {
        total: current.total + 1,
        pass: passed ? current.pass + 1 : current.pass,
        fail: passed ? current.fail : current.fail + 1,
        passRate: 0,
      };
      updated.passRate = updated.total > 0 ? updated.pass / updated.total : 0;
      newStats.set(batchId, updated);
      return { batchStatistics: newStats };
    }),

  // Wizard actions
  openWizard: () => set({ isWizardOpen: true }),
  closeWizard: () => set({ isWizardOpen: false }),

  // Selectors
  getBatch: (batchId) => {
    const { batches } = get();
    return batches.get(batchId);
  },

  getAllBatches: () => {
    const { batches } = get();
    return Array.from(batches.values());
  },

  getRunningBatches: () => {
    const allBatches = get().getAllBatches();
    return allBatches.filter((b) => b.status === 'running');
  },

  getSelectedBatch: () => {
    const { selectedBatchId } = get();
    return selectedBatchId ? get().getBatch(selectedBatchId) : undefined;
  },

  getBatchStats: (batchId) => {
    const { batchStatistics } = get();
    return batchStatistics.get(batchId);
  },

  getTotalStats: () => {
    const { batchStatistics } = get();
    const total = { total: 0, pass: 0, fail: 0, passRate: 0 };

    batchStatistics.forEach((s) => {
      total.total += s.total;
      total.pass += s.pass;
      total.fail += s.fail;
    });

    total.passRate = total.total > 0 ? total.pass / total.total : 0;
    return total;
  },
}));
