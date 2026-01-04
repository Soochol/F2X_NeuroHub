/**
 * WebSocket message type definitions.
 */

import type { BatchStatus } from './batch';
import type { LogLevel } from './log';
import type { StepResult } from './execution';

// ============================================================
// Client → Server Messages
// ============================================================

/**
 * Client message to subscribe to batch updates.
 */
export interface SubscribeMessage {
  type: 'subscribe';
  batchIds: string[];
}

/**
 * Client message to unsubscribe from batch updates.
 */
export interface UnsubscribeMessage {
  type: 'unsubscribe';
  batchIds: string[];
}

/**
 * Union type for all client messages.
 */
export type ClientMessage = SubscribeMessage | UnsubscribeMessage;

// ============================================================
// Server → Client Messages
// ============================================================

/**
 * Server message for batch status updates.
 */
export interface BatchStatusMessage {
  type: 'batch_status';
  batchId: string;
  data: {
    status: BatchStatus;
    currentStep?: string;
    stepIndex: number;
    progress: number;
    executionId?: string;
    /** Last run result (included in initial push after subscribe) */
    lastRunPassed?: boolean | null;
    /** Step results (included in initial push after subscribe) */
    steps?: StepResult[];
  };
}

/**
 * Server message when a step starts.
 */
export interface StepStartMessage {
  type: 'step_start';
  batchId: string;
  data: {
    step: string;
    index: number;
    total: number;
    executionId?: string;
    /** All step names from manifest (sent on first step only) */
    stepNames?: string[];
  };
}

/**
 * Server message when a step completes.
 */
export interface StepCompleteMessage {
  type: 'step_complete';
  batchId: string;
  data: {
    step: string;
    index: number;
    duration: number;
    pass: boolean;
    result?: Record<string, unknown>;
    executionId?: string;
  };
}

/**
 * Server message when a sequence completes.
 */
export interface SequenceCompleteMessage {
  type: 'sequence_complete';
  batchId: string;
  data: {
    executionId: string;
    overallPass: boolean;
    duration: number;
    steps: StepResult[];
  };
}

/**
 * Server message for log entries.
 */
export interface LogMessage {
  type: 'log';
  batchId: string;
  data: {
    level: LogLevel;
    message: string;
    timestamp: Date;
    /** Execution ID for correlating logs to specific runs */
    executionId?: string;
  };
}

/**
 * Server message for errors.
 */
export interface ErrorMessage {
  type: 'error';
  batchId: string;
  data: {
    code: string;
    message: string;
    step?: string;
    timestamp: Date;
    /** Execution ID for correlating errors to specific runs */
    executionId?: string;
  };
}

/**
 * Server acknowledgment for subscribe/unsubscribe.
 */
export interface SubscriptionAckMessage {
  type: 'subscribed' | 'unsubscribed';
  data: {
    batchIds: string[];
  };
}

/**
 * Server message when a batch is created.
 */
export interface BatchCreatedMessage {
  type: 'batch_created';
  batchId: string;
  data: {
    id: string;
    name: string;
    sequencePackage?: string;
  };
}

/**
 * Server message when a batch is deleted.
 */
export interface BatchDeletedMessage {
  type: 'batch_deleted';
  batchId: string;
  data: {
    id: string;
  };
}

/**
 * Union type for all server messages.
 */
export type ServerMessage =
  | BatchStatusMessage
  | StepStartMessage
  | StepCompleteMessage
  | SequenceCompleteMessage
  | LogMessage
  | ErrorMessage
  | SubscriptionAckMessage
  | BatchCreatedMessage
  | BatchDeletedMessage;
