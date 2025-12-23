// Export all types from a central location

// User types
export interface User {
  id: number;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserResponse {
  id: number;
  email: string;
  created_at: string;
  updated_at: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Task types
export type TaskPriority = 'low' | 'medium' | 'high';
export type RecurrencePattern = 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: TaskPriority;
  due_date?: string | null;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string | null;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string | null;
  completed?: boolean;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
}

export interface TaskResponse {
  id: number;
  user_id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: TaskPriority;
  due_date?: string | null;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
  created_at: string;
  updated_at: string;
}

// Subtask types
export interface Subtask {
  id: number;
  task_id: number;
  title: string;
  description: string | null;
  completed: boolean;
  sort_order: number;
  created_at: string;
}

export interface SubtaskCreate {
  title: string;
  description?: string | null;
}

export interface SubtaskUpdate {
  completed: boolean;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}

// Form types
export interface AuthFormData {
  email: string;
  password: string;
}

export interface TaskFormData {
  title: string;
  description: string;
  priority: TaskPriority;
  due_date?: string;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
}