/**
 * Station Service Types for Frontend
 *
 * TypeScript types for Station Monitor functionality
 */

// ============================================================================
// Station Types
// ============================================================================

export interface Station {
  id: string;
  name: string;
  description?: string;
  host: string;
  port: number;
  status: StationConnectionStatus;
  health?: StationHealth;
  batches?: BatchSummary[];
  lastSeen?: string;
}

export type StationConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';

export interface StationHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  batchesRunning: number;
  backendStatus: 'connected' | 'disconnected';
  diskUsage: number;
  uptime: number;
  version: string;
}

// Raw API response (snake_case)
export interface StationSystemInfoRaw {
  station_id: string;
  station_name: string;
  description?: string;
  version: string;
  uptime: number;
  backend_connected: boolean;
}

// Transformed (camelCase)
export interface StationSystemInfo {
  stationId: string;
  stationName: string;
  description?: string;
  version: string;
  uptime: number;
  backendConnected: boolean;
}

// ============================================================================
// Batch Types
// ============================================================================

export type BatchStatus =
  | 'idle'
  | 'starting'
  | 'running'
  | 'stopping'
  | 'completed'
  | 'error';

export interface BatchSummary {
  id: string;
  name: string;
  status: BatchStatus;
  sequenceName: string;
  sequenceVersion: string;
  currentStep?: string;
  stepIndex: number;
  totalSteps: number;
  progress: number;
  startedAt?: string;
  elapsed: number;
  lastRunPassed?: boolean;
}

export interface BatchDetail extends BatchSummary {
  sequence: BatchSequenceInfo;
  parameters: Record<string, unknown>;
  hardware: Record<string, unknown>;
  execution: BatchExecution;
}

export interface BatchSequenceInfo {
  name: string;
  version: string;
  packagePath: string;
}

export interface BatchExecution {
  status: BatchStatus;
  currentStep?: string;
  stepIndex: number;
  totalSteps: number;
  progress: number;
  startedAt?: string;
  elapsed: number;
  steps: BatchStepResult[];
}

export interface BatchStepResult {
  name: string;
  index: number;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'skipped';
  duration?: number;
  result?: Record<string, unknown>;
  error?: string;
}

export interface BatchStatistics {
  total: number;
  pass: number;
  fail: number;
  passRate: number;
}

// ============================================================================
// WebSocket Message Types
// ============================================================================

export type StationWebSocketMessageType =
  | 'batch_status'
  | 'step_start'
  | 'step_complete'
  | 'sequence_complete'
  | 'log'
  | 'error'
  | 'subscribed'
  | 'unsubscribed'
  | 'batch_created'
  | 'batch_deleted';

export interface StationWebSocketMessage {
  type: StationWebSocketMessageType;
  batch_id?: string;
  data?: Record<string, unknown>;
  timestamp?: string;
}

export interface BatchStatusMessage {
  type: 'batch_status';
  batch_id: string;
  status: BatchStatus;
  current_step?: string;
  step_index: number;
  progress: number;
}

export interface StepStartMessage {
  type: 'step_start';
  batch_id: string;
  step: string;
  index: number;
  total: number;
}

export interface StepCompleteMessage {
  type: 'step_complete';
  batch_id: string;
  step: string;
  index: number;
  duration: number;
  pass: boolean;
  result?: Record<string, unknown>;
}

export interface SequenceCompleteMessage {
  type: 'sequence_complete';
  batch_id: string;
  execution_id: string;
  overall_pass: boolean;
  duration: number;
  steps?: BatchStepResult[];
}

export interface LogMessage {
  type: 'log';
  batch_id: string;
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

export interface ErrorMessage {
  type: 'error';
  batch_id?: string;
  code: string;
  message: string;
  step?: string;
  timestamp: string;
}

export interface BatchCreatedMessage {
  type: 'batch_created';
  batch_id: string;
  data: {
    id: string;
    name: string;
    sequence_package?: string;
  };
}

export interface BatchDeletedMessage {
  type: 'batch_deleted';
  batch_id: string;
  data: {
    id: string;
  };
}

// ============================================================================
// API Response Types
// ============================================================================

export interface StationApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// ============================================================================
// Station Configuration (for managing multiple stations)
// ============================================================================

export interface StationConfig {
  id: string;
  name: string;
  host: string;
  port: number;
  description?: string;
  enabled: boolean;
}

// Default stations configuration (can be overridden by backend config)
export const DEFAULT_STATIONS: StationConfig[] = [
  {
    id: 'station-1',
    name: 'Station 1',
    host: 'localhost',
    port: 8080,
    description: 'Primary test station',
    enabled: true,
  },
  {
    id: 'station-2',
    name: 'Station 2',
    host: 'localhost',
    port: 8081,
    description: 'Secondary test station',
    enabled: true,
  },
];
