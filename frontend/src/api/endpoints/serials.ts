/**
 * Serials API Endpoints
 */

import apiClient from '../client';
import type { Serial, SerialCreate, SerialUpdate, SerialTrace, SerialStatus, PaginatedResponse } from '@/types/api';

export const serialsApi = {
  /**
   * Get serials list with filters and pagination
   */
  getSerials: async (params?: {
    skip?: number;
    limit?: number;
    lot_id?: number;
    status?: SerialStatus;
  }): Promise<PaginatedResponse<Serial>> => {
    const response = await apiClient.get<PaginatedResponse<Serial>>('/serials/', { params });
    return response.data;
  },

  /**
   * Get single serial by ID
   */
  getSerial: async (serialId: number): Promise<Serial> => {
    const response = await apiClient.get<Serial>(`/serials/${serialId}`);
    return response.data;
  },

  /**
   * Get serial by serial number
   */
  getSerialByNumber: async (serialNumber: string): Promise<Serial> => {
    const response = await apiClient.get<Serial>(`/serials/number/${serialNumber}`);
    return response.data;
  },

  /**
   * Create new serial
   */
  createSerial: async (data: SerialCreate, printLabel: boolean = false): Promise<Serial> => {
    const query = printLabel ? '?print_label=true' : '';
    const response = await apiClient.post<Serial>(`/serials/${query}`, data);
    return response.data;
  },

  /**
   * Update serial
   */
  updateSerial: async (serialId: number, data: SerialUpdate): Promise<Serial> => {
    const response = await apiClient.put<Serial>(`/serials/${serialId}`, data);
    return response.data;
  },

  /**
   * Delete serial
   */
  deleteSerial: async (serialId: number): Promise<void> => {
    await apiClient.delete(`/serials/${serialId}`);
  },

  /**
   * Get complete traceability for serial
   */
  getTrace: async (serialNumber: string): Promise<SerialTrace> => {
    const response = await apiClient.get<SerialTrace>(`/serials/${serialNumber}/trace`);
    return response.data;
  },

  /**
   * Update serial status
   */
  updateSerialStatus: async (serialId: number, data: { status: SerialStatus; failure_reason?: string }): Promise<Serial> => {
    const response = await apiClient.put<Serial>(`/serials/${serialId}/status`, data);
    return response.data;
  },

  /**
   * Start rework for a FAILED serial
   */
  startRework: async (serialId: number): Promise<Serial> => {
    const response = await apiClient.post<Serial>(`/serials/${serialId}/rework`);
    return response.data;
  },

  /**
   * Check if serial can be reworked
   */
  canRework: async (serialId: number): Promise<{ can_rework: boolean; reason: string; rework_count: number; status: string }> => {
    const response = await apiClient.get(`/serials/${serialId}/can-rework`);
    return response.data;
  },

  /**
   * Get serials by LOT ID
   */
  getSerialsByLot: async (lotId: number, params?: { skip?: number; limit?: number }): Promise<Serial[]> => {
    const response = await apiClient.get<Serial[]>(`/serials/lot/${lotId}`, { params });
    return response.data;
  },

  /**
   * Get failed serials available for rework
   */
  getFailedSerials: async (params?: { skip?: number; limit?: number }): Promise<Serial[]> => {
    const response = await apiClient.get<Serial[]>('/serials/failed', { params });
    return response.data;
  },

  /**
   * Generate serial from WIP ID
   */
  generateFromWip: async (wipId: string, printLabel: boolean = true): Promise<Serial> => {
    const response = await apiClient.post<Serial>(`/serials/generate-from-wip?wip_id=${wipId}&print_label=${printLabel}`);
    return response.data;
  },
};
