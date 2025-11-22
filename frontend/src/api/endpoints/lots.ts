/**
 * LOTs API Endpoints
 */

import apiClient from '../client';
import type { Lot, LotCreate, LotUpdate, LotStatus } from '@/types/api';

export const lotsApi = {
  /**
   * Get LOTs list with filters and pagination
   * Note: Backend returns array directly, not PaginatedResponse
   */
  getLots: async (params?: {
    skip?: number;
    limit?: number;
    status?: LotStatus;
    product_model_id?: number;
  }): Promise<Lot[]> => {
    const response = await apiClient.get<Lot[]>('/lots/', { params });
    return response.data;
  },

  /**
   * Get active LOTs (CREATED or IN_PROGRESS)
   */
  getActiveLots: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<Lot[]> => {
    const response = await apiClient.get<Lot[]>('/lots/active', { params });
    return response.data;
  },

  /**
   * Get single LOT by ID
   */
  getLot: async (lotId: number): Promise<Lot> => {
    const response = await apiClient.get<Lot>(`/lots/${lotId}`);
    return response.data;
  },

  /**
   * Get LOT by lot number
   */
  getLotByNumber: async (lotNumber: string): Promise<Lot> => {
    const response = await apiClient.get<Lot>(`/lots/number/${lotNumber}`);
    return response.data;
  },

  /**
   * Create new LOT
   */
  createLot: async (data: LotCreate): Promise<Lot> => {
    const response = await apiClient.post<Lot>('/lots/', data);
    return response.data;
  },

  /**
   * Update LOT
   */
  updateLot: async (lotId: number, data: LotUpdate): Promise<Lot> => {
    const response = await apiClient.put<Lot>(`/lots/${lotId}`, data);
    return response.data;
  },

  /**
   * Generate WIP IDs for LOT
   */
  startWipGeneration: async (lotId: number, quantity: number): Promise<any[]> => {
    const response = await apiClient.post<any[]>(`/lots/${lotId}/start-wip-generation`, null, {
      params: { quantity }
    });
    return response.data;
  },

  /**
   * Delete LOT
   */
  deleteLot: async (lotId: number): Promise<void> => {
    await apiClient.delete(`/lots/${lotId}`);
  },
};
