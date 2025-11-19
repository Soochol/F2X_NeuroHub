/**
 * Authentication API Endpoints
 */

import apiClient from '../client';
import type { LoginRequest, LoginResponse, User } from '@/types/api';

export const authApi = {
  /**
   * Login with username and password
   */
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store token and user info
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

    return response.data;
  },

  /**
   * Get current user info
   */
  me: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Refresh access token
   */
  refresh: async (): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/refresh');

    // Update stored token
    localStorage.setItem('access_token', response.data.access_token);

    return response.data;
  },

  /**
   * Logout
   */
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');

    // Clear stored data
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};
