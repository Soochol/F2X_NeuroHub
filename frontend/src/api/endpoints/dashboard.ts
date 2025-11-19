/**
 * Dashboard API Endpoints
 */

import apiClient from '../client';
import type { DashboardSummary, DashboardLot, ProcessWIP, LotStatus } from '@/types/api';

export const dashboardApi = {
  /**
   * Get dashboard summary with KPIs
   */
  getSummary: async (targetDate?: string): Promise<DashboardSummary> => {
    const params = targetDate ? { target_date: targetDate } : {};
    const response = await apiClient.get<DashboardSummary>('/dashboard/summary', { params });
    return response.data;
  },

  /**
   * Get LOTs list for dashboard
   */
  getLots: async (status?: LotStatus, limit = 20): Promise<{ lots: DashboardLot[]; total: number }> => {
    const params: Record<string, any> = { limit };
    if (status) {
      params.status = status;
    }
    const response = await apiClient.get<{ lots: DashboardLot[]; total: number }>('/dashboard/lots', { params });
    return response.data;
  },

  /**
   * Get work-in-progress by process
   */
  getProcessWIP: async (): Promise<{ processes: ProcessWIP[]; total_wip: number; bottleneck_process?: string }> => {
    const response = await apiClient.get<{ processes: ProcessWIP[]; total_wip: number; bottleneck_process?: string }>('/dashboard/process-wip');
    return response.data;
  },
};
