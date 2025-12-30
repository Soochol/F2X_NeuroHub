/**
 * Batch state store.
 * Manages batch data, statistics, and real-time updates from WebSocket.
 * Locally created batches are persisted to localStorage.
 */

import { create } from 'zustand';
import type { Batch, BatchStatus, StepResult, BatchStatistics } from '../types';

// Storage key for local batches
const LOCAL_BATCHES_KEY = 'station-ui-local-batches';
const LOCAL_STATS_KEY = 'station-ui-local-batch-stats';
const LOCAL_STEPS_KEY = 'station-ui-local-batch-steps';

interface BatchState {
  // State
  batches: Map<string, Batch>;
  localBatches: Map<string, Batch>; // Locally created batches (persisted)
  localBatchStats: Map<string, BatchStatistics>; // Stats for local batches (persisted)
  localBatchSteps: Map<string, StepResult[]>; // Step results for local batches (persisted)
  selectedBatchId: string | null;
  batchStatistics: Map<string, BatchStatistics>;
  isWizardOpen: boolean;

  // Actions
  setBatches: (batches: Batch[]) => void;
  updateBatch: (batch: Batch) => void;
  addLocalBatch: (batch: Batch) => void; // Add locally created batch
  removeLocalBatch: (batchId: string) => void; // Remove local batch
  updateBatchStatus: (batchId: string, status: BatchStatus) => void;
  setLastRunResult: (batchId: string, passed: boolean) => void;
  updateStepProgress: (
    batchId: string,
    currentStep: string,
    stepIndex: number,
    progress: number
  ) => void;
  updateStepResult: (batchId: string, stepResult: StepResult) => void;
  setLocalBatchSteps: (batchId: string, steps: StepResult[]) => void;
  updateLocalBatchStep: (batchId: string, stepIndex: number, step: StepResult) => void;
  clearLocalBatchSteps: (batchId: string) => void;
  selectBatch: (batchId: string | null) => void;
  clearBatches: () => void;

  // Statistics actions
  setBatchStatistics: (batchId: string, stats: BatchStatistics) => void;
  setLocalBatchStatistics: (batchId: string, stats: BatchStatistics) => void;
  setAllBatchStatistics: (stats: Record<string, BatchStatistics>) => void;
  incrementBatchStats: (batchId: string, passed: boolean) => void;

  // Wizard actions
  openWizard: () => void;
  closeWizard: () => void;

  // Selectors
  getBatch: (batchId: string) => Batch | undefined;
  getAllBatches: () => Batch[]; // Get all batches (API + local)
  getRunningBatches: () => Batch[];
  getSelectedBatch: () => Batch | undefined;
  getBatchStats: (batchId: string) => BatchStatistics | undefined;
  getLocalBatchSteps: (batchId: string) => StepResult[];
  getTotalStats: () => BatchStatistics;
}

// Helper to convert Map to array for JSON serialization
const mapToArray = <T>(map: Map<string, T>): [string, T][] => Array.from(map.entries());

// Load persisted local batches from localStorage
const loadPersistedBatches = (): Map<string, Batch> => {
  try {
    const stored = localStorage.getItem(LOCAL_BATCHES_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as [string, Batch][];
      return new Map(parsed);
    }
  } catch (e) {
    console.warn('Failed to load local batches:', e);
  }
  return new Map();
};

const loadPersistedStats = (): Map<string, BatchStatistics> => {
  try {
    const stored = localStorage.getItem(LOCAL_STATS_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as [string, BatchStatistics][];
      return new Map(parsed);
    }
  } catch (e) {
    console.warn('Failed to load local batch stats:', e);
  }
  return new Map();
};

// Save local batches to localStorage
const persistBatches = (batches: Map<string, Batch>) => {
  try {
    localStorage.setItem(LOCAL_BATCHES_KEY, JSON.stringify(mapToArray(batches)));
  } catch (e) {
    console.warn('Failed to persist local batches:', e);
  }
};

const persistStats = (stats: Map<string, BatchStatistics>) => {
  try {
    localStorage.setItem(LOCAL_STATS_KEY, JSON.stringify(mapToArray(stats)));
  } catch (e) {
    console.warn('Failed to persist local batch stats:', e);
  }
};

const loadPersistedSteps = (): Map<string, StepResult[]> => {
  try {
    const stored = localStorage.getItem(LOCAL_STEPS_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as [string, StepResult[]][];
      return new Map(parsed);
    }
  } catch (e) {
    console.warn('Failed to load local batch steps:', e);
  }
  return new Map();
};

const persistSteps = (steps: Map<string, StepResult[]>) => {
  try {
    localStorage.setItem(LOCAL_STEPS_KEY, JSON.stringify(mapToArray(steps)));
  } catch (e) {
    console.warn('Failed to persist local batch steps:', e);
  }
};

