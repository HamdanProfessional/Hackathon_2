# Frontend Guidelines

## Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Hooks + TanStack Query (optional)
- **HTTP Client**: Fetch API (native)
- **Testing**: Jest, Testing Library, Playwright

## Project Structure
```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Auth route group
│   ├── dashboard/         # Dashboard page
│   └── chat/              # Chat page (Phase III)
├── components/             # React components
│   ├── ui/                # shadcn/ui components
│   └── [feature]/         # Feature-specific components
├── lib/                   # Utilities and API clients
│   ├── api.ts            # API client
│   ├── auth.ts           # Auth utilities
│   └── types.ts          # TypeScript types
├── hooks/                 # Custom React hooks
├── styles/                # Global styles
└── public/                # Static assets
```

## Patterns

### API Client
Always use the apiClient for API calls:

```typescript
import { apiClient } from '@/lib/api'
const tasks = await apiClient.getTasks()
```

### Components
- Use shadcn/ui components when available
- Follow existing component patterns
- Use TypeScript for all components
- Prefer Server Components by default
- Use Client Components (`'use client'`) for interactivity

### Styling
- Use Tailwind CSS classes
- No inline styles (except dynamic values)
- Follow existing component patterns
- Use responsive design (mobile-first)

### State Management
- Use React hooks (useState, useContext) for local state
- Use TanStack Query for server state caching
- Keep state as close to where it's used as possible

### Authentication
- Use JWT tokens stored in httpOnly cookies
- Tokens injected via Authorization header
- Redirect to login on 401 responses
- Use `useAuth()` hook for auth state

## Available Skills

The frontend has access to specialized skills from `.claude/skills/` for common development tasks:

### Frontend Component
**Skill**: `frontend-component`

Builds Next.js 16+ App Router components with TypeScript, Tailwind CSS, and proper API integration.

**When to use**:
- Building the UI for a new feature
- Creating React components and pages
- After backend API is ready

**What it provides**:
- TypeScript interfaces in `lib/types.ts` matching backend schemas
- API client methods in `lib/[feature]-api.ts`
- Next.js page structure (page.tsx, layout.tsx, components)
- State management with loading/error/success states
- JWT authentication integration via `useAuth()` hook
- Mobile-first Tailwind CSS styling

### API Schema Sync
**Skill**: `api-schema-sync`

Synchronizes API contracts between FastAPI (Pydantic) and Next.js (TypeScript).

**When to use**:
- Backend schema changed and frontend needs updating
- Type mismatches between frontend and backend
- Adding new endpoints that need TypeScript types

**What it provides**:
- Updated TypeScript interfaces in `lib/types.ts`
- Type conversion helpers (ISO dates, enum mappings)
- Typed API client methods
- Schema alignment validation

### CORS Fixer
**Skill**: `cors-fixer`

Diagnoses and fixes CORS errors between frontend and backend.

**When to use**:
- "Blocked by CORS policy" error messages
- Frontend cannot connect to backend
- Preflight OPTIONS requests failing

**What it provides**:
- FastAPI CORSMiddleware configuration fixes
- Frontend fetch request adjustments
- Environment-specific CORS policies
- Credential handling guidance

### Chatkit Integrator
**Skill**: `chatkit-integrator`

Integrates OpenAI Chatkit with database-backed conversation persistence for Phase III AI chat interfaces.

**When to use**:
- Phase III: Building AI chat interface
- Implementing Chatkit UI components
- Integrating conversation list and chat UI

**What it provides**:
- Complete frontend setup (TypeScript types, API client, Chatkit config, chat page)
- `chat-types.ts` - TypeScript interfaces for conversations/messages
- `chat-api-client.ts` - API client with JWT authentication
- `chatkit-config.ts` - Chatkit configuration with custom backend adapter
- Real-time updates via HTTP polling (2-3 seconds)

### i18n Bilingual Translator
**Skill**: `i18n-bilingual-translator`

Implements English/Urdu bilingual internationalization with RTL support for Phase III.

**When to use**:
- Phase III: Building English/Urdu bilingual UI
- Need RTL layout for Urdu text
- Implementing language switcher

**What it provides**:
- Complete next-intl setup with App Router
- Translation files (`en.json`, `ur.json`) with comprehensive translations
- `LanguageSwitcher.tsx` component (3 variants: button, dropdown, flag)
- `rtl.css` - RTL styles with Urdu typography (Noto Nastaliq font)
- `middleware.ts` - Locale detection and routing
- Locale-based layout with direction switching (LTR/RTL)

### Integration Tester
**Skill**: `integration-tester`

Creates comprehensive integration tests for frontend-backend communication.

**When to use**:
- Testing API integration
- Validating frontend-backend communication
- Testing authentication flows

