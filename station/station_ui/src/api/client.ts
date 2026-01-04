/**
 * Axios HTTP client configuration for Station Service API.
 *
 * Note: The server now returns camelCase field names directly via Pydantic's
 * alias_generator, so no client-side transformation is needed.
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import type { ApiResponse, ErrorResponse } from '../types';

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
 * Response interceptor to handle errors.
 * Note: No transformation needed - server returns camelCase directly.
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Server returns camelCase directly via Pydantic alias_generator
    return response;
  },
  (error: AxiosError<ErrorResponse>) => {
    const status = error.response?.status;
    const responseData = error.response?.data as Record<string, unknown> | undefined;

    // Check for structured error response (ApiResponse format)
    if (responseData?.error) {
      return Promise.reject({
        ...(responseData.error as object),
        status,
      } as ApiError);
    }

    // Check for FastAPI HTTPException format (detail field)
    if (responseData?.detail) {
      const detail = responseData.detail;
      return Promise.reject({
        code: 'API_ERROR',
        message: typeof detail === 'string' ? detail : JSON.stringify(detail),
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
