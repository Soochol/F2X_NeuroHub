/**
 * Log type definitions.
 */

/**
 * Log severity levels.
 */
export type LogLevel = 'debug' | 'info' | 'warning' | 'error';

/**
 * Log entry record.
 */
export interface LogEntry {
  /** Log ID */
  id: number;
  /** Batch ID */
  batchId: string;
  /** Execution ID (if associated with an execution) */
  executionId?: string;
  /** Log level */
  level: LogLevel;
  /** Log message */
  message: string;
  /** Timestamp */
  timestamp: Date;
}
