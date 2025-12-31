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
