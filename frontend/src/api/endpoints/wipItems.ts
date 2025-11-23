/**
 * WIP Items API Endpoints
 */

import apiClient from '../client';
import type { WIPItem, WIPStatus, WipTrace } from '@/types/api';

export const wipItemsApi = {
    /**
     * Get list of WIP items with filters
     */
    getWIPItems: async (params?: {
        skip?: number;
        limit?: number;
        lot_id?: number;
        status?: WIPStatus;
        process_id?: number;
    }): Promise<WIPItem[]> => {
        const response = await apiClient.get<WIPItem[]>('/wip-items/', { params });
        return response.data;
    },

    /**
     * Get WIP item by ID
     */
    getWIPItem: async (wipId: number): Promise<WIPItem> => {
        const response = await apiClient.get<WIPItem>(`/wip-items/${wipId}`);
        return response.data;
    },

    /**
     * Get WIP statistics
     */
    getStatistics: async (params?: {
        lot_id?: number;
        process_id?: number;
    }): Promise<{
        total: number;
        created: number;
        in_progress: number;
        completed: number;
        failed: number;
        converted: number;
    }> => {
        const response = await apiClient.get('/wip-items/statistics', { params });
        return response.data;
    },

    /**
     * Get WIP traceability
     */
    getTrace: async (wipId: string): Promise<WipTrace> => {
        const response = await apiClient.get<WipTrace>(`/wip-items/${wipId}/trace`);
        return response.data;
    },
};
