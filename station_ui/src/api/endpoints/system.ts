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
