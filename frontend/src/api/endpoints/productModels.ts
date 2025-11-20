/**
 * Product Models API Endpoints
 */

import apiClient from '../client';
import type { ProductModel } from '@/types/api';

export interface ProductModelCreate {
  model_code: string;
  model_name: string;
  category?: string;
  production_cycle_days?: number;
  specifications?: Record<string, unknown>;
  status?: 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED';
}

export interface ProductModelUpdate {
  model_code?: string;
  model_name?: string;
  category?: string;
  production_cycle_days?: number;
  specifications?: Record<string, unknown>;
  status?: 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED';
}

export const productModelsApi = {
  /**
   * Get all product models
   */
  getProductModels: async (params?: { is_active?: boolean }): Promise<ProductModel[]> => {
    const response = await apiClient.get<ProductModel[]>('/product-models/', { params });
    return response.data;
  },

  /**
   * Get single product model by ID
   */
  getProductModel: async (productModelId: number): Promise<ProductModel> => {
    const response = await apiClient.get<ProductModel>(`/product-models/${productModelId}`);
    return response.data;
  },

  /**
   * Create new product model
   */
  createProductModel: async (data: ProductModelCreate): Promise<ProductModel> => {
    const response = await apiClient.post<ProductModel>('/product-models/', data);
    return response.data;
  },

  /**
   * Update product model
   */
  updateProductModel: async (productModelId: number, data: ProductModelUpdate): Promise<ProductModel> => {
    const response = await apiClient.put<ProductModel>(`/product-models/${productModelId}`, data);
    return response.data;
  },

  /**
   * Delete product model
   */
  deleteProductModel: async (productModelId: number): Promise<void> => {
    await apiClient.delete(`/product-models/${productModelId}`);
  },
};
