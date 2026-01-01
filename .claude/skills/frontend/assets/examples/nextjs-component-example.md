# Next.js 16+ Component Example - Evolution of TODO

This example shows the actual component patterns used in the Evolution of TODO project.

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Auth route group
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── dashboard/           # Dashboard page
│   │   └── page.tsx
│   ├── chat/                # Chat page (Phase III)
│   │   └── page.tsx
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Home page
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   └── ...
│   └── task/                # Feature components
│       ├── task-form.tsx
│       ├── task-card.tsx
│       └── task-list.tsx
├── lib/                     # Utilities
│   ├── api.ts               # API client
│   ├── auth.ts              # Auth utilities
│   ├── types.ts             # TypeScript types
│   └── utils.ts             # Helper functions
├── hooks/                   # Custom hooks
│   ├── use-auth-guard.ts
│   └── use-debounce.ts
├── styles/                  # Global styles
│   └── globals.css
└── config.json              # Runtime config
```

## Client Component with Form

```typescript
// components/task/task-form.tsx
"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CalendarDays, X } from "lucide-react";
import { Task } from "@/types";
import { toast } from "sonner";

interface TaskFormProps {
  task?: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description?: string;
    priority: "low" | "medium" | "high";
    due_date?: string;
  }) => Promise<void>;
  isSubmitting?: boolean;
}

const defaultFormData = {
  title: "",
  description: "",
  priority: "medium" as "low" | "medium" | "high",
  due_date: "",
};

export default function TaskForm({
  task,
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
}: TaskFormProps) {
  const [formData, setFormData] = useState(defaultFormData);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Populate form when editing
  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || "",
        priority: (task.priority as "low" | "medium" | "high") || "medium",
        due_date: task.due_date || "",
      });
    } else {
      setFormData(defaultFormData);
    }
    setErrors({});
  }, [task, isOpen]);

  // Keyboard shortcut (Ctrl/Cmd + Enter to submit)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !isSubmitting) {
        e.preventDefault();
        const form = document.querySelector("form");
        if (form) {
          const submitEvent = new Event("submit", { cancelable: true });
          form.dispatchEvent(submitEvent);
        }
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, isSubmitting]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});

    const submitData = {
      ...formData,
      description: formData.description || "",
      due_date: formData.due_date || undefined,
    };

    await onSubmit(submitData);
    onClose();
  };

  const handleInputChange = (
    field: keyof typeof formData,
    value: string | boolean
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

  const getTodayString = () => {
    return new Date().toISOString().split('T')[0];
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] bg-zinc-900 border-zinc-800">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-foreground">
            {task ? "Edit Task" : "Create New Task"}
          </DialogTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="absolute right-4 top-4 h-8 w-8 p-0 text-zinc-400 hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </Button>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-sm font-medium text-foreground">
              Title
              <span className="text-destructive ml-1">*</span>
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleInputChange("title", e.target.value)}
              placeholder="Enter task title"
              className={cn(
                "bg-zinc-800 border-zinc-700 focus:border-primary",
                errors.title && "border-destructive"
              )}
              maxLength={500}
              disabled={isSubmitting}
            />
            {errors.title && (
              <p className="text-xs text-destructive">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium text-foreground">
              Description
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange("description", e.target.value)}
              placeholder="Add a description (optional)"
              className="bg-zinc-800 border-zinc-700 focus:border-primary resize-none"
              rows={4}
              maxLength={2000}
              disabled={isSubmitting}
            />
          </div>

          {/* Priority */}
          <div className="space-y-2">
            <Label htmlFor="priority" className="text-sm font-medium text-foreground">
              Priority
            </Label>
            <Select
              value={formData.priority}
              onValueChange={(value: "LOW" | "MEDIUM" | "HIGH") =>
                handleInputChange("priority", value)
              }
              disabled={isSubmitting}
            >
              <SelectTrigger className="bg-zinc-800 border-zinc-700 focus:border-primary">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-zinc-800 border-zinc-700">
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 border-zinc-700 hover:bg-zinc-800"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 gradient-bg"
            >
              {isSubmitting ? "Saving..." : task ? "Update Task" : "Create Task"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

## API Client with TypeScript

```typescript
// lib/api.ts
import axios, { AxiosInstance } from 'axios';
import { toast } from 'sonner';

let runtimeApiUrl: string | null = null;

export function getApiBaseUrl(): string {
  if (runtimeApiUrl) {
    return runtimeApiUrl;
  }
  const buildTimeUrl = process.env.NEXT_PUBLIC_API_URL;
  if (buildTimeUrl && buildTimeUrl !== 'http://localhost:8000') {
    return buildTimeUrl;
  }
  return 'https://api.testservers.online';
}

// Load runtime config
if (typeof window !== 'undefined') {
  fetch('/config.json')
    .then(res => res.json())
    .then((config: { NEXT_PUBLIC_API_URL?: string }) => {
      if (config.NEXT_PUBLIC_API_URL) {
        runtimeApiUrl = config.NEXT_PUBLIC_API_URL;
      }
    })
    .catch(() => {});
}

// Type definitions
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

// API Client Class
class ApiClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: getApiBaseUrl(),
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.axios.interceptors.request.use(
      (config) => {
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
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          toast.error('Please log in to continue');
        } else if (error.response?.data?.detail) {
          toast.error(error.response.data.detail);
        } else {
          toast.error('An error occurred. Please try again.');
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  private clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  // Task methods
  async getTasks(params?: {
    search?: string;
    status?: string;
    priority?: string;
    sort_by?: string;
    sort_order?: string;
    limit?: number;
    offset?: number;
  }): Promise<Task[]> {
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

  async toggleTaskCompletion(id: number): Promise<Task> {
    const response = await this.axios.patch<Task>(`/api/tasks/${id}/complete`);
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

## Runtime Config (config.json)

```json
{
  "NEXT_PUBLIC_API_URL": "https://api.testservers.online"
}
```

This allows changing the API URL without rebuilding the Docker image.

## Key Patterns

### 1. Client Components
Use `"use client"` directive for interactive components with hooks.

### 2. Form Handling
- Controlled components with useState
- Validation before submit
- Error state management
- Loading state during submission

### 3. shadcn/ui Components
- Dark theme (bg-zinc-900, border-zinc-800)
- Lucide React icons
- Sonner for toast notifications

### 4. API Client
- Axios with interceptors
- JWT token management
- Runtime config support
- Error handling with toasts

### 5. TypeScript
- Strict types for all data
- Interface definitions matching backend
- Type-safe API calls

### 6. Tailwind CSS
- Utility-first styling
- Mobile-first responsive design
- Dark theme by default
- Custom gradient-bg class
