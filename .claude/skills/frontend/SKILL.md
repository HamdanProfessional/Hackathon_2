---
name: frontend
description: Build Next.js 16+ App Router components in frontend/app/[route]/page.tsx with TypeScript interfaces, Tailwind CSS utility classes (className='flex items-center gap-4'), and English/Urdu bilingual support via next-intl with useTranslations() hook and RTL dir='rtl' layouts. Use when creating UI pages with forms via useState(), dashboards with data fetching via fetch('/api/tasks'), chat interfaces with WebSocket or polling, or components requiring JWT Authorization: Bearer ${token} headers.
---

# Frontend Skill

Build Next.js 16+ App Router components with TypeScript, Tailwind CSS, and English/Urdu bilingual support.

## File Structure

```
frontend/
├── app/
│   ├── [locale]/           # i18n routing (en, ur)
│   │   ├── chat/
│   │   │   └── page.tsx    # Chat interface with real-time messages
│   │   ├── dashboard/
│   │   │   └── page.tsx    # Dashboard with task list and stats
│   │   ├── login/
│   │   │   └── page.tsx    # Login form
│   │   └── layout.tsx      # Root layout with fonts and metadata
│   └── globals.css         # Global Tailwind styles
├── components/
│   ├── task-form.tsx       # Task creation/editing form
│   ├── task-list.tsx       # Task display component
│   ├── task-card.tsx       # Individual task card
│   ├── chat-widget.tsx     # Floating chat widget
│   └── language-switcher.tsx  # English/Urdu toggle
├── lib/
│   ├── api.ts              # API client with JWT headers
│   ├── chatkit-config.ts   # ChatKit configuration
│   └── utils.ts            # Utility functions
├── types/
│   └── api.ts              # TypeScript interfaces for API responses
├── messages/
│   ├── en.json             # English translations
│   └── ur.json             # Urdu translations
├── middleware.ts           # Locale detection middleware
├── next.config.js          # Next.js configuration
└── tailwind.config.ts      # Tailwind configuration
```

## Quick Reference

| Action | Command | File |
|--------|---------|------|
| Create page | `touch frontend/app/[locale]/dashboard/page.tsx` | Page component |
| Create component | `touch frontend/components/task-form.tsx` | Reusable component |
| Add translations | Edit `frontend/messages/en.json` | Translation file |
| Install next-intl | `cd frontend && npm install next-intl` | i18n package |
| Add API type | Edit `frontend/types/api.ts` | TypeScript interface |
| Configure middleware | Edit `frontend/middleware.ts` | Locale routing |
| Run dev server | `cd frontend && npm run dev` | http://localhost:3000 |
| Build production | `cd frontend && npm run build` | Production build |

## When to Use This Skill

| User Request | Action | Files to Modify |
|--------------|--------|-----------------|
| "Build task form" | Create form component with useState() | `frontend/components/task-form.tsx` |
| "Display tasks from API" | Create dashboard with fetch() | `frontend/app/[locale]/dashboard/page.tsx` |
| "Add Urdu language" | Configure next-intl and add translations | `frontend/messages/ur.json`, `frontend/middleware.ts` |
| "Fix RTL layout" | Use logical properties (ps/pe/ms/me) | Component styles |
| "Add JWT to API calls" | Add Authorization header to fetch() | `frontend/lib/api.ts` |
| "Create chat interface" | Build chat page with WebSocket/polling | `frontend/app/[locale]/chat/page.tsx` |

---

## Part 1: Page Component (frontend/app/[locale]/dashboard/page.tsx)

