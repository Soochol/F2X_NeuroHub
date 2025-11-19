/**
 * Alerts API Endpoints
 */

import apiClient from '../client';
import type {
  Alert,
  AlertListResponse,
  AlertCreate,
  AlertUpdate,
  AlertType,
  AlertSeverity,
  AlertStatus,
} from '@/types/api';

export const alertsApi = {
  /**
   * Get alerts list with filters and pagination
   */
  getAlerts: async (params?: {
    skip?: number;
    limit?: number;
    status?: AlertStatus;
    severity?: AlertSeverity;
    alert_type?: AlertType;
  }): Promise<AlertListResponse> => {
    const response = await apiClient.get<AlertListResponse>('/alerts/', { params });
    return response.data;
  },

  /**
   * Get unread alerts count
   */
  getUnreadCount: async (): Promise<number> => {
    const response = await apiClient.get<{ count: number }>('/alerts/unread/count');
    return response.data.count;
  },

  /**
   * Get single alert by ID
   */
  getAlert: async (alertId: number): Promise<Alert> => {
    const response = await apiClient.get<Alert>(`/alerts/${alertId}`);
    return response.data;
  },

  /**
   * Create new alert
   */
  createAlert: async (data: AlertCreate): Promise<Alert> => {
    const response = await apiClient.post<Alert>('/alerts/', data);
    return response.data;
  },

  /**
   * Update alert
   */
  updateAlert: async (alertId: number, data: AlertUpdate): Promise<Alert> => {
    const response = await apiClient.put<Alert>(`/alerts/${alertId}`, data);
    return response.data;
  },

  /**
   * Mark single alert as read
   */
  markAsRead: async (alertId: number): Promise<Alert> => {
    const response = await apiClient.put<Alert>(`/alerts/${alertId}/read`);
    return response.data;
  },

  /**
   * Bulk mark alerts as read
   */
  bulkMarkAsRead: async (alertIds: number[]): Promise<{ updated_count: number }> => {
    const response = await apiClient.put<{ updated_count: number }>('/alerts/bulk-read', {
      alert_ids: alertIds,
    });
    return response.data;
  },

  /**
   * Delete alert
   */
  deleteAlert: async (alertId: number): Promise<void> => {
    await apiClient.delete(`/alerts/${alertId}`);
  },
};
