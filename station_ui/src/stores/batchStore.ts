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
  updateBatchStatus: (batchId: string, status: BatchStatus, executionId?: string) => void;
  setLastRunResult: (batchId: string, passed: boolean) => void;
  updateStepProgress: (
    batchId: string,
    currentStep: string,
    stepIndex: number,
    progress: number,
    executionId?: string
  ) => void;
  updateStepResult: (batchId: string, stepResult: StepResult) => void;
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
          // Never allow completed state to be reverted to running by stale API data
          // This prevents the bug where navigating between pages causes status regression
          if (existing.status === 'completed' && (batch.status === 'running' || batch.status === 'starting')) {
            console.log(`[batchStore] setBatches: BLOCKED status regression ${existing.status} -> ${batch.status} for ${batch.id.slice(0, 8)}...`);
            newBatches.set(batch.id, existing);
            continue;
          }

          // Preserve real-time WebSocket updates for running/starting batches
          // (API polling data might be stale during active execution)
          if (existing.status === 'running' || existing.status === 'starting') {
            newBatches.set(batch.id, {
              ...batch,
              status: existing.status,
              currentStep: existing.currentStep,
              stepIndex: existing.stepIndex,
              progress: existing.progress,
              lastRunPassed: existing.lastRunPassed,
              executionId: existing.executionId,
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

  updateBatchStatus: (batchId, status, executionId?) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      const batch = state.batches.get(batchId);
      console.log(`[batchStore] updateBatchStatus: ${batchId.slice(0, 8)}... status=${status}, exec=${executionId}, exists=${!!batch}, currentStatus=${batch?.status}`);

      // Note: No guard here - explicit status updates from server should always be trusted
      // Race condition guards are handled in WebSocketContext.tsx for specific message types

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
          elapsed: 0,
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
        newBatches.set(batchId, {
          ...batch,
          currentStep,
          stepIndex,
          progress,
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
