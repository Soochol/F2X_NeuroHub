/**
 * User Types - Authentication and user management
 */

import { UserRole } from './enums';

// ============================================================================
// User Model
// ============================================================================

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
}

// ============================================================================
// Authentication
// ============================================================================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}
