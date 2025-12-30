/**
 * API Client for Tablet Scanner App
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import { logger } from '@/services/logger';
import { STORAGE_KEYS, API_TIMEOUT_MS, API_BASE_URL } from '@/constants';
import type {
  Process,
  WIPTrace,
  ProcessStartRequest,
  ProcessStartResponse,
  ProcessCompleteRequest,
  ProcessCompleteResponse,
  TodayStatistics,
  LoginRequest,
  LoginResponse,
} from '@/types';

const apiLogger = logger.scope('API');

// Type-safe queue item for failed requests during token refresh
interface QueuedRequest {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}

// Extended request config with retry flag
interface ExtendedAxiosHeaders {
  _retry?: boolean;
  Authorization?: string;
  [key: string]: unknown;
}

// Create axios instance
const createApiClient = (baseURL: string): AxiosInstance => {
  const client = axios.create({
    baseURL,
    timeout: API_TIMEOUT_MS,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  let isRefreshing = false;
  let failedQueue: QueuedRequest[] = [];

  const processQueue = (error: unknown, token: string | null = null) => {
    failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else if (token) {
        prom.resolve(token);
      }
    });
    failedQueue = [];
  };

  // Request interceptor - add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor - handle errors
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && originalRequest && !(originalRequest.headers as ExtendedAxiosHeaders)._retry) {
        const url = originalRequest.url || '';
        if (!url.includes('/auth/login') && !url.includes('/auth/refresh')) {
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                if (originalRequest.headers) {
                  (originalRequest.headers as ExtendedAxiosHeaders).Authorization = 'Bearer ' + token;
                }
                return client(originalRequest);
              })
              .catch((err) => Promise.reject(err));
          }

          (originalRequest.headers as ExtendedAxiosHeaders)._retry = true;
          isRefreshing = true;

          const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
          if (refreshToken) {
            try {
              const res = await axios.post(`${client.defaults.baseURL}/auth/refresh`, {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token: newRefreshToken } = res.data;
              localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token);
              if (newRefreshToken) {
                localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken);
              }

              processQueue(null, access_token);

              if (originalRequest.headers) {
                (originalRequest.headers as ExtendedAxiosHeaders).Authorization = 'Bearer ' + access_token;
              }
              return client(originalRequest);
            } catch (refreshError) {
              processQueue(refreshError, null);
              localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
              localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
              window.location.href = '/login';
              return Promise.reject(refreshError);
            } finally {
              isRefreshing = false;
            }
          }
        }
      }

      if (error.response?.status === 401) {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

// Default API client - use environment variable or fallback to relative path
const getApiBaseUrl = (): string => {
  // VITE_API_BASE_URL: 프로덕션에서 전체 URL (예: https://api.example.com/api/v1)
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // 개발 환경에서는 프록시 사용
  return API_BASE_URL;
};

let apiClient = createApiClient(getApiBaseUrl());

// Update base URL
export const setApiBaseUrl = (baseUrl: string) => {
  apiClient = createApiClient(baseUrl);
};

// Auth API
export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.data.access_token);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.data.refresh_token);

    return response.data;
  },

  refresh: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.data.access_token);
    if (response.data.refresh_token) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.data.refresh_token);
    }
    return response.data;
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    } catch (e) {
      apiLogger.error('Logout error', e);
    }
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  },
};

// Process API
export const processApi = {
  // Get all processes (trailing slash required - backend has redirect_slashes=False)
  getAll: async (): Promise<Process[]> => {
    const response = await apiClient.get<Process[]>('/processes/');
    return response.data;
  },

  // Get process by ID
  getById: async (id: number): Promise<Process> => {
    const response = await apiClient.get<Process>(`/processes/${id}`);
    return response.data;
  },
};

// WIP API
export const wipApi = {
  // Get WIP trace by WIP ID string
  getTrace: async (wipId: string): Promise<WIPTrace> => {
    const response = await apiClient.get<WIPTrace>(`/wip-items/${wipId}/trace`);
    return response.data;
  },

  // Scan WIP (validate and get info)
  scan: async (wipId: string, processId?: number): Promise<WIPTrace> => {
    const params = processId ? { process_id: processId } : {};
    const response = await apiClient.post<WIPTrace>(`/wip-items/${wipId}/scan`, null, { params });
    return response.data;
  },
};

// Process Operations API
export const processOperationsApi = {
  // Start process (착공)
  start: async (data: ProcessStartRequest): Promise<ProcessStartResponse> => {
    const response = await apiClient.post<ProcessStartResponse>('/process-operations/start', data);
    return response.data;
  },

  // Complete process (완공)
  complete: async (data: ProcessCompleteRequest): Promise<ProcessCompleteResponse> => {
    const response = await apiClient.post<ProcessCompleteResponse>('/process-operations/complete', data);
    return response.data;
  },
};

// Statistics API
export const statisticsApi = {
  // Get today's statistics for a process
  getToday: async (processId: number): Promise<TodayStatistics> => {
    const response = await apiClient.get<TodayStatistics>('/analytics/today-summary', {
      params: { process_id: processId },
    });
    return response.data;
  },
};

// Error handling helper
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return '알 수 없는 오류가 발생했습니다';
};

export { apiClient };
