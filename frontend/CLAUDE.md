# Frontend Guidelines

## Stack
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS

## Patterns

### API Client
Always use the apiClient for API calls:

```typescript
import { apiClient } from '@/lib/api'
const tasks = await apiClient.getTasks()
```

### Components
- Use shadcn/ui components
- Follow existing component patterns
- Use TypeScript for all components

### Styling
- Use Tailwind CSS classes
- No inline styles
- Follow existing component patterns