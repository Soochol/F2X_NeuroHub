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
  selectedBatchId: string | null;
  batchStatistics: Map<string, BatchStatistics>;
  isWizardOpen: boolean;

  // Actions
  setBatches: (batches: Batch[]) => void;
  updateBatch: (batch: Batch) => void;
  removeBatch: (batchId: string) => void;
  updateBatchStatus: (batchId: string, status: BatchStatus) => void;
  setLastRunResult: (batchId: string, passed: boolean) => void;
  updateStepProgress: (
    batchId: string,
    currentStep: string,
    stepIndex: number,
    progress: number
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
  selectedBatchId: null,
  batchStatistics: new Map(),
  isWizardOpen: false,

  // Actions
  setBatches: (batches) =>
    set({
      batches: new Map(batches.map((b) => [b.id, b])),
    }),

  updateBatch: (batch) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      newBatches.set(batch.id, batch);
      return { batches: newBatches };
    }),

  removeBatch: (batchId) =>
    set((state) => {
      const newBatches = new Map(state.batches);
      newBatches.delete(batchId);
      const newStats = new Map(state.batchStatistics);
      newStats.delete(batchId);
      return { batches: newBatches, batchStatistics: newStats };
    }),

  updateBatchStatus: (batchId, status) =>
    set((state) => {
      const batch = state.batches.get(batchId);
      if (!batch) return state;

      const newBatches = new Map(state.batches);
      newBatches.set(batchId, { ...batch, status });
      return { batches: newBatches };
    }),

  setLastRunResult: (batchId, passed) =>
    set((state) => {
      const batch = state.batches.get(batchId);
      if (!batch) return state;

      const newBatches = new Map(state.batches);
      newBatches.set(batchId, { ...batch, lastRunPassed: passed });
      return { batches: newBatches };
    }),

  updateStepProgress: (batchId, currentStep, stepIndex, progress) =>
    set((state) => {
      const batch = state.batches.get(batchId);
      if (!batch) return state;

      const newBatches = new Map(state.batches);
      newBatches.set(batchId, {
        ...batch,
        currentStep,
        stepIndex,
        progress,
      });
      return { batches: newBatches };
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
      return { batches: newBatches };
    }),

  selectBatch: (batchId) => set({ selectedBatchId: batchId }),

  clearBatches: () => set({ batches: new Map() }),

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
