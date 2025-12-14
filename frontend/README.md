# Todo CRUD Frontend - Next.js + AI Chat

Web frontend for the Todo CRUD application with AI-powered chat interface. Built with Next.js 15, React 18, TypeScript, and OpenAI ChatKit.

## Tech Stack

### Core
- **Framework**: Next.js 15.0+ (App Router)
- **UI Library**: React 18.3+
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3.4+ with Typography plugin
- **Components**: shadcn/ui
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Phase III: AI Chat Integration ⭐ NEW
- **AI Chat**: @openai/chatkit >= 1.0.0
- **Markdown**: react-markdown >= 9.0.1
- **GFM**: remark-gfm >= 4.0.0 (GitHub Flavored Markdown)

## Project Structure

```
frontend/
├── app/                    # Next.js 15 App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   ├── login/              # Login page
│   ├── register/           # Registration page
│   ├── dashboard/          # Task dashboard (protected)
│   └── chat/               # ⭐ NEW: AI chat interface (protected)
│       └── page.tsx
├── components/             # React components
│   ├── ui/                 # shadcn/ui components
│   ├── auth/               # Authentication components
│   ├── tasks/              # Task management components
│   └── chat/               # ⭐ NEW: Chat components
│       └── chat-interface.tsx  # Main chat UI
├── lib/                    # Utilities
│   ├── api.ts              # API client with auth
│   ├── auth.ts             # Auth utilities
│   └── chat-client.ts      # ⭐ NEW: Chat API functions
├── types/                  # TypeScript definitions
│   ├── task.ts
│   └── user.ts
├── public/                 # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── .env.local.example
└── README.md               # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, set to your backend API URL:
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### 3. Run Development Server

```bash
npm run dev
```

Application will be available at http://localhost:3000

## Available Scripts

```bash
# Development server with hot-reload
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Run tests
npm test
```

## Features

### Pages

1. **Landing Page** (`/`)
   - Redirects to `/login` if not authenticated
   - Redirects to `/dashboard` if authenticated

2. **Registration** (`/register`)
   - Create new user account
   - Email and password validation
   - Auto-login after successful registration

3. **Login** (`/login`)
   - Authenticate with email and password
   - JWT token stored in localStorage
   - Redirect to dashboard after login

4. **Dashboard** (`/dashboard`) - Protected Route
   - View all user's tasks
   - Create new tasks
   - Edit task details
   - Mark tasks complete/incomplete
   - Delete tasks with confirmation
   - Navigate to AI chat

5. **⭐ AI Chat** (`/chat`) - Protected Route (Phase III)
   - Natural language task management
   - Conversation sidebar with history
   - Real-time agent responses
   - Markdown rendering (code blocks, lists, formatting)
   - Mobile responsive design
   - Loading states and error handling
   - Multi-turn conversation support

### Components

#### UI Components (shadcn/ui)
- Button
- Input
- Card
- Dialog
- Checkbox

#### Auth Components
- `LoginForm` - Email/password login form
- `RegisterForm` - User registration form

#### Task Components
- `TaskList` - Display all tasks
- `TaskItem` - Single task with actions
- `TaskCreateForm` - Create new task
- `TaskEditDialog` - Edit existing task
- `TaskDeleteDialog` - Delete confirmation

#### ⭐ Chat Components (Phase III)
- `ChatInterface` - Main chat UI component
  - Message history display
  - Input form with send button
  - Loading indicator (animated dots)
  - Error message display
  - Markdown rendering for agent responses
  - Conversation history loading
  - Auto-scroll to latest message

## API Integration

The frontend communicates with the FastAPI backend via the API client in `lib/api.ts`.

### Authentication Flow

1. User registers or logs in
2. Backend returns JWT token
3. Token stored in localStorage
4. Token included in all subsequent requests
5. Middleware protects authenticated routes

### API Functions

```typescript
// Authentication
register(email, password)
login(email, password)
logout()

// Tasks
createTask(title, description)
getTasks()
getTaskById(id)
updateTask(id, title, description)
toggleTaskCompletion(id)
deleteTask(id)

// ⭐ Chat (Phase III)
sendChatMessage(message, conversationId?)
getConversations()
getConversationMessages(conversationId)
```

### Chat Usage Example

```typescript
import { sendChatMessage, getConversations } from '@/lib/chat-client';

// Send a message to the AI assistant
const response = await sendChatMessage("Add buy milk to my list");
// response = { conversation_id: 1, response: "I've added 'Buy milk' to your task list.", tool_calls: [...] }

// Continue conversation
const followUp = await sendChatMessage("Show me my tasks", response.conversation_id);

// List all conversations
const conversations = await getConversations();
// conversations = [{ id: 1, user_id: 1, created_at: "...", updated_at: "..." }]
```

## Styling

### Tailwind CSS

This project uses Tailwind CSS with the default configuration.

Custom theme colors are defined in `tailwind.config.ts`.

### shadcn/ui

UI components from shadcn/ui are located in `components/ui/`.

To add new components:

```bash
npx shadcn-ui@latest add [component-name]
```

Example:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
```

## TypeScript

All components use TypeScript for type safety.

Type definitions are in `types/`:
- `types/user.ts` - User, LoginRequest, RegisterRequest
- `types/task.ts` - Task, TaskCreate, TaskUpdate

## Testing

### Unit Tests (Jest + React Testing Library)

```bash
npm test
```

### E2E Tests (Playwright - Optional)

```bash
npm run test:e2e
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel dashboard
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

### Manual Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Development Tips

### Adding New Pages

1. Create file in `app/[route]/page.tsx`
2. Add to middleware if route protection needed
3. Update navigation if applicable

### Adding New Components

1. Create component in `components/[category]/`
2. Use TypeScript for props
3. Style with Tailwind CSS
4. Export from component file

### State Management

This project uses React Context for global state:
- Authentication state
- User information
- Task list state

For more complex state, consider Zustand or Redux in future phases.

## Troubleshooting

### API Connection Issues

- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check that backend is running
- Verify CORS is configured in backend

### Authentication Issues

- Check localStorage for token
- Verify token is valid (not expired)
- Check middleware configuration

### Build Errors

- Clear `.next` directory: `rm -rf .next`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run lint`

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Accessibility

- Keyboard navigation supported
- ARIA labels on interactive elements
- Semantic HTML
- Screen reader compatible

## Performance

- Automatic code splitting (Next.js)
- Image optimization (Next.js Image)
- Lazy loading for task lists
- Optimistic UI updates

## Security

- XSS protection (React auto-escaping)
- CSRF protection (JWT tokens)
- Input validation on all forms
- Secure token storage

## ⭐ Phase III Features (Implemented)

- ✅ AI-powered chat interface
- ✅ Natural language task management
- ✅ Conversation history and persistence
- ✅ Markdown rendering with code blocks
- ✅ Mobile responsive chat UI
- ✅ Conversation management sidebar
- ✅ Real-time agent responses with loading states
- ✅ Error handling and retry support

## Future Enhancements (Phase IV+)

- Task categories and tags
- Task search and filtering
- Task sorting options
- Task due dates and reminders
- Dark mode toggle
- PWA support
- Offline mode
- Voice input for chat
- Multi-language support (Urdu)
- Kubernetes deployment
