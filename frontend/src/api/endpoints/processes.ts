/**
 * Processes API Endpoints
 */

import apiClient from '../client';
import type { Process } from '@/types/api';

export interface ProcessCreate {
  process_number: number;
  process_code: string;
  process_name_ko: string;
  process_name_en: string;
  description?: string;
  sort_order: number;
  is_active?: boolean;
  estimated_duration_seconds?: number;
  quality_criteria?: Record<string, unknown>;
  auto_print_label?: boolean;
  label_template_type?: string;
  process_type?: string;
}

export interface ProcessUpdate {
  process_number?: number;
  process_code?: string;
  process_name_ko?: string;
  process_name_en?: string;
  description?: string;
  sort_order?: number;
  is_active?: boolean;
  estimated_duration_seconds?: number;
  quality_criteria?: Record<string, unknown>;
  auto_print_label?: boolean;
  label_template_type?: string;
  process_type?: string;
}

export const processesApi = {
  /**
   * Get all processes
   */
  getProcesses: async (params?: { is_active?: boolean }): Promise<Process[]> => {
    const response = await apiClient.get<Process[]>('/processes/', { params });
    return response.data;
  },

  /**
   * Get single process by ID
   */
  getProcess: async (processId: number): Promise<Process> => {
    const response = await apiClient.get<Process>(`/processes/${processId}`);
    return response.data;
  },

  /**
   * Create new process
   */
  createProcess: async (data: ProcessCreate): Promise<Process> => {
    const response = await apiClient.post<Process>('/processes/', data);
    return response.data;
  },

  /**
   * Update process
   */
  updateProcess: async (processId: number, data: ProcessUpdate): Promise<Process> => {
    const response = await apiClient.put<Process>(`/processes/${processId}`, data);
    return response.data;
  },

  /**
   * Delete process
   */
  deleteProcess: async (processId: number): Promise<void> => {
    await apiClient.delete(`/processes/${processId}`);
  },
};