**What it provides**:
- Frontend-backend communication tests
- Authentication flow testing
- API mock server configuration
- Test data management

### Development (Test Builder)
**Skill**: `development`

Generates comprehensive test suites for frontend.

**When to use**:
- Writing tests for new features
- Creating component tests
- Improving test coverage

**What it provides**:
- Frontend testing (Jest, Testing Library, component tests)
- E2E testing (Playwright, user flows, cross-browser)
- Test fixtures and mocks for isolation
- Coverage reporting and thresholds

## Development Workflow

### 1. Feature Implementation
1. Read feature spec from `specs/features/[feature].md`
2. Review API endpoints in backend documentation
3. Use `frontend-component` skill to scaffold UI
4. Implement component logic and state management
5. Add Tailwind CSS styling
6. Test API integration
7. Write tests with `development` skill

### 2. API Integration
```typescript
// Define types in lib/types.ts
export interface Task {
  id: number;
  title: string;
  completed: boolean;
  priority_id?: number;
}

// Create API client in lib/api.ts
export async function getTasks(): Promise<Task[]> {
  const response = await fetch('/api/tasks', {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  });
  if (!response.ok) throw new Error('Failed to fetch tasks');
  return response.json();
}
```

### 3. Component Structure
```typescript
// components/TaskList.tsx
'use client';

import { useState, useEffect } from 'react';
import { Task } from '@/lib/types';
import { getTasks } from '@/lib/api';

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTasks()
      .then(setTasks)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="space-y-2">
      {tasks.map(task => (
        <div key={task.id} className="p-4 border rounded">
          {task.title}
        </div>
      ))}
    </div>
  );
}
```

### 4. Testing
```bash
# Component tests
npm test

# E2E tests
npm run test:e2e

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

## Common Patterns

### Server Component (Default)
```typescript
// app/dashboard/page.tsx
import { getTasks } from '@/lib/api';

export default async function DashboardPage() {
  const tasks = await getTasks();

  return (
    <div>
      <h1>Dashboard</h1>
      <TaskList tasks={tasks} />
    </div>
  );
}
```

### Client Component
```typescript
'use client';

import { useState } from 'react';

export function InteractiveComponent() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### Data Fetching with TanStack Query
```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { getTasks } from '@/lib/api';

export function TaskList() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: getTasks
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading tasks</div>;

  return (
    <ul>
      {data?.map(task => (
        <li key={task.id}>{task.title}</li>
      ))}
    </ul>
  );
}
```

### Form Handling
```typescript
'use client';

import { useState } from 'react';
import { createTask } from '@/lib/api';

export function CreateTaskForm() {
  const [title, setTitle] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTask({ title });
      setTitle('');
    } catch (err) {
      setError('Failed to create task');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full px-4 py-2 border rounded"
        placeholder="Task title"
      />
      {error && <p className="text-red-500">{error}</p>}
      <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">
        Create Task
      </button>
    </form>
  );
}
```

### Authentication Hook
```typescript
// hooks/useAuth.ts
import { useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check auth status on mount
    fetch('/api/auth/me')
      .then(res => {
        if (res.ok) return res.json();
        return null;
      })
      .then(data => {
        setUser(data);
        setLoading(false);
      });
  }, []);

  return { user, loading };
}
```

## Best Practices

1. **TypeScript First**: All components must be properly typed
2. **Component Organization**: Follow atomic design (atoms, molecules, organisms)
3. **Tailwind Conventions**: Use utility classes, avoid custom CSS
4. **Accessibility**: ARIA labels, keyboard navigation, semantic HTML
5. **Performance**: Code splitting, lazy loading, image optimization
6. **Error Boundaries**: Graceful degradation and user-friendly error messages
7. **Server vs Client**: Use Server Components by default, Client Components for interactivity

## Environment Variables

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production API URL (set during build)
NEXT_PUBLIC_API_URL=https://api.testservers.online
```

## Phase-Specific Guidelines

### Phase I: Console App
- No frontend (CLI only)

### Phase II: Web App
- Use Next.js App Router
- React components with TypeScript
- Tailwind CSS styling
- API integration with backend

### Phase III: AI Chatbot
- OpenAI ChatKit integration
- English/Urdu bilingual support
- RTL layout for Urdu
- JWT token management
- Real-time chat interface

### Phase IV: Microservices
- Service-specific frontend modules
- API Gateway integration
- Service mesh patterns

### Phase V: Event-Driven
- Real-time updates via polling
- Event-driven UI updates
- Optimistic UI updates

## Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm start
```

### Vercel Deployment
```bash
npx vercel
```

## Code Quality

```bash
# Type checking
npx tsc --noEmit

# Linting
npm run lint

# Format
npm run format

# Test
npm test

# E2E Test
npm run test:e2e
```
