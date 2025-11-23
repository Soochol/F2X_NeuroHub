/**
 * Printer Monitoring API Endpoints
 */

import apiClient from '../client';
import type {
    PrinterStatus,
    PrintLogsResponse,
    PrintLogQueryParams,
    PrintStatistics
} from '@/types/api';

export const printerApi = {
    /**
     * Get printer connection status
     */
    getStatus: async (): Promise<PrinterStatus> => {
        const response = await apiClient.get<PrinterStatus>('/printer/status');
        return response.data;
    },

    /**
     * Get print logs with filters
     */
    getLogs: async (params?: PrintLogQueryParams): Promise<PrintLogsResponse> => {
        const response = await apiClient.get<PrintLogsResponse>('/printer/print-logs', { params });
        return response.data;
    },

    /**
     * Get print statistics
     */
    getStatistics: async (params?: { start_date?: string; end_date?: string }): Promise<PrintStatistics> => {
        const response = await apiClient.get<PrintStatistics>('/printer/statistics', { params });
        return response.data;
    },

    /**
     * Test print
     */
    testPrint: async (labelType: string): Promise<{ success: boolean; message: string }> => {
        const response = await apiClient.get<{ success: boolean; message: string }>('/printer/test-print', {
            params: { label_type: labelType }
        });
        return response.data;
    }
};
