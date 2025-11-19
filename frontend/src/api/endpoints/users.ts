/**
 * Users API Endpoints
 */

import apiClient from '../client';
import type { User, UserRole } from '@/types/api';

export interface UserCreate {
  username: string;
  full_name: string;
  email: string;
  password: string;
  role: UserRole;
  is_active?: boolean;
}

export interface UserUpdate {
  full_name?: string;
  email?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface PasswordChange {
  new_password: string;
}

export const usersApi = {
  /**
   * Get all users with filters
   */
  getUsers: async (params?: {
    skip?: number;
    limit?: number;
    role?: UserRole;
    is_active?: boolean;
  }): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users/', { params });
    return response.data;
  },

  /**
   * Get single user by ID
   */
  getUser: async (userId: number): Promise<User> => {
    const response = await apiClient.get<User>(`/users/${userId}`);
    return response.data;
  },

  /**
   * Create new user
   */
  createUser: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users/', data);
    return response.data;
  },

  /**
   * Update user
   */
  updateUser: async (userId: number, data: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>(`/users/${userId}`, data);
    return response.data;
  },

  /**
   * Delete user
   */
  deleteUser: async (userId: number): Promise<void> => {
    await apiClient.delete(`/users/${userId}`);
  },

  /**
   * Change user password
   */
  changePassword: async (userId: number, data: PasswordChange): Promise<User> => {
    const response = await apiClient.put<User>(`/users/${userId}/password`, data);
    return response.data;
  },
};
