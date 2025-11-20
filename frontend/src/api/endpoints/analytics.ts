/**
 * Analytics API Endpoints
 */

import apiClient from '../client';
import type {
  ProductionStats,
  QualityMetrics,
  DefectAnalysis,
  DefectTrendsResponse,
  CycleTimeAnalysis,
} from '@/types/api';

export const analyticsApi = {
  /**
   * Get production statistics
   */
  getProductionStats: async (startDate?: string, endDate?: string): Promise<ProductionStats> => {
    const params: Record<string, any> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await apiClient.get<ProductionStats>('/analytics/production-stats', { params });
    return response.data;
  },

  /**
   * Get quality metrics
   */
  getQualityMetrics: async (startDate?: string, endDate?: string): Promise<QualityMetrics> => {
    const params: Record<string, any> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await apiClient.get<QualityMetrics>('/analytics/quality-metrics', { params });
    return response.data;
  },

  /**
   * Get defect analysis
   */
  getDefects: async (startDate?: string, endDate?: string): Promise<DefectAnalysis> => {
    const params: Record<string, any> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await apiClient.get<DefectAnalysis>('/analytics/defects', { params });
    return response.data;
  },

  /**
   * Get defect trends over time
   */
  getDefectTrends: async (period = 'daily', days = 30): Promise<DefectTrendsResponse> => {
    const params = { period, days };
    const response = await apiClient.get<DefectTrendsResponse>('/analytics/defect-trends', { params });
    return response.data;
  },

  /**
   * Get cycle time analysis
   */
  getCycleTime: async (processId?: number, startDate?: string, endDate?: string): Promise<CycleTimeAnalysis> => {
    const params: Record<string, any> = {};
    if (processId) params.process_id = processId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await apiClient.get<CycleTimeAnalysis>('/analytics/cycle-time', { params });
    return response.data;
  },
};
