import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { toast } from 'sonner';
import { getSession } from '@/lib/auth-client';

// Runtime configuration - support for runtime config.json overrides
// This allows changing the backend URL without rebuilding the Docker image
let runtimeApiUrl: string | null = null;

// Get API URL - tries runtime config first, then production backend, then build-time env var, then localhost
function getApiBaseUrl(): string {
  if (runtimeApiUrl) {
    return runtimeApiUrl;
  }
  // Use production backend as default, unless build-time env is explicitly set to something else
  const buildTimeUrl = process.env.NEXT_PUBLIC_API_URL;
  if (buildTimeUrl && buildTimeUrl !== 'http://localhost:8000') {
    return buildTimeUrl;
  }
  // Default to production backend
  return 'https://backend-lac-nu-61.vercel.app';
}

// Load runtime config from /config.json (called on page load)
if (typeof window !== 'undefined') {
  fetch('/config.json')
    .then(res => res.json())
    .then((config: { NEXT_PUBLIC_API_URL?: string }) => {
      if (config.NEXT_PUBLIC_API_URL) {
        runtimeApiUrl = config.NEXT_PUBLIC_API_URL;
        console.log('[API] Using runtime config:', runtimeApiUrl);
      }
    })
    .catch(() => {
      console.log('[API] Using build-time config:', getApiBaseUrl());
    });
}

// Type definitions
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
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | 'yearly';
}

export interface CreateTaskRequest {
  title: string;
  description?: string | null;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string | null;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | 'yearly';
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string | null;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string | null;
  completed?: boolean;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly' | 'yearly';
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
      baseURL: getApiBaseUrl(),
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token and update baseURL dynamically
    this.axios.interceptors.request.use(
      (config) => {
        // Update baseURL from runtime config on each request
        const currentBaseUrl = getApiBaseUrl();
        if (config.baseURL !== currentBaseUrl) {
          config.baseURL = currentBaseUrl;
        }

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
        // Don't show error for cancelled requests
        if (error.code === 'ERR_CANCELED' || error.message?.includes('canceled')) {
          return Promise.reject(error);
        }

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

  // Token management - Integrated with Better Auth
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      // Check for Better Auth token first, then fallback to legacy token
      return (
        localStorage.getItem('access_token') ||  // Better Auth token
        localStorage.getItem('todo_access_token')     // Legacy token
      );
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      // Store in both keys for compatibility
      localStorage.setItem('access_token', token);     // Better Auth
      localStorage.setItem('todo_access_token', token);  // Legacy
      // Also set cookie for middleware
      document.cookie = `todo_access_token=${token}; path=/; max-age=86400; sameSite=strict`;
    }
  }

  private clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('todo_access_token');
      localStorage.removeItem('access_token');  // Better Auth
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

  // Better Auth integration: Get current user from session
  async getCurrentUserFromAuth(): Promise<User | null> {
    try {
      const session = await getSession();
      // Use type assertion to handle Better Auth response structure
      const sessionData = session.data as any;
      if (sessionData?.session?.user) {
        // Convert Better Auth user format to our User type
        const authUser = sessionData.session.user;
        return {
          id: parseInt(authUser.id) || 0,
          email: authUser.email,
          created_at: authUser.createdAt || new Date().toISOString()
        };
      }
      return null;
    } catch {
      return null;
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
    await this.axios.patch('/api/users/me/preferences', preferences);
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

  // Subtask methods
  async getSubtasks(taskId: number): Promise<Subtask[]> {
    const response = await this.axios.get<Subtask[]>(`/api/tasks/${taskId}/subtasks`);
    return response.data;
  }

  async createSubtask(taskId: number, subtask: SubtaskCreate): Promise<Subtask> {
    const response = await this.axios.post<Subtask>(`/api/tasks/${taskId}/subtasks`, subtask);
    return response.data;
  }

  async updateSubtask(subtaskId: number, completed: boolean): Promise<Subtask> {
    const response = await this.axios.patch<Subtask>(`/api/subtasks/${subtaskId}`, { completed });
    return response.data;
  }

  async deleteSubtask(subtaskId: number): Promise<void> {
    await this.axios.delete(`/api/subtasks/${subtaskId}`);
  }

  // Conversation Analytics methods
  async getChatOverview(): Promise<{
    total_conversations: number;
    total_messages: number;
    avg_messages_per_conversation: number;
    total_tool_calls: number;
  }> {
    const response = await this.axios.get('/api/analytics/overview');
    return response.data;
  }

  async getConversationsTimeline(period: 'daily' | 'weekly' | 'monthly' = 'daily'): Promise<{
    period: string;
    data: Array<{ date: string; count: number }>;
    total_conversations: number;
  }> {
    const response = await this.axios.get('/api/analytics/conversations-timeline', {
      params: { period }
    });
    return response.data;
  }

  async getToolUsage(): Promise<{
    total_tool_calls: number;
    tool_stats: Array<{ tool_name: string; call_count: number }>;
    most_used_tool: string | null;
  }> {
    const response = await this.axios.get('/api/analytics/tool-usage');
    return response.data;
  }

  async getMessageDistribution(): Promise<{
    total_messages: number;
    distribution: Array<{ role: string; count: number; percentage: number }>;
  }> {
    const response = await this.axios.get('/api/analytics/message-distribution');
    return response.data;
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