```typescript
/**
 * Dashboard page displaying user's tasks with statistics.
 * File: frontend/app/[locale]/dashboard/page.tsx
 */
'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { apiFetch } from '@/lib/api';
import type { Task, TaskStats } from '@/types/api';

export default function DashboardPage() {
  const t = useTranslations('dashboard');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
    fetchStats();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await apiFetch('/api/tasks?page=1&page_size=20');
      const data = await response.json();
      setTasks(data.items || []);
    } catch (err) {
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    const response = await apiFetch('/api/tasks/stats/summary');
    const data = await response.json();
    setStats(data);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{t('title')}</h1>
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          onClick={() => window.location.href = '/tasks/new'}
        >
          {t('newTask')}
        </button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm">{t('total')}</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm">{t('pending')}</div>
            <div className="text-3xl font-bold text-yellow-600">{stats.pending}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm">{t('inProgress')}</div>
            <div className="text-3xl font-bold text-blue-600">{stats.in_progress}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-gray-500 text-sm">{t('completed')}</div>
            <div className="text-3xl font-bold text-green-600">{stats.completed}</div>
          </div>
        </div>
      )}

      {/* Task List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">{t('taskList')}</h2>
        </div>
        <ul className="divide-y divide-gray-200">
          {tasks.map((task) => (
            <li key={task.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
                  <p className="text-sm text-gray-500">{task.description || 'No description'}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    task.status === 'completed' ? 'bg-green-100 text-green-800' :
                    task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {t(task.status)}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    task.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                    task.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {t(task.priority)}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

## Part 2: Form Component (frontend/components/task-form.tsx)

```typescript
/**
 * Task creation/editing form with validation.
 * File: frontend/components/task-form.tsx
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { apiFetch } from '@/lib/api';

interface TaskFormProps {
  initialData?: {
    title: string;
    description: string;
    priority: string;
    due_date?: string;
  };
  onSuccess?: () => void;
}

export default function TaskForm({ initialData, onSuccess }: TaskFormProps) {
  const t = useTranslations('taskForm');
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    description: initialData?.description || '',
    priority: initialData?.priority || 'normal',
    due_date: initialData?.due_date || '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiFetch('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to create task');
      }

      if (onSuccess) {
        onSuccess();
      } else {
        router.push('/dashboard');
      }
    } catch (err) {
      setError('Failed to create task. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
          {t('title')} *
        </label>
        <input
          id="title"
          name="title"
          type="text"
          value={formData.title}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t('titlePlaceholder')}
          required
          minLength={1}
          maxLength={255}
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          {t('description')}
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={t('descriptionPlaceholder')}
          rows={4}
        />
      </div>

      {/* Priority */}
      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
          {t('priority')}
        </label>
        <select
          id="priority"
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="low">{t('low')}</option>
          <option value="normal">{t('normal')}</option>
          <option value="high">{t('high')}</option>
          <option value="urgent">{t('urgent')}</option>
        </select>
      </div>

      {/* Due Date */}
      <div>
        <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-2">
          {t('dueDate')}
        </label>
        <input
          id="due_date"
          name="due_date"
          type="date"
          value={formData.due_date}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white py-3 px-4 rounded-lg transition-colors font-medium"
      >
        {loading ? t('submitting') : t('submit')}
      </button>
    </form>
  );
}
```

---

## Part 3: API Client with JWT (frontend/lib/api.ts)

```typescript
/**
 * API client with JWT authentication headers.
 * File: frontend/lib/api.ts
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiFetchOptions extends RequestInit {
  skipAuth?: boolean;
}

/**
 * Get JWT token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

/**
 * Get auth headers for API requests
 */
export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Wrapper around fetch with automatic JWT injection
 */
export async function apiFetch(url: string, options: ApiFetchOptions = {}): Promise<Response> {
  const { skipAuth = false, ...fetchOptions } = options;

  const headers = skipAuth
    ? { 'Content-Type': 'application/json' }
    : getAuthHeaders();

  const response = await fetch(`${API_URL}${url}`, {
    ...fetchOptions,
    headers: {
      ...headers,
      ...fetchOptions.headers,
    },
  });

  // Handle 401 Unauthorized - redirect to login
  if (response.status === 401 && !skipAuth) {
    localStorage.removeItem('token');
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  return response;
}

/**
 * API methods for common operations
 */
export const api = {
  // Tasks
  getTasks: (page = 1, pageSize = 20) =>
    apiFetch(`/api/tasks?page=${page}&page_size=${pageSize}`),

  getTask: (id: number) =>
    apiFetch(`/api/tasks/${id}`),

  createTask: (data: unknown) =>
    apiFetch('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTask: (id: number, data: unknown) =>
    apiFetch(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteTask: (id: number) =>
    apiFetch(`/api/tasks/${id}`, {
      method: 'DELETE',
    }),

  // Auth
  login: (email: string, password: string) =>
    apiFetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      skipAuth: true,
    }),

  register: (email: string, password: string) =>
    apiFetch('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      skipAuth: true,
    }),
};
```

---

## Part 4: TypeScript Types (frontend/types/api.ts)

```typescript
/**
 * TypeScript interfaces for API responses.
 * File: frontend/types/api.ts
 */

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  items: Task[];
  total: number;
  page: number;
  page_size: number;
}

export interface TaskStats {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
  completion_rate: number;
}

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  response: string;
  conversation_id: number;
  message_id: number;
}
```

---

## Part 5: Bilingual Support (next-intl)

### Install next-intl

```bash
cd frontend
npm install next-intl
```

### Configure Middleware (frontend/middleware.ts)

```typescript
import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // A list of all locales that are supported
  locales: ['en', 'ur'],

  // Used when no locale matches
  defaultLocale: 'en',
});

