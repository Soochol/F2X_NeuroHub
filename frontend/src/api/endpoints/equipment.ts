/**
 * Equipment API Endpoints
 */

import apiClient from '../client';
import type { Equipment } from '@/types/api';

export interface EquipmentCreate {
  equipment_code: string;
  equipment_name: string;
  equipment_type: string;
  description?: string;
  process_id?: number;
  production_line_id?: number;
  manufacturer?: string;
  model_number?: string;
  serial_number?: string;
  status?: string;
  is_active?: boolean;
  last_maintenance_date?: string;
  next_maintenance_date?: string;
  total_operation_hours?: number;
  specifications?: Record<string, unknown>;
  maintenance_schedule?: Record<string, unknown>;
}

export interface EquipmentUpdate {
  equipment_code?: string;
  equipment_name?: string;
  equipment_type?: string;
  description?: string;
  process_id?: number;
  production_line_id?: number;
  manufacturer?: string;
  model_number?: string;
  serial_number?: string;
  status?: string;
  is_active?: boolean;
  last_maintenance_date?: string;
  next_maintenance_date?: string;
  total_operation_hours?: number;
  specifications?: Record<string, unknown>;
  maintenance_schedule?: Record<string, unknown>;
}

export const equipmentApi = {
  /**
   * Get all equipment
   */
  getEquipment: async (params?: { skip?: number; limit?: number }): Promise<Equipment[]> => {
    const response = await apiClient.get<Equipment[]>('/equipment/', { params });
    return response.data;
  },

  /**
   * Get active equipment
   */
  getActiveEquipment: async (): Promise<Equipment[]> => {
    const response = await apiClient.get<Equipment[]>('/equipment/active');
    return response.data;
  },

  /**
   * Get single equipment by ID
   */
  getEquipmentById: async (equipmentId: number): Promise<Equipment> => {
    const response = await apiClient.get<Equipment>(`/equipment/${equipmentId}`);
    return response.data;
  },

  /**
   * Get equipment by production line
   */
  getEquipmentByLine: async (productionLineId: number): Promise<Equipment[]> => {
    const response = await apiClient.get<Equipment[]>(`/equipment/production-line/${productionLineId}`);
    return response.data;
  },

  /**
   * Get equipment by process
   */
  getEquipmentByProcess: async (processId: number): Promise<Equipment[]> => {
    const response = await apiClient.get<Equipment[]>(`/equipment/process/${processId}`);
    return response.data;
  },

  /**
   * Create new equipment
   */
  createEquipment: async (data: EquipmentCreate): Promise<Equipment> => {
    const response = await apiClient.post<Equipment>('/equipment/', data);
    return response.data;
  },

  /**
   * Update equipment
   */
  updateEquipment: async (equipmentId: number, data: EquipmentUpdate): Promise<Equipment> => {
    const response = await apiClient.put<Equipment>(`/equipment/${equipmentId}`, data);
    return response.data;
  },

  /**
   * Delete equipment
   */
  deleteEquipment: async (equipmentId: number): Promise<void> => {
    await apiClient.delete(`/equipment/${equipmentId}`);
  },
};
