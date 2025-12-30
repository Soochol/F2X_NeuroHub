/**
 * Zebra Printer Utility - Backend API Version
 * Calls backend API to print labels via network printer
 */

import apiClient from '@/api/client';
import type { AxiosError } from 'axios';

interface PrintResponse {
    success: boolean;
    message?: string;
}

interface ErrorResponseData {
    detail?: string;
}

/**
 * Print WIP label via backend API
 */
export const printWIPLabel = async (wipId: string): Promise<void> => {
    try {
        const response = await apiClient.post<PrintResponse>(`/wip-items/${wipId}/print-label`);

        if (!response.data.success) {
            throw new Error(response.data.message || 'Print failed');
        }
    } catch (error: unknown) {
        const axiosError = error as AxiosError<ErrorResponseData>;
        if (axiosError.response?.data?.detail) {
            throw new Error(axiosError.response.data.detail);
        }
        throw new Error(axiosError.message || 'Failed to print label');
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
    // Placeholder: log parameters for future implementation
    void serialNumber;
    void lotNumber;
    void productModel;
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

interface PrinterInfo {
    name: string;
}

export const getDefaultPrinter = async (): Promise<PrinterInfo> => {
    return { name: 'Backend Printer Service' };
};

export const getAvailablePrinters = async (): Promise<PrinterInfo[]> => {
    return [];
};
