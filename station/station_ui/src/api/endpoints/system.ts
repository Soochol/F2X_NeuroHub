/**
 * System API endpoints.
 */

import type { ApiResponse, SystemInfo, HealthStatus } from '../../types';
import apiClient, { extractData } from '../client';

/**
 * Get system information.
 */
export async function getSystemInfo(): Promise<SystemInfo> {
  const response = await apiClient.get<ApiResponse<SystemInfo>>('/system/info');
  return extractData(response);
}

/**
 * Get system health status.
 */
export async function getHealthStatus(): Promise<HealthStatus> {
  const response = await apiClient.get<ApiResponse<HealthStatus>>('/system/health');
  return extractData(response);
}

/**
 * Update station information request payload.
 */
export interface UpdateStationInfoRequest {
  id: string;
  name: string;
  description: string;
}

/**
 * Update station information.
 */
export async function updateStationInfo(data: UpdateStationInfoRequest): Promise<SystemInfo> {
  const response = await apiClient.put<ApiResponse<SystemInfo>>('/system/station-info', data);
  return extractData(response);
}

/**
 * Workflow configuration response.
 */
export interface WorkflowConfig {
  enabled: boolean;
  input_mode: 'popup' | 'barcode';
  auto_sequence_start: boolean;
  require_operator_login: boolean;
}

/**
 * Get workflow configuration.
 */
export async function getWorkflowConfig(): Promise<WorkflowConfig> {
  const response = await apiClient.get<ApiResponse<WorkflowConfig>>('/system/workflow');
  return extractData(response);
}

/**
 * Update workflow configuration request payload.
 */
export interface UpdateWorkflowRequest {
  enabled?: boolean;
  input_mode?: 'popup' | 'barcode';
  auto_sequence_start?: boolean;
  require_operator_login?: boolean;
}

/**
 * Update workflow configuration.
 */
export async function updateWorkflowConfig(data: UpdateWorkflowRequest): Promise<WorkflowConfig> {
  const response = await apiClient.put<ApiResponse<WorkflowConfig>>('/system/workflow', data);
  return extractData(response);
}

// ============================================================================
// Operator Session
// ============================================================================

/**
 * Operator information.
 */
export interface OperatorInfo {
  id: number;
  username: string;
  name: string;
  role: string;
}

/**
 * Operator session state.
 * Note: Keys are camelCase after API response transformation.
 */
export interface OperatorSession {
  loggedIn: boolean;
  operator: OperatorInfo | null;
  accessToken: string | null;
  loggedInAt: string | null;
}

/**
 * Get current operator session.
 */
export async function getOperatorSession(): Promise<OperatorSession> {
  const response = await apiClient.get<ApiResponse<OperatorSession>>('/system/operator');
  return extractData(response);
}

/**
 * Operator login request.
 */
export interface OperatorLoginRequest {
  username: string;
  password: string;
}

/**
 * Login operator.
 */
export async function operatorLogin(data: OperatorLoginRequest): Promise<OperatorSession> {
  const response = await apiClient.post<ApiResponse<OperatorSession>>('/system/operator-login', data);
  return extractData(response);
}

/**
 * Logout operator.
 */
export async function operatorLogout(): Promise<OperatorSession> {
  const response = await apiClient.post<ApiResponse<OperatorSession>>('/system/operator-logout');
  return extractData(response);
}

// ============================================================================
// Process List (공정 목록)
// ============================================================================

/**
 * Process information from backend MES.
 */
export interface ProcessInfo {
  id: number;
  processNumber: number;
  processCode: string;
  processNameKo: string;
  processNameEn: string;
}

/**
 * Get list of active processes from backend MES.
 */
export async function getProcesses(): Promise<ProcessInfo[]> {
  const response = await apiClient.get<ApiResponse<ProcessInfo[]>>('/system/processes');
  return extractData(response);
}

// ============================================================================
// Process Headers (Process Header 목록)
// ============================================================================

/**
 * Process header information from backend MES.
 */
