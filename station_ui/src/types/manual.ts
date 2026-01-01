/**
 * Manual Control Type Definitions.
 *
 * Types for enhanced manual control page functionality.
 */

/**
 * Parameter definition for a hardware command.
 */
export interface CommandParameter {
  /** Parameter name */
  name: string;
  /** Display name for UI */
  displayName: string;
  /** Parameter type */
  type: 'string' | 'number' | 'boolean' | 'select' | 'range';
  /** Whether parameter is required */
  required: boolean;
  /** Default value */
  default?: unknown;
  /** Unit of measurement */
  unit?: string;
  /** Minimum value for numbers */
  min?: number;
  /** Maximum value for numbers */
  max?: number;
  /** Options for select type */
  options?: Array<{ value: unknown; label: string }>;
  /** Parameter description */
  description?: string;
}

/**
 * Hardware command definition.
 */
export interface CommandInfo {
  /** Command/method name */
  name: string;
  /** Display name for UI */
  displayName: string;
  /** Command description */
  description: string;
  /** Category: measurement, control, configuration, diagnostic */
  category: 'measurement' | 'control' | 'configuration' | 'diagnostic';
  /** Command parameters */
  parameters: CommandParameter[];
  /** Return type */
  returnType: string;
  /** Return unit */
  returnUnit?: string;
  /** Whether command is async */
  async: boolean;
}

/**
 * Response containing available commands for a hardware device.
 */
export interface HardwareCommandsResponse {
  /** Hardware device ID */
  hardwareId: string;
  /** Driver class name */
  driver: string;
  /** Whether device is connected */
  connected: boolean;
  /** Available commands */
  commands: CommandInfo[];
}

/**
 * Detailed hardware status.
 */
export interface HardwareDetailedStatus {
  /** Hardware device ID */
  id: string;
  /** Driver class name */
  driver: string;
  /** Connection status */
  status: 'connected' | 'disconnected' | 'error';
  /** Whether connected */
  connected: boolean;
  /** Configuration */
  config: Record<string, unknown>;
  /** Device info */
  info: Record<string, unknown>;
  /** Last error message */
  lastError?: string;
}

/**
 * Manual step configuration.
 */
export interface ManualStepConfig {
  /** Can be skipped in manual mode */
  skippable: boolean;
  /** Only runs in automatic mode */
  autoOnly: boolean;
  /** Confirmation prompt */
  prompt?: string;
  /** Pause before execution */
  pauseBefore: boolean;
  /** Pause after execution */
  pauseAfter: boolean;
  /** Parameters that can be overridden */
  parameterOverrides: string[];
}

/**
 * Step information for manual execution.
 */
export interface ManualStepInfo {
  /** Step name */
  name: string;
  /** Display name */
  displayName: string;
  /** Execution order */
  order: number;
  /** Timeout in seconds */
  timeout: number;
  /** Manual mode config */
  manual: ManualStepConfig;
  /** Current status */
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  /** Step result */
  result?: Record<string, unknown>;
  /** Execution duration */
  duration?: number;
}

/**
 * Command preset for quick access.
 */
export interface CommandPreset {
  /** Preset ID */
  id: string;
  /** Preset name */
  name: string;
  /** Hardware device ID */
  hardwareId: string;
  /** Command name */
  command: string;
  /** Command parameters */
  params: Record<string, unknown>;
  /** Creation timestamp */
  createdAt: string;
}

/**
 * Request body for creating a command preset.
 */
export interface CreatePresetRequest {
  /** Preset name */
  name: string;
  /** Hardware device ID */
  hardwareId: string;
  /** Command name */
  command: string;
  /** Command parameters */
  params: Record<string, unknown>;
}

/**
 * Result history entry.
 */
export interface ResultHistoryEntry {
  /** Unique ID */
  id: string;
  /** Hardware device ID */
  hardware: string;
  /** Command executed */
  command: string;
  /** Command parameters */
  params: Record<string, unknown>;
  /** Execution result */
  result: unknown;
  /** Whether execution succeeded */
  success: boolean;
  /** Execution duration in ms */
  duration: number;
  /** Timestamp */
  timestamp: Date;
  /** Unit for numeric results */
  unit?: string;
}

/**
 * Manual control state for Zustand store.
 */
export interface ManualControlState {
  /** Selected batch ID */
  selectedBatchId: string | null;
  /** Selected hardware ID */
  selectedHardwareId: string | null;
  /** Selected command */
  selectedCommand: CommandInfo | null;
  /** Parameter values */
  parameterValues: Record<string, unknown>;
  /** Result history */
  resultHistory: ResultHistoryEntry[];
  /** Command presets */
  presets: CommandPreset[];

  // Manual sequence mode
  /** Whether manual sequence mode is enabled */
  manualSequenceMode: boolean;
  /** Sequence steps */
  sequenceSteps: ManualStepInfo[];
  /** Current step index */
  currentStepIndex: number;
  /** Parameter overrides per step */
  stepOverrides: Record<string, Record<string, unknown>>;

  // Actions
  selectDevice: (batchId: string | null, hardwareId: string | null) => void;
  selectCommand: (command: CommandInfo | null) => void;
  setParameterValue: (name: string, value: unknown) => void;
  setParameterValues: (values: Record<string, unknown>) => void;
  addResultToHistory: (entry: Omit<ResultHistoryEntry, 'id' | 'timestamp'>) => void;
  clearHistory: () => void;
  addPreset: (preset: CommandPreset) => void;
  removePreset: (presetId: string) => void;

  // Manual sequence actions
  setManualSequenceMode: (enabled: boolean) => void;
  setSequenceSteps: (steps: ManualStepInfo[]) => void;
  updateStepStatus: (
    stepName: string,
    status: ManualStepInfo['status'],
    result?: Record<string, unknown>,
    duration?: number
  ) => void;
  setCurrentStepIndex: (index: number) => void;
  setStepOverride: (stepName: string, overrides: Record<string, unknown>) => void;
  resetSequence: () => void;
}
