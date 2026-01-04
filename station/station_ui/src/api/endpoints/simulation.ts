/**
 * Interactive Simulation API endpoints.
 */

import type { ApiResponse } from '../../types';
import apiClient, { extractData } from '../client';

// ============================================================================
// Types
// ============================================================================

export interface SimulationStepState {
  name: string;
  displayName: string;
  order: number;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'skipped';
  startedAt?: string;
  completedAt?: string;
  duration: number;
  result?: Record<string, unknown>;
  measurements: Record<string, unknown>;
  error?: string;
}

export interface SimulationSessionSummary {
  id: string;
  sequenceName: string;
  sequenceVersion: string;
  status: string;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  currentStepIndex: number;
  totalSteps: number;
  passedSteps: number;
  failedSteps: number;
  overallPass: boolean;
}

export interface SimulationSessionDetail {
  id: string;
  sequenceName: string;
  sequenceVersion: string;
  status: 'created' | 'ready' | 'running' | 'paused' | 'completed' | 'failed' | 'aborted';
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  currentStepIndex: number;
  steps: SimulationStepState[];
  parameters: Record<string, unknown>;
  overallPass: boolean;
  error?: string;
}

export interface CreateSessionRequest {
  sequence_name: string;
  parameters?: Record<string, unknown>;
  hardware_config?: Record<string, unknown>;
}

export interface RunStepRequest {
  parameter_overrides?: Record<string, unknown>;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Create a new simulation session.
 */
export async function createSimulationSession(
  sequenceName: string,
  parameters?: Record<string, unknown>,
  hardwareConfig?: Record<string, unknown>
): Promise<SimulationSessionDetail> {
  const response = await apiClient.post<ApiResponse<SimulationSessionDetail>>(
    '/simulation/sessions',
    {
      sequence_name: sequenceName,
      parameters,
      hardware_config: hardwareConfig,
    }
  );
  return extractData(response);
}

/**
 * List all simulation sessions.
 */
export async function listSimulationSessions(): Promise<SimulationSessionSummary[]> {
  const response = await apiClient.get<ApiResponse<SimulationSessionSummary[]>>(
    '/simulation/sessions'
  );
  return extractData(response);
}

/**
 * Get a simulation session by ID.
 */
export async function getSimulationSession(
  sessionId: string
): Promise<SimulationSessionDetail> {
  const response = await apiClient.get<ApiResponse<SimulationSessionDetail>>(
    `/simulation/sessions/${sessionId}`
  );
  return extractData(response);
}

/**
 * Delete a simulation session.
 */
export async function deleteSimulationSession(sessionId: string): Promise<boolean> {
  const response = await apiClient.delete<ApiResponse<boolean>>(
    `/simulation/sessions/${sessionId}`
  );
  return extractData(response);
}

/**
 * Initialize a simulation session (run setup).
 */
export async function initializeSimulationSession(
  sessionId: string
): Promise<SimulationSessionDetail> {
  const response = await apiClient.post<ApiResponse<SimulationSessionDetail>>(
    `/simulation/sessions/${sessionId}/initialize`
  );
  return extractData(response);
}

/**
 * Finalize a simulation session (run teardown).
 */
export async function finalizeSimulationSession(
  sessionId: string
): Promise<SimulationSessionDetail> {
  const response = await apiClient.post<ApiResponse<SimulationSessionDetail>>(
    `/simulation/sessions/${sessionId}/finalize`
  );
  return extractData(response);
}

/**
 * Abort a simulation session.
 */
export async function abortSimulationSession(
  sessionId: string
): Promise<SimulationSessionDetail> {
  const response = await apiClient.post<ApiResponse<SimulationSessionDetail>>(
    `/simulation/sessions/${sessionId}/abort`
  );
  return extractData(response);
}

/**
 * Run a step in the simulation.
 */
export async function runSimulationStep(
  sessionId: string,
  stepName: string,
  parameterOverrides?: Record<string, unknown>
): Promise<SimulationStepState> {
  const response = await apiClient.post<ApiResponse<SimulationStepState>>(
    `/simulation/sessions/${sessionId}/steps/${stepName}/run`,
    parameterOverrides ? { parameter_overrides: parameterOverrides } : undefined
  );
  return extractData(response);
}

/**
 * Skip a step in the simulation.
 */
export async function skipSimulationStep(
  sessionId: string,
  stepName: string
): Promise<SimulationStepState> {
  const response = await apiClient.post<ApiResponse<SimulationStepState>>(
    `/simulation/sessions/${sessionId}/steps/${stepName}/skip`
  );
  return extractData(response);
}

/**
 * Run a quick (all-in-one) simulation.
 */
export async function runQuickSimulation(
  sequenceName: string,
  parameters?: Record<string, unknown>,
  hardwareConfig?: Record<string, unknown>
): Promise<SimulationSessionDetail> {
  const response = await apiClient.post<ApiResponse<SimulationSessionDetail>>(
    `/simulation/quick/${sequenceName}`,
    {
      sequence_name: sequenceName,
      parameters,
      hardware_config: hardwareConfig,
    }
  );
  return extractData(response);
}
