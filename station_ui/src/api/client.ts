/**
 * Axios HTTP client configuration for Station Service API.
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import type { ApiResponse, ErrorResponse } from '../types';
import { transformKeys } from '../utils/transform';

/**
 * API client instance configured for Station Service.
 */
// Determine API base URL based on environment
// In production (served from /ui), use absolute path; in dev, use relative
const getBaseUrl = (): string => {
  // Check if we're being served from /ui path (production)
  if (typeof window !== 'undefined' && window.location.pathname.startsWith('/ui')) {
    return '/api';  // Absolute path from root
  }
  return '/api';  // Development mode with proxy
};

export const apiClient: AxiosInstance = axios.create({
  baseURL: getBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Custom API error with status code for proper handling.
 */
export interface ApiError {
  code: string;
  message: string;
  status?: number;
}

/**
 * Response interceptor to transform snake_case to camelCase and handle errors.
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Transform response data keys from snake_case to camelCase
    if (response.data) {
      response.data = transformKeys(response.data);
    }
    return response;
  },
  (error: AxiosError<ErrorResponse>) => {
    const status = error.response?.status;

    if (error.response?.data?.error) {
      // Server returned a structured error - preserve status code
      return Promise.reject({
        ...error.response.data.error,
        status,
      } as ApiError);
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject({
        code: 'TIMEOUT',
        message: 'Request timed out',
      } as ApiError);
    }

    if (!error.response) {
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to server',
      } as ApiError);
    }

    return Promise.reject({
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unknown error occurred',
      status,
    } as ApiError);
  }
);

/**
 * Helper to extract data from API response.
 */
export function extractData<T>(response: AxiosResponse<ApiResponse<T>>): T {
  return response.data.data;
}

export default apiClient;
