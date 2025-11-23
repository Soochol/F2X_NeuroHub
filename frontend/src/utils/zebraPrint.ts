/**
 * Zebra Printer Utility - Backend API Version
 * Calls backend API to print labels via network printer
 */

import apiClient from '@/api/client';

/**
 * Print WIP label via backend API
 */
export const printWIPLabel = async (wipId: string): Promise<void> => {
    try {
        const response = await apiClient.post(`/wip-items/${wipId}/print-label`);

        if (!response.data.success) {
            throw new Error(response.data.message || 'Print failed');
        }
    } catch (error: any) {
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        throw new Error(error.message || 'Failed to print label');
    }
};

/**
 * Print Serial label (placeholder - to be implemented)
 */
export const printSerialLabel = async (
    serialNumber: string,
    lotNumber?: string,
    productModel?: string
): Promise<void> => {
    // TODO: Implement serial label printing API
    throw new Error('Serial label printing not yet implemented');
};

/**
 * Print test label (placeholder - to be implemented)
 */
export const printTestLabel = async (): Promise<void> => {
    // TODO: Implement test label printing API
    throw new Error('Test label printing not yet implemented');
};

// Deprecated functions for backwards compatibility
export const isBrowserPrintAvailable = async (): Promise<boolean> => {
    return true; // Always return true since we're using backend
};

export const getDefaultPrinter = async (): Promise<any> => {
    return { name: 'Backend Printer Service' };
};

export const getAvailablePrinters = async (): Promise<any[]> => {
    return [];
};
