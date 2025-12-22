import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { toast } from 'sonner';

// API base URL - hardcoded for production
const API_BASE_URL = 'https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app';
// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions
export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Task {
  id: number;
  title: string;
  description: string;
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
  name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
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

// API Client Class
class ApiClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.axios.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle auth errors
    this.axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          toast.error('Please log in to continue');
        } else if (error.response?.data?.detail) {
          // Show server error messages
          toast.error(error.response.data.detail);
        } else if (error.code === 'ECONNABORTED') {
          // Network timeout
          toast.error('Request timeout. Please try again.');
        } else if (error.code === 'ERR_NETWORK') {
          // Network error
          toast.error('Unable to connect to server. Please check your connection.');
        } else {
          // Generic error
          toast.error('An error occurred. Please try again.');
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('todo_access_token');
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('todo_access_token', token);
      // Also set cookie for middleware
      document.cookie = `todo_access_token=${token}; path=/; max-age=86400; sameSite=strict`;
    }
  }

  private clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('todo_access_token');
      // Also remove cookie
      document.cookie = 'todo_access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
  }

  // Auth methods
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await this.axios.post<TokenResponse>('/api/auth/login', credentials);
    this.setToken(response.data.access_token);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<TokenResponse> {
    const response = await this.axios.post<TokenResponse>('/api/auth/register', userData);
    this.setToken(response.data.access_token);
    return response.data;
  }

  logout(): void {
    this.clearToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  getCurrentUser(): User | null {
    try {
      const token = this.getToken();
      if (!token) return null;

      // Decode JWT to get user info
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: payload.sub,
        email: payload.email,
        created_at: new Date().toISOString() // We don't have created_at in token
      };
    } catch {
      return null;
    }
  }

  // Task methods
  async getTasks(params?: TaskListParams): Promise<Task[]> {
    const response = await this.axios.get<Task[]>('/api/tasks', { params });
    return response.data;
  }

  async getTask(id: number): Promise<Task> {
    const response = await this.axios.get<Task>(`/api/tasks/${id}`);
    return response.data;
  }

  async createTask(task: CreateTaskRequest): Promise<Task> {
    const response = await this.axios.post<Task>('/api/tasks', task);
    return response.data;
  }

  async updateTask(id: number, task: UpdateTaskRequest): Promise<Task> {
    const response = await this.axios.put<Task>(`/api/tasks/${id}`, task);
    return response.data;
  }

  async deleteTask(id: number): Promise<void> {
    await this.axios.delete(`/api/tasks/${id}`);
  }

  // Toggle task completion status
  async toggleTaskCompletion(id: number): Promise<Task> {
    const response = await this.axios.patch<Task>(`/api/tasks/${id}/complete`);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.axios.get<{ status: string }>('/health');
    return response.data;
  }

  // User methods
  async getUserPreferences(): Promise<any> {
    const response = await this.axios.get('/api/users/me');
    return response.data;
  }

  async exportUserData(): Promise<Blob> {
    const response = await this.axios.get('/api/users/me/export', {
      responseType: 'blob',
    });
    return response.data;
  }

  async updateUserPreferences(preferences: any): Promise<void> {
    await this.axios.put('/api/users/me/preferences', preferences);
  }

  // Chat methods
  async sendChatMessage(message: string, conversationId?: string | null) {
    const response = await this.axios.post('/api/chat', {
      message,
      conversation_id: conversationId
    });
    return response.data;
  }

  async getConversations(limit = 20, offset = 0) {
    const response = await this.axios.get('/api/chat/conversations', {
      params: { limit, offset }
    });
    return response.data;
  }

  async getConversation(conversationId: string) {
    const response = await this.axios.get(`/api/chat/conversations/${conversationId}`);
    return response.data;
  }

  async deleteConversation(conversationId: string) {
    await this.axios.delete(`/api/chat/conversations/${conversationId}`);
  }

  // Expose the axios instance for custom requests
  get axiosInstance() {
    return this.axios;
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient();

// Export axios instance for custom requests if needed
export { axios };

// Export types
export type { AxiosResponse };