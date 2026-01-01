# Frontend Resources - Evolution of TODO Edition

## Next.js 16+ App Router

### Official Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [App Router](https://nextjs.org/docs/app)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)
- [Routing](https://nextjs.org/docs/app/building-your-application/routing)

### Project Structure Used
```
frontend/
├── app/                      # App Router
│   ├── (auth)/              # Route groups
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/
│   ├── chat/
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Home page
├── components/
│   ├── ui/                  # shadcn/ui components
│   └── [feature]/           # Feature components
├── lib/                     # Utilities
│   ├── api.ts               # API client
│   ├── auth.ts              # Auth utilities
│   └── types.ts             # TypeScript types
└── hooks/                   # Custom hooks
```

## React & TypeScript

### Patterns Used

#### Server vs Client Components
```typescript
// Use Server Components by default (faster, no JS)
export default async function TaskList() {
  const tasks = await fetchTasks()
  return <div>{/* ... */}</div>
}

// Use Client Components for interactivity
'use client'
export function TaskForm() {
  const [value, setValue] = useState('')
  return <input onChange={(e) => setValue(e.target.value)} />
}
```

#### TypeScript Best Practices
- Use strict mode in tsconfig.json
- Avoid `any` type
- Use proper type inference
- Define proper interfaces for API responses

#### Type Definitions
```typescript
// lib/types.ts
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
```

## Styling - Tailwind CSS

### Theme Configuration
```javascript
// tailwind.config.js
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### Dark Theme CSS Variables
```css
/* app/globals.css */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 240 10% 3.9%;
    --primary: 240 5.9% 10%;
    --primary-foreground: 0 0% 98%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 240 5.9% 10%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 240 10% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;
  }
}
```

## shadcn/ui Components

### Installation
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add select
npx shadcn-ui@latest add switch
```

### Dark Theme Usage
```typescript
<DialogContent className="bg-zinc-900 border-zinc-800">
  <DialogTitle className="text-foreground">
    Title
  </DialogTitle>
</DialogContent>
```

## Icons - Lucide React

### Installation
```bash
npm install lucide-react
```

### Usage
```typescript
import { CalendarDays, X, Check, Trash2, Edit2 } from "lucide-react";

<CalendarDays className="h-4 w-4" />
<X className="h-4 w-4" />
```

## Toast Notifications - Sonner

### Installation
```bash
npm install sonner
```

### Usage
```typescript
import { toast } from "sonner";
import { Toaster } from "@/components/ui/toaster";

// In layout
<Toaster />

// In components
toast.success("Task created successfully");
toast.error("Failed to create task");
toast.loading("Saving...");
```

## API Client Patterns

### Axios with Interceptors
```typescript
import axios, { AxiosInstance } from 'axios';

class ApiClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL,
      timeout: 30000,
    });

    // Request interceptor for auth
    this.axios.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
}
```

### Runtime Config Support
```typescript
// lib/api.ts
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

// Load runtime config from /config.json
if (typeof window !== 'undefined') {
  fetch('/config.json')
    .then(res => res.json())
    .then((config: { NEXT_PUBLIC_API_URL?: string }) => {
      if (config.NEXT_PUBLIC_API_URL) {
        runtimeApiUrl = config.NEXT_PUBLIC_API_URL;
      }
    });
}
```

## Performance Best Practices

### 1. Code Splitting
```typescript
// Dynamic imports for heavy components
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
});
```

### 2. Image Optimization
```typescript
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
  priority
/>
```

### 3. Font Optimization
```typescript
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

## Accessibility

### ARIA Labels
```typescript
<button
  aria-label="Close dialog"
  onClick={onClose}
>
  <X className="h-4 w-4" />
</button>
```

### Keyboard Navigation
```typescript
// Handle keyboard shortcuts
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      handleSubmit();
    }
    if (e.key === "Escape") {
      onClose();
    }
  };

  document.addEventListener("keydown", handleKeyDown);
  return () => document.removeEventListener("keydown", handleKeyDown);
}, []);
```

## Deployment

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production
NEXT_PUBLIC_API_URL=https://api.testservers.online
```

### Build & Start
```bash
# Development
npm run dev

# Production build
npm run build
npm start

# Vercel deployment
npx vercel
```

## Best Practices Summary

1. **Server Components by Default**: Use for static content, data fetching
2. **Client Components for Interactivity**: Add `"use client"` directive
3. **TypeScript First**: Proper types for all data
4. **Error Boundaries**: Graceful error handling
5. **Loading States**: Show loading during async operations
6. **Form Validation**: Client-side validation before submit
7. **Dark Theme**: Support dark mode with CSS variables
8. **Mobile First**: Responsive design with Tailwind
9. **Accessibility**: ARIA labels, keyboard navigation
10. **Performance**: Code splitting, image optimization, lazy loading
