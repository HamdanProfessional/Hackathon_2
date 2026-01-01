# Frontend Resources

## Next.js Documentation
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)

## React Resources
- [React Documentation](https://react.dev/)
- [React Hooks](https://react.dev/reference/react)
- [TypeScript for React](https://react.dev/learn/typescript)

## Styling
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Framer Motion](https://www.framer.com/motion/)
- [Radix UI](https://www.radix-ui.com/)

## State Management
- [Zustand](https://zustand-demo.pmnd.rs/)
- [Jotai](https://jotai.org/)
- [React Query](https://tanstack.com/query/latest)

## Best Practices

### 1. Server vs Client Components
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

### 2. TypeScript Best Practices
- Use strict mode in tsconfig.json
- Avoid `any` type
- Use proper type inference
- Define proper interfaces for API responses

### 3. Performance
- Use `React.memo` for expensive components
- Implement proper loading states
- Use `Suspense` for data fetching
- Optimize images with Next.js Image component

### 4. Accessibility
- Use semantic HTML
- Add ARIA labels where needed
- Ensure keyboard navigation
- Test with screen readers
