// Generated TypeScript API client for TODO API

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  priority: 'low' | 'medium' | 'high';
  due_date?: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface CreateTaskRequest {
  title: string;
  description?: string | null;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string | null;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string | null;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string | null;
  completed?: boolean;
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
  token: string;
  user: User;
}

export interface ApiError {
  detail: string;
}

export interface TaskListParams {
  search?: string;
  status?: 'all' | 'active' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  sort_by?: 'created_at' | 'due_date' | 'priority';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

// API Response types
export type ApiResponse<T> = T | ApiError;
export type TaskListResponse = Task[];
export type TaskResponse = Task;
export type DeleteTaskResponse = { success: boolean };