/**
 * Manual Control Store
 *
 * Zustand store for managing manual control page state.
 */

import { create } from 'zustand';
import type {
  ManualControlState,
  CommandInfo,
  CommandPreset,
  ManualStepInfo,
  ResultHistoryEntry,
} from '../types';

const MAX_HISTORY_SIZE = 50;

/**
 * Generate a unique ID for history entries.
 */
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

export const useManualControlStore = create<ManualControlState>((set) => ({
  // Device selection
  selectedBatchId: null,
  selectedHardwareId: null,

  // Command state
  selectedCommand: null,
  parameterValues: {},

  // Results
  resultHistory: [],

  // Presets
  presets: [],

  // Manual sequence mode
  manualSequenceMode: false,
  sequenceSteps: [],
  currentStepIndex: 0,
  stepOverrides: {},

  // Actions
  selectDevice: (batchId: string | null, hardwareId: string | null) => {
    set({
      selectedBatchId: batchId,
      selectedHardwareId: hardwareId,
      selectedCommand: null,
      parameterValues: {},
    });
  },

  selectCommand: (command: CommandInfo | null) => {
    // Initialize parameter values with defaults
    const parameterValues: Record<string, unknown> = {};
    if (command) {
      command.parameters.forEach((param) => {
        if (param.default !== undefined) {
          parameterValues[param.name] = param.default;
        }
      });
    }
    set({ selectedCommand: command, parameterValues });
  },

  setParameterValue: (name: string, value: unknown) => {
    set((state) => ({
      parameterValues: {
        ...state.parameterValues,
        [name]: value,
      },
    }));
  },

  setParameterValues: (values: Record<string, unknown>) => {
    set({ parameterValues: values });
  },

  addResultToHistory: (entry: Omit<ResultHistoryEntry, 'id' | 'timestamp'>) => {
    const newEntry: ResultHistoryEntry = {
      ...entry,
      id: generateId(),
      timestamp: new Date(),
    };

    set((state) => ({
      resultHistory: [newEntry, ...state.resultHistory].slice(0, MAX_HISTORY_SIZE),
    }));
  },

  clearHistory: () => {
    set({ resultHistory: [] });
  },

  addPreset: (preset: CommandPreset) => {
    set((state) => ({
      presets: [...state.presets, preset],
    }));
  },

  removePreset: (presetId: string) => {
    set((state) => ({
      presets: state.presets.filter((p) => p.id !== presetId),
    }));
  },

  // Manual sequence actions
  setManualSequenceMode: (enabled: boolean) => {
    set({ manualSequenceMode: enabled });
  },

  setSequenceSteps: (steps: ManualStepInfo[]) => {
    set({
      sequenceSteps: steps,
      currentStepIndex: 0,
      stepOverrides: {},
    });
  },

  updateStepStatus: (
    stepName: string,
    status: ManualStepInfo['status'],
    result?: Record<string, unknown>,
    duration?: number
  ) => {
    set((state) => ({
      sequenceSteps: state.sequenceSteps.map((step) =>
        step.name === stepName
          ? { ...step, status, result, duration }
          : step
      ),
    }));
  },

  setCurrentStepIndex: (index: number) => {
    set({ currentStepIndex: index });
  },

  setStepOverride: (stepName: string, overrides: Record<string, unknown>) => {
    set((state) => ({
      stepOverrides: {
        ...state.stepOverrides,
        [stepName]: overrides,
      },
    }));
  },

  resetSequence: () => {
    set((state) => ({
      sequenceSteps: state.sequenceSteps.map((step) => ({
        ...step,
        status: 'pending' as const,
        result: undefined,
        duration: undefined,
      })),
      currentStepIndex: 0,
    }));
  },
}));

/**
 * Selector for grouped commands by category.
 */
export const selectGroupedCommands = (commands: CommandInfo[]) => {
  const grouped: Record<string, CommandInfo[]> = {
    measurement: [],
    control: [],
    configuration: [],
    diagnostic: [],
  };

  commands.forEach((cmd) => {
    const category = cmd.category as keyof typeof grouped;
    if (grouped[category]) {
      grouped[category].push(cmd);
    }
  });

  return grouped;
};