export const useBatchStore = create<BatchState>((set, get) => ({
  // Initial state
  batches: new Map(),
  localBatches: loadPersistedBatches(),
  localBatchStats: loadPersistedStats(),
  localBatchSteps: loadPersistedSteps(),
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

  addLocalBatch: (batch) =>
    set((state) => {
      const newLocalBatches = new Map(state.localBatches);
      newLocalBatches.set(batch.id, batch);
      persistBatches(newLocalBatches);
      return { localBatches: newLocalBatches };
    }),

  removeLocalBatch: (batchId) =>
    set((state) => {
      const newLocalBatches = new Map(state.localBatches);
      newLocalBatches.delete(batchId);
      persistBatches(newLocalBatches);

      const newLocalStats = new Map(state.localBatchStats);
      newLocalStats.delete(batchId);
      persistStats(newLocalStats);

      return { localBatches: newLocalBatches, localBatchStats: newLocalStats };
    }),

  updateBatchStatus: (batchId, status) =>
    set((state) => {
      // Check in API batches first
      const batch = state.batches.get(batchId);
      if (batch) {
        const newBatches = new Map(state.batches);
        newBatches.set(batchId, { ...batch, status });
        return { batches: newBatches };
      }

      // Check in local batches
      const localBatch = state.localBatches.get(batchId);
      if (localBatch) {
        const newLocalBatches = new Map(state.localBatches);
        newLocalBatches.set(batchId, { ...localBatch, status });
        persistBatches(newLocalBatches);
        return { localBatches: newLocalBatches };
      }

      return state;
    }),

  setLastRunResult: (batchId, passed) =>
    set((state) => {
      // Check in API batches first
      const batch = state.batches.get(batchId);
      if (batch) {
        const newBatches = new Map(state.batches);
        newBatches.set(batchId, { ...batch, lastRunPassed: passed });
        return { batches: newBatches };
      }

      // Check in local batches
      const localBatch = state.localBatches.get(batchId);
      if (localBatch) {
        const newLocalBatches = new Map(state.localBatches);
        newLocalBatches.set(batchId, { ...localBatch, lastRunPassed: passed });
        persistBatches(newLocalBatches);
        return { localBatches: newLocalBatches };
      }

      return state;
    }),

  updateStepProgress: (batchId, currentStep, stepIndex, progress) =>
    set((state) => {
      // Check in API batches first
      const batch = state.batches.get(batchId);
      if (batch) {
        const newBatches = new Map(state.batches);
        newBatches.set(batchId, {
          ...batch,
          currentStep,
          stepIndex,
          progress,
        });
        return { batches: newBatches };
      }

      // Check in local batches
      const localBatch = state.localBatches.get(batchId);
      if (localBatch) {
        const newLocalBatches = new Map(state.localBatches);
        newLocalBatches.set(batchId, {
          ...localBatch,
          currentStep,
          stepIndex,
          progress,
        });
        persistBatches(newLocalBatches);
        return { localBatches: newLocalBatches };
      }

      return state;
    }),

  updateStepResult: (batchId, stepResult) =>
    set((state) => {
      const batch = state.batches.get(batchId);
      if (!batch) return state;

      const newBatches = new Map(state.batches);
      newBatches.set(batchId, {
        ...batch,
        stepIndex: stepResult.order,
        progress: batch.totalSteps > 0 ? stepResult.order / batch.totalSteps : 0,
      });
      return { batches: newBatches };
    }),

  setLocalBatchSteps: (batchId, steps) =>
    set((state) => {
      const newSteps = new Map(state.localBatchSteps);
      newSteps.set(batchId, steps);
      persistSteps(newSteps);
      return { localBatchSteps: newSteps };
    }),

  updateLocalBatchStep: (batchId, stepIndex, step) =>
    set((state) => {
      const newSteps = new Map(state.localBatchSteps);
      const currentSteps = newSteps.get(batchId) || [];
      const updatedSteps = [...currentSteps];
      updatedSteps[stepIndex] = step;
      newSteps.set(batchId, updatedSteps);
      persistSteps(newSteps);
      return { localBatchSteps: newSteps };
    }),

  clearLocalBatchSteps: (batchId) =>
    set((state) => {
      const newSteps = new Map(state.localBatchSteps);
      newSteps.delete(batchId);
      persistSteps(newSteps);
      return { localBatchSteps: newSteps };
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

  setLocalBatchStatistics: (batchId, stats) =>
    set((state) => {
      const newLocalStats = new Map(state.localBatchStats);
      newLocalStats.set(batchId, stats);
      persistStats(newLocalStats);
      return { localBatchStats: newLocalStats };
    }),

  setAllBatchStatistics: (stats) =>
    set({
      batchStatistics: new Map(Object.entries(stats)),
    }),

  incrementBatchStats: (batchId, passed) =>
    set((state) => {
      // Check if it's a local batch
      if (state.localBatches.has(batchId)) {
        const newLocalStats = new Map(state.localBatchStats);
        const current = newLocalStats.get(batchId) || { total: 0, pass: 0, fail: 0, passRate: 0 };
        const updated = {
          total: current.total + 1,
          pass: passed ? current.pass + 1 : current.pass,
          fail: passed ? current.fail : current.fail + 1,
          passRate: 0,
        };
        updated.passRate = updated.total > 0 ? updated.pass / updated.total : 0;
        newLocalStats.set(batchId, updated);
        persistStats(newLocalStats);
        return { localBatchStats: newLocalStats };
      }

      // API batch
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
    const { batches, localBatches } = get();
    return batches.get(batchId) || localBatches.get(batchId);
  },

  getAllBatches: () => {
    const { batches, localBatches } = get();
    return [...Array.from(batches.values()), ...Array.from(localBatches.values())];
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
    const { batchStatistics, localBatchStats } = get();
    return batchStatistics.get(batchId) || localBatchStats.get(batchId);
  },

  getLocalBatchSteps: (batchId) => {
    const { localBatchSteps } = get();
    return localBatchSteps.get(batchId) || [];
  },

  getTotalStats: () => {
    const { batchStatistics, localBatchStats } = get();
    const total = { total: 0, pass: 0, fail: 0, passRate: 0 };

    batchStatistics.forEach((s) => {
      total.total += s.total;
      total.pass += s.pass;
      total.fail += s.fail;
    });

    localBatchStats.forEach((s) => {
      total.total += s.total;
      total.pass += s.pass;
      total.fail += s.fail;
    });

    total.passRate = total.total > 0 ? total.pass / total.total : 0;
    return total;
  },
}));
