/**
 * API Client for Tablet Scanner App
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
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

// Create axios instance
const createApiClient = (baseURL: string): AxiosInstance => {
  const client = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  let isRefreshing = false;
  let failedQueue: any[] = [];

  const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token);
      }
    });
    failedQueue = [];
  };

  // Request interceptor - add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
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

      if (error.response?.status === 401 && originalRequest && !originalRequest.headers._retry) {
        const url = originalRequest.url || '';
        if (!url.includes('/auth/login') && !url.includes('/auth/refresh')) {
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = 'Bearer ' + token;
                }
                return client(originalRequest);
              })
              .catch((err) => Promise.reject(err));
          }

          // @ts-ignore
          originalRequest.headers._retry = true;
          isRefreshing = true;

          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const res = await axios.post(`${client.defaults.baseURL}/auth/refresh`, {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token: newRefreshToken } = res.data;
              localStorage.setItem('access_token', access_token);
              if (newRefreshToken) {
                localStorage.setItem('refresh_token', newRefreshToken);
              }

              processQueue(null, access_token);

              if (originalRequest.headers) {
                originalRequest.headers.Authorization = 'Bearer ' + access_token;
              }
              return client(originalRequest);
            } catch (refreshError) {
              processQueue(refreshError, null);
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
              return Promise.reject(refreshError);
            } finally {
              isRefreshing = false;
            }
          }
        }
      }

      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

// Default API client
let apiClient = createApiClient('/api/v1');

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

    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);

    return response.data;
  },

  refresh: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    localStorage.setItem('access_token', response.data.access_token);
    if (response.data.refresh_token) {
      localStorage.setItem('refresh_token', response.data.refresh_token);
    }
    return response.data;
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    } catch (e) {
      console.error('Logout error', e);
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
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
