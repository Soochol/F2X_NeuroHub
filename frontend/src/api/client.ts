/**
 * F2X NeuroHub MES - API Client Configuration
 *
 * Axios instance with interceptors for authentication and error handling
 */

import axios, { type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import type { APIError } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';

// Create axios instance
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError<APIError>) => {
    // Handle 401 Unauthorized - Clear token and redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }

    // Handle other errors
    const errorMessage =
      error.response?.data?.detail || error.message || 'An unexpected error occurred';

    console.error('API Error:', errorMessage);

    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data,
    });
  }
);

export default apiClient;
