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

export interface PrinterSettings {
    ip: string;
    port: number;
    queue_name: string | null;
}

export interface PrinterSettingsUpdate {
    ip?: string;
    port?: number;
    queue_name?: string;
}

export interface PrinterTestResult {
    success: boolean;
    ip: string;
    port: number;
    response_time_ms?: number;
    error?: string;
}

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
    },

    /**
     * Get printer settings
     */
    getSettings: async (): Promise<PrinterSettings> => {
        const response = await apiClient.get<PrinterSettings>('/printer/settings');
        return response.data;
    },

    /**
     * Update printer settings
     */
    updateSettings: async (settings: PrinterSettingsUpdate): Promise<PrinterSettings> => {
        const response = await apiClient.put<PrinterSettings>('/printer/settings', settings);
        return response.data;
    },

    /**
     * Test printer connection
     */
    testConnection: async (ip: string, port: number): Promise<PrinterTestResult> => {
        const response = await apiClient.post<PrinterTestResult>('/printer/settings/test', null, {
            params: { ip, port }
        });
        return response.data;
    }
};
