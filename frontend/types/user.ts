/**
 * User-related TypeScript type definitions
 */

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface UserPreferences {
  showCompleted?: boolean;
  compactView?: boolean;
  darkMode?: boolean;
  viewMode?: 'grid' | 'list';
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