export interface ProcessHeaderInfo {
  id: number;
  stationId: string;
  batchId: string;
  processId: number;
  status: 'OPEN' | 'CLOSED' | 'CANCELLED';
  totalCount: number;
  passCount: number;
  failCount: number;
  openedAt: string;
  closedAt: string | null;
  processName: string | null;
  processCode: string | null;
}

/**
 * Get list of process headers from backend MES.
 * @param stationId Optional filter by station ID
 * @param batchId Optional filter by batch ID
 * @param processId Optional filter by process ID
 * @param status Optional filter by status (OPEN, CLOSED, CANCELLED)
 * @param limit Maximum records to return (default 100)
 */
export async function getProcessHeaders(params?: {
  stationId?: string;
  batchId?: string;
  processId?: number;
  status?: string;
  limit?: number;
}): Promise<ProcessHeaderInfo[]> {
  const queryParams = new URLSearchParams();
  if (params?.stationId) queryParams.set('station_id', params.stationId);
  if (params?.batchId) queryParams.set('batch_id', params.batchId);
  if (params?.processId) queryParams.set('process_id', String(params.processId));
  if (params?.status) queryParams.set('header_status', params.status);
  if (params?.limit) queryParams.set('limit', String(params.limit));

  const url = `/system/headers${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  const response = await apiClient.get<ApiResponse<ProcessHeaderInfo[]>>(url);
  return extractData(response);
}

// ============================================================================
// WIP Validation
// ============================================================================

/**
 * WIP validation response.
 */
export interface ValidateWIPResponse {
  valid: boolean;
  wipId: string;
  intId?: number;
  lotId?: string;
  status?: string;
  message?: string;
  /** True if WIP already has PASS result for the requested process */
  hasPassForProcess?: boolean;
  /** Warning message if hasPassForProcess is true */
  passWarningMessage?: string;
}

/**
 * Validate WIP ID before starting a batch.
 * This performs a quick check against the backend to verify the WIP exists.
 *
 * @param wipId WIP ID to validate
 * @param processId Optional process ID for validation
 * @returns Validation result
 */
export async function validateWip(
  wipId: string,
  processId?: number
): Promise<ValidateWIPResponse> {
  const response = await apiClient.post<ApiResponse<ValidateWIPResponse>>(
    '/system/validate-wip',
    { wip_id: wipId, process_id: processId }
  );
  return extractData(response);
}

// ============================================================================
// Backend Configuration
// ============================================================================

/**
 * Backend configuration response.
 */
export interface BackendConfig {
  url: string;
  apiKeyMasked: string;
  syncInterval: number;
  stationId: string;
  timeout: number;
  maxRetries: number;
}

/**
 * Update backend configuration request payload.
 */
export interface UpdateBackendConfigRequest {
  url?: string;
  syncInterval?: number;
  stationId?: string;
  timeout?: number;
  maxRetries?: number;
}

/**
 * Get backend configuration.
 */
export async function getBackendConfig(): Promise<BackendConfig> {
  const response = await apiClient.get<ApiResponse<BackendConfig>>('/system/backend-config');
  return extractData(response);
}

/**
 * Update backend configuration.
 */
export async function updateBackendConfig(data: UpdateBackendConfigRequest): Promise<BackendConfig> {
  // Convert camelCase to snake_case for API
  const snakeCaseData: Record<string, unknown> = {};
  if (data.url !== undefined) snakeCaseData.url = data.url;
  if (data.syncInterval !== undefined) snakeCaseData.sync_interval = data.syncInterval;
  if (data.stationId !== undefined) snakeCaseData.station_id = data.stationId;
  if (data.timeout !== undefined) snakeCaseData.timeout = data.timeout;
  if (data.maxRetries !== undefined) snakeCaseData.max_retries = data.maxRetries;

  const response = await apiClient.put<ApiResponse<BackendConfig>>('/system/backend-config', snakeCaseData);
  return extractData(response);
}
