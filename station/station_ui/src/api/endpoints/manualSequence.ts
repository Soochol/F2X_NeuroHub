/**
 * Manual Sequence API endpoints.
 *
 * Provides API functions for manual step-by-step sequence execution
 * with real hardware, without requiring a Batch.
 */

import type { ApiResponse } from '../../types';
import apiClient, { extractData } from '../client';

// ============================================================================
// Types
// ============================================================================

export type ManualSessionStatus =
  | 'created'
  | 'connecting'
  | 'ready'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'aborted';

export type ManualStepStatus = 'pending' | 'running' | 'passed' | 'failed' | 'skipped';

export interface HardwareState {
  id: string;
  displayName: string;
  connected: boolean;
  driverClass?: string;
  config: Record<string, unknown>;
  commands: string[];
  error?: string;
}

export interface ManualStepState {
  name: string;
  displayName: string;
  order: number;
  skippable: boolean;
  status: ManualStepStatus;
  startedAt?: string;
  completedAt?: string;
  duration: number;
  result?: Record<string, unknown>;
  measurements: Record<string, unknown>;
  error?: string;
  parameterOverrides: string[];
}

export interface ManualSessionSummary {
  id: string;
  sequenceName: string;
  sequenceVersion: string;
  status: ManualSessionStatus;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  currentStepIndex: number;
  totalSteps: number;
  passedSteps: number;
  failedSteps: number;
  hardwareConnected: number;
  hardwareTotal: number;
  overallPass: boolean;
}

export interface ManualSessionDetail {
  id: string;
  sequenceName: string;
  sequenceVersion: string;
  status: ManualSessionStatus;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  currentStepIndex: number;
  steps: ManualStepState[];
  hardware: HardwareState[];
  parameters: Record<string, unknown>;
  hardwareConfig: Record<string, Record<string, unknown>>;
  overallPass: boolean;
  error?: string;
}

export interface CommandParameter {
  name: string;
  displayName: string;
  type: string;
  required: boolean;
  default?: unknown;
  min?: number;
  max?: number;
  unit?: string;
}

export interface CommandDefinition {
  name: string;
  displayName: string;
  description?: string;
  category?: string;
  parameters: CommandParameter[];
  returns?: {
    type: string;
    description?: string;
  };
}

export interface CommandResult {
  success: boolean;
  hardwareId: string;
  command: string;
  result?: unknown;
  error?: string;
  duration: number;
}

export interface CreateManualSessionRequest {
  sequence_name: string;
  hardware_config?: Record<string, Record<string, unknown>>;
  parameters?: Record<string, unknown>;
}

export interface ManualRunStepRequest {
  parameter_overrides?: Record<string, unknown>;
}

export interface ExecuteCommandRequest {
  command: string;
  parameters?: Record<string, unknown>;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Create a new manual test session.
 */
export async function createManualSession(
  sequenceName: string,
  hardwareConfig?: Record<string, Record<string, unknown>>,
  parameters?: Record<string, unknown>
): Promise<ManualSessionDetail> {
  const response = await apiClient.post<ApiResponse<ManualSessionDetail>>(
    '/manual-sequence/sessions',
    {
      sequence_name: sequenceName,
      hardware_config: hardwareConfig,
      parameters,
    }
  );
  return extractData(response);
}

/**
 * List all manual test sessions.
 */
export async function listManualSessions(): Promise<ManualSessionSummary[]> {
  const response = await apiClient.get<ApiResponse<ManualSessionSummary[]>>(
    '/manual-sequence/sessions'
  );
  return extractData(response);
}

/**
 * Get a manual test session by ID.
 */
export async function getManualSession(sessionId: string): Promise<ManualSessionDetail> {
  const response = await apiClient.get<ApiResponse<ManualSessionDetail>>(
    `/manual-sequence/sessions/${sessionId}`
  );
  return extractData(response);
}

/**
 * Delete a manual test session.
 */
export async function deleteManualSession(sessionId: string): Promise<boolean> {
  const response = await apiClient.delete<ApiResponse<boolean>>(
    `/manual-sequence/sessions/${sessionId}`
  );
  return extractData(response);
}

/**
 * Initialize a manual test session (connect hardware, run setup).
 */
export async function initializeManualSession(
  sessionId: string
): Promise<ManualSessionDetail> {
  const response = await apiClient.post<ApiResponse<ManualSessionDetail>>(
    `/manual-sequence/sessions/${sessionId}/initialize`
  );
  return extractData(response);
}

/**
 * Finalize a manual test session (run teardown, disconnect hardware).
 */
export async function finalizeManualSession(
  sessionId: string
): Promise<ManualSessionDetail> {
  const response = await apiClient.post<ApiResponse<ManualSessionDetail>>(
    `/manual-sequence/sessions/${sessionId}/finalize`
  );
  return extractData(response);
}

/**
 * Abort a manual test session (emergency stop).
 */
export async function abortManualSession(
  sessionId: string
): Promise<ManualSessionDetail> {
  const response = await apiClient.post<ApiResponse<ManualSessionDetail>>(
    `/manual-sequence/sessions/${sessionId}/abort`
  );
  return extractData(response);
}

/**
 * Run a step in the manual session.
 */
export async function runManualStep(
  sessionId: string,
  stepName: string,
  parameterOverrides?: Record<string, unknown>
): Promise<ManualStepState> {
  const response = await apiClient.post<ApiResponse<ManualStepState>>(
    `/manual-sequence/sessions/${sessionId}/steps/${stepName}/run`,
    parameterOverrides ? { parameter_overrides: parameterOverrides } : undefined
  );
  return extractData(response);
}

/**
 * Skip a step in the manual session.
 */
export async function skipManualStep(
  sessionId: string,
  stepName: string
): Promise<ManualStepState> {
  const response = await apiClient.post<ApiResponse<ManualStepState>>(
    `/manual-sequence/sessions/${sessionId}/steps/${stepName}/skip`
  );
  return extractData(response);
}

/**
 * Get connected hardware for a session.
 */
export async function getManualSessionHardware(
  sessionId: string
): Promise<HardwareState[]> {
  const response = await apiClient.get<ApiResponse<HardwareState[]>>(
    `/manual-sequence/sessions/${sessionId}/hardware`
  );
  return extractData(response);
}

/**
 * Get available commands for a hardware device.
 */
export async function getHardwareCommands(
  sessionId: string,
  hardwareId: string
): Promise<CommandDefinition[]> {
  const response = await apiClient.get<ApiResponse<CommandDefinition[]>>(
    `/manual-sequence/sessions/${sessionId}/hardware/${hardwareId}/commands`
  );
  return extractData(response);
}

/**
 * Execute a hardware command.
 */
export async function executeHardwareCommand(
  sessionId: string,
  hardwareId: string,
  command: string,
  parameters?: Record<string, unknown>
): Promise<CommandResult> {
  const response = await apiClient.post<ApiResponse<CommandResult>>(
    `/manual-sequence/sessions/${sessionId}/hardware/${hardwareId}/execute`,
    {
      command,
      parameters,
    }
  );
  return extractData(response);
}
