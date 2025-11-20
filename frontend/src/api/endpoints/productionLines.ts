/**
 * Production Lines API Endpoints
 */

import apiClient from '../client';
import type { ProductionLine } from '@/types/api';

export interface ProductionLineCreate {
  line_code: string;
  line_name: string;
  description?: string;
  cycle_time_sec?: number;
  location?: string;
  is_active?: boolean;
}

export interface ProductionLineUpdate {
  line_code?: string;
  line_name?: string;
  description?: string;
  cycle_time_sec?: number;
  location?: string;
  is_active?: boolean;
}

export const productionLinesApi = {
  /**
   * Get all production lines
   */
  getProductionLines: async (params?: { skip?: number; limit?: number }): Promise<ProductionLine[]> => {
    const response = await apiClient.get<ProductionLine[]>('/production-lines/', { params });
    return response.data;
  },

  /**
   * Get active production lines
   */
  getActiveProductionLines: async (): Promise<ProductionLine[]> => {
    const response = await apiClient.get<ProductionLine[]>('/production-lines/active');
    return response.data;
  },

  /**
   * Get single production line by ID
   */
  getProductionLine: async (productionLineId: number): Promise<ProductionLine> => {
    const response = await apiClient.get<ProductionLine>(`/production-lines/${productionLineId}`);
    return response.data;
  },

  /**
   * Create new production line
   */
  createProductionLine: async (data: ProductionLineCreate): Promise<ProductionLine> => {
    const response = await apiClient.post<ProductionLine>('/production-lines/', data);
    return response.data;
  },

  /**
   * Update production line
   */
  updateProductionLine: async (productionLineId: number, data: ProductionLineUpdate): Promise<ProductionLine> => {
    const response = await apiClient.put<ProductionLine>(`/production-lines/${productionLineId}`, data);
    return response.data;
  },

  /**
   * Delete production line
   */
  deleteProductionLine: async (productionLineId: number): Promise<void> => {
    await apiClient.delete(`/production-lines/${productionLineId}`);
  },
};
