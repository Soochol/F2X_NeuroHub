/**
 * Process Data API Endpoints
 */

import apiClient from '../client';
import type { ProcessData, ProcessDataCreate, ProcessResult, DataLevel } from '@/types/api';

export const processDataApi = {
  /**
   * Get process data list with filters and pagination
   */
  getProcessDataList: async (params?: {
    skip?: number;
    limit?: number;
    serial_id?: number;
    process_id?: number;
    result?: ProcessResult;
  }): Promise<ProcessData[]> => {
    const response = await apiClient.get<ProcessData[]>('/process-data/', { params });
    return response.data;
  },

  /**
   * Get single process data by ID
   */
  getProcessData: async (processDataId: number): Promise<ProcessData> => {
    const response = await apiClient.get<ProcessData>(`/process-data/${processDataId}`);
    return response.data;
  },

  /**
   * Create new process data record
   */
  createProcessData: async (data: ProcessDataCreate): Promise<ProcessData> => {
    const response = await apiClient.post<ProcessData>('/process-data/', data);
    return response.data;
  },

  /**
   * Get process data for a specific serial
   */
  getProcessDataBySerial: async (serialId: number): Promise<ProcessData[]> => {
    const response = await apiClient.get<ProcessData[]>(`/process-data/serial/${serialId}`);
    return response.data;
  },

  /**
   * Start a process for a serial
   */
  startProcess: async (data: {
    serial_id: number;
    process_id: number;
    worker_id: number;
  }): Promise<{ message: string; process_data_id: number }> => {
    const response = await apiClient.post('/process-data/start', data);
    return response.data;
  },

  /**
   * Complete a process for a serial
   */
  completeProcess: async (processDataId: number, data: {
    result: ProcessResult;
    data_level: DataLevel;
    measurements?: Record<string, any>;
    defect_codes?: string[];
    notes?: string;
  }): Promise<ProcessData> => {
    const response = await apiClient.post<ProcessData>(`/process-data/${processDataId}/complete`, data);
    return response.data;
  },
};
