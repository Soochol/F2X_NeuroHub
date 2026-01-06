/**
 * Batch type definitions.
 */

import type { ExecutionStatus, StepResult } from './execution';
import type { HardwareStatus } from './hardware';

/**
 * Batch execution status.
 */
export type BatchStatus = 'idle' | 'starting' | 'running' | 'stopping' | 'completed' | 'error';

/**
 * Batch statistics for pass/fail tracking.
 */
export interface BatchStatistics {
  /** Total number of executions */
  total: number;
  /** Number of passed executions */
  passCount: number;
  /** Number of failed executions */
  fail: number;
  /** Pass rate (0.0 to 1.0) */
  passRate: number;
  /** Average duration in seconds */
  avgDuration?: number;
  /** Last execution duration in seconds */
  lastDuration?: number;
}

/**
 * Step execution statistics within a batch.
 */
export interface StepStatistics {
  /** Step name */
  name: string;
  /** Step order */
  order: number;
  /** Total executions */
  total: number;
  /** Passed executions */
  pass: number;
  /** Failed executions */
  fail: number;
  /** Average duration in seconds */
  avgDuration: number;
  /** Last result data */
  lastResult?: Record<string, unknown>;
}

/**
 * Batch configuration for wizard.
 */
export interface BatchConfiguration {
  /** Batch ID */
  id: string;
  /** Batch name */
  name: string;
  /** Selected sequence name */
  sequenceName?: string;
  /** Selected sequence version */
  sequenceVersion?: string;
  /** Step order customization (step name to order mapping) */
  stepOrder: Array<{ name: string; order: number; enabled: boolean }>;
  /** Parameter overrides */
  parameters: Record<string, unknown>;
  /** Batch quantity for multiple runs */
  quantity: number;
}

/**
 * Represents a batch configuration and runtime state.
 */
export interface Batch {
  /** Batch ID (e.g., "batch_1") */
  id: string;
  /** Batch name (e.g., "Batch 1") */
  name: string;
  /** Current status */
  status: BatchStatus;
  /** Sequence name */
  sequenceName?: string;
  /** Sequence version */
  sequenceVersion?: string;
  /** Sequence package path */
  sequencePackage: string;

  /** Current step name */
  currentStep?: string;
  /** Current step index (0-based) */
  stepIndex?: number;
  /** Total number of steps */
  totalSteps?: number;
  /** Step names in order */
  stepNames?: string[];
  /** Step results (real-time updates from WebSocket) */
  steps?: StepResult[];
  /** Progress (0.0 to 1.0) */
  progress: number;
  /** Current execution ID (for distinguishing between sequence runs) */
  executionId?: string;
  /** Last run result (true = pass, false = fail, undefined = no run yet) */
  lastRunPassed?: boolean;

  /** Start time */
  startedAt?: Date;
  /** Elapsed time in seconds */
  elapsed: number;

  /** Hardware configuration */
  hardwareConfig: Record<string, Record<string, unknown>>;
  /** Auto-start enabled */
  autoStart: boolean;

  /** Process ID */
  pid?: number;
}

/**
 * Batch detailed information (for API responses).
 */
export interface BatchDetail extends Batch {
  /** Sequence parameters */
  parameters: Record<string, unknown>;
  /** Dynamic batch configuration (processId, headerId, etc.) */
  config: Record<string, unknown>;
  /** Hardware status by device ID */
  hardwareStatus: Record<string, HardwareStatus>;
  /** [Deprecated] Use config.processId instead */
  processId?: number;
  /** [Deprecated] Use config.headerId instead */
  headerId?: number;
  /** Current execution status */
  execution?: {
    status: ExecutionStatus;
    currentStep?: string;
    stepIndex: number;
    totalSteps: number;
    progress: number;
    startedAt?: Date;
    elapsed: number;
    steps: StepResult[];
  };
}

/**
 * Request body for starting a sequence.
 */
export interface SequenceStartRequest {
  parameters?: Record<string, unknown>;
  /** Pre-validated WIP integer ID (skip lookup in worker if provided) */
  wip_int_id?: number;
}

/**
 * Request body for manual hardware control.
 */
export interface ManualControlRequest {
  hardware: string;
  command: string;
  params?: Record<string, unknown>;
}

/**
 * Response for batch start operation.
 */
export interface BatchStartResponse {
  batchId: string;
  status: string;
  pid?: number;
}

/**
 * Response for batch stop operation.
 */
export interface BatchStopResponse {
  batchId: string;
  status: string;
}

/**
 * Response for sequence start operation.
 */
export interface SequenceStartResponse {
  batchId: string;
  executionId: string;
  status: string;
}

/**
 * Response for manual control operation.
 */
export interface ManualControlResponse {
  hardware: string;
  command: string;
  result: Record<string, unknown>;
}

/**
 * Request body for creating batch configuration.
 */
export interface CreateBatchRequest {
  /** Number of batches to create */
  quantity: number;
  /** Sequence name to use */
  sequenceName: string;
  /** Step order customization */
  stepOrder?: Array<{ name: string; displayName?: string; order: number; enabled: boolean }>;
  /** Parameter overrides */
  parameters?: Record<string, unknown>;
  /** MES Process ID (required when workflow.enabled) */
  processId?: number;
}

/**
 * Response for batch creation.
 */
export interface CreateBatchResponse {
  /** Created batch IDs */
  batchIds: string[];
  /** Sequence assigned */
  sequenceName: string;
  /** Created timestamp */
  createdAt: string;
}

/**
 * Request body for updating batch configuration.
 */
export interface UpdateBatchConfigRequest {
  /** Sequence name to deploy */
  sequenceName?: string;
  /** Step order customization */
  stepOrder?: Array<{ name: string; order: number; enabled: boolean }>;
  /** Parameter overrides */
  parameters?: Record<string, unknown>;
}

/**
 * Batch with extended statistics.
 */
export interface BatchWithStats extends Batch {
  /** Execution statistics */
  statistics: BatchStatistics;
  /** Step-level statistics */
  stepStatistics?: StepStatistics[];
}
