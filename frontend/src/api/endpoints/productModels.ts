/**
 * Product Models API Endpoints
 */

import apiClient from '../client';
import type { ProductModel } from '@/types/api';

export interface ProductModelCreate {
  code: string;
  name: string;
  description?: string;
  version: string;
  is_active?: boolean;
}

export interface ProductModelUpdate {
  code?: string;
  name?: string;
  description?: string;
  version?: string;
  is_active?: boolean;
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
