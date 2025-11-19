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
  createSerial: async (data: SerialCreate): Promise<Serial> => {
    const response = await apiClient.post<Serial>('/serials/', data);
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
};