export const config = {
  // Match only internationalized pathnames
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};
```

### Create Translation Files

**frontend/messages/en.json**:
```json
{
  "dashboard": {
    "title": "Dashboard",
    "newTask": "New Task",
    "total": "Total",
    "pending": "Pending",
    "inProgress": "In Progress",
    "completed": "Completed",
    "taskList": "Task List"
  },
  "taskForm": {
    "title": "Task Title",
    "titlePlaceholder": "Enter task title",
    "description": "Description",
    "descriptionPlaceholder": "Enter task description",
    "priority": "Priority",
    "low": "Low",
    "normal": "Normal",
    "high": "High",
    "urgent": "Urgent",
    "dueDate": "Due Date",
    "submit": "Create Task",
    "submitting": "Creating..."
  },
  "common": {
    "loading": "Loading...",
    "error": "An error occurred",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit"
  }
}
```

**frontend/messages/ur.json**:
```json
{
  "dashboard": {
    "title": "ڈیش بورڈ",
    "newTask": "نئی کام",
    "total": "کل",
    "pending": "زیر التوا",
    "inProgress": "جاری ہے ہے",
    "completed": "مکمل ہو گیا",
    "taskList": "کام کی فہرست"
  },
  "taskForm": {
    "title": "کام کا عنوان",
    "titlePlaceholder": "کام کا عنوان درج کریں",
    "description": "تفصیل",
    "descriptionPlaceholder": "کام کی تفصیل درج کریں",
    "priority": "ترجیح",
    "low": "کم",
    "normal": "عام",
    "high": "زیادہ",
    "urgent": "فوری",
    "dueDate": "آخری تاریخ",
    "submit": "کام بنائیں",
    "submitting": "بنایا جا رہا ہے..."
  },
  "common": {
    "loading": "لوڈ ہو رہا ہے...",
    "error": "ایک خرابی پیش آ گئی",
    "save": "محفوظ کریں",
    "cancel": "منسوخ کریں",
    "delete": "حذف کریں",
    "edit": "ترمیم کریں"
  }
}
```

### Update Layout for RTL (frontend/app/[locale]/layout.tsx)

```typescript
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';
import { Noto_Nastaliq_Urdu } from 'next/font/google';

const notoNastaliq = Noto_Nastaliq_Urdu({
  weight: '400',
  subsets: ['arabic'],
  variable: '--font-urdu',
});

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  // Ensure that the incoming `locale` is valid
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale} dir={locale === 'ur' ? 'rtl' : 'ltr'} className={locale === 'ur' ? notoNastaliq.className : ''}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

---

## Part 6: Language Switcher Component

```typescript
/**
 * Language switcher component for English/Urdu toggle.
 * File: frontend/components/language-switcher.tsx
 */
'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useLocale } from 'next-intl';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLocale = (newLocale: string) => {
    // Remove current locale from pathname and add new locale
    const segments = pathname.split('/');
    segments[1] = newLocale;
    const newPath = segments.join('/');
    router.push(newPath);
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => switchLocale('en')}
        className={`px-3 py-1 rounded ${
          locale === 'en'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        }`}
      >
        English
      </button>
      <button
        onClick={() => switchLocale('ur')}
        className={`px-3 py-1 rounded ${
          locale === 'ur'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        } font-urdu`}
      >
        اردو
      </button>
    </div>
  );
}
```

---

## Part 7: Tailwind RTL Utilities

```css
/* frontend/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* RTL Support - Use logical properties */
@layer utilities {
  /* Logical padding */
  .ps-4 { padding-inline-start: 1rem; }
  .pe-4 { padding-inline-end: 1rem; }

  /* Logical margin */
  .ms-2 { margin-inline-start: 0.5rem; }
  .me-2 { margin-inline-end: 0.5rem; }

  /* Logical border */
  .border-s { border-inline-start-width: 1px; }
  .border-e { border-inline-end-width: 1px; }
}
```

### RTL-Safe Component Patterns

```typescript
// ❌ WRONG - Fixed direction (breaks in RTL)
<div className="ml-4 mr-4 pl-4 pr-4">

// ✅ CORRECT - Logical properties (works in both LTR and RTL)
<div className="ms-4 me-4 ps-4 pe-4">

// Text alignment that respects direction
<div className="text-start">   // instead of text-left
<div className="text-end">     // instead of text-right

// Rounded corners that work in both directions
<div className="rounded-s-lg rounded-e-lg">  // instead of rounded-l-lg rounded-r-lg
```

---

## Quality Checklist

Before finalizing frontend components:

- [ ] **TypeScript**: All components have proper type definitions
- [ ] **Client Directive**: 'use client' added to components with hooks
- [ ] **Tailwind CSS**: Utility classes used for all styling
- [ ] **JWT Authentication**: Authorization header in all API calls
- [ ] **Loading States**: Proper loading indicators during fetch
- [ ] **Error Handling**: User-friendly error messages displayed
- [ ] **Responsive Design**: Mobile-first approach with breakpoints
- [ ] **Translations**: All strings use useTranslations() hook
- [ ] **RTL Support**: Logical properties (ps/pe/ms/me) instead of left/right
- [ ] **Language Switcher**: Component available in navigation
- [ ] **Urdu Font**: Noto Nastaliq Urdu applied conditionally
- [ ] **API Types**: TypeScript interfaces in types/api.ts
- [ ] **Environment Variables**: NEXT_PUBLIC_API_URL configured
- [ ] **Form Validation**: HTML5 validation + custom validation
- [ ] **Error Boundaries**: Error handling for component failures
