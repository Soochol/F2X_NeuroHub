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
