/**
 * Axios HTTP client configuration for Station Service API.
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import type { ApiResponse, ErrorResponse } from '../types';

/**
 * Convert snake_case keys to camelCase recursively.
 */
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

function transformKeys<T>(obj: unknown): T {
  if (obj === null || obj === undefined) {
    return obj as T;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => transformKeys(item)) as T;
  }

  if (typeof obj === 'object') {
    const transformed: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
      transformed[snakeToCamel(key)] = transformKeys(value);
    }
    return transformed as T;
  }

  return obj as T;
}

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
    if (error.response?.data?.error) {
      // Server returned a structured error
      return Promise.reject(error.response.data.error);
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject({
        code: 'TIMEOUT',
        message: 'Request timed out',
      });
    }

    if (!error.response) {
      return Promise.reject({
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to server',
      });
    }

    return Promise.reject({
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unknown error occurred',
    });
  }
);

/**
 * Helper to extract data from API response.
 */
export function extractData<T>(response: AxiosResponse<ApiResponse<T>>): T {
  return response.data.data;
}

export default apiClient;
