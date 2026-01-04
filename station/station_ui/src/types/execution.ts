/**
 * Execution type definitions.
 */

/**
 * Execution status.
 */
export type ExecutionStatus = 'running' | 'completed' | 'failed' | 'stopped';

/**
 * Step execution status.
 */
export type StepStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

/**
 * Result of a single step execution.
 */
export interface StepResult {
  /** Step name */
  name: string;
  /** Step order (1-based) */
  order: number;
  /** Step status */
  status: StepStatus;
  /** Whether step passed */
  pass: boolean;
  /** Duration in seconds */
  duration?: number;
  /** Start time */
  startedAt?: Date;
  /** Completion time */
  completedAt?: Date;
  /** Step result data */
  result?: Record<string, unknown>;
  /** Error message if failed */
  error?: string;
}

/**
 * Complete execution result.
 */
export interface ExecutionResult {
  /** Execution ID (e.g., "exec_20250120_123456") */
  id: string;
  /** Batch ID */
  batchId: string;
  /** Sequence name */
  sequenceName: string;
  /** Sequence version */
  sequenceVersion: string;
  /** Execution status */
  status: ExecutionStatus;
  /** Overall pass/fail */
  overallPass: boolean;

  /** Start time */
  startedAt: Date;
  /** Completion time */
  completedAt?: Date;
  /** Duration in seconds */
  duration?: number;

  /** Sequence parameters used */
  parameters: Record<string, unknown>;
  /** Step results */
  steps: StepResult[];

  /** Backend sync time */
  syncedAt?: Date;
}

/**
 * Execution summary for list views.
 */
export interface ExecutionSummary {
  /** Execution ID */
  id: string;
  /** Batch ID */
  batchId: string;
  /** Sequence name */
  sequenceName: string;
  /** Sequence version */
  sequenceVersion: string;
  /** Execution status */
  status: ExecutionStatus;
  /** Overall pass/fail */
  overallPass: boolean;
  /** Start time */
  startedAt: Date;
  /** Completion time */
  completedAt?: Date;
  /** Duration in seconds */
  duration?: number;
  /** Whether synced to backend */
  synced: boolean;
}
