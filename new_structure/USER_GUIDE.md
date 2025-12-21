# 🚀 Todo Evolution - Pilot's Handbook

> **Welcome, Commander!** This is your cheat sheet for navigating the Todo Evolution project. Everything you need to know to go from zero to full-stack AI-powered productivity app.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [The Command Bank](#the-command-bank)
- [Phase Navigation](#phase-navigation)
- [Agent Reference](#agent-reference)
- [Troubleshooting](#troubleshooting)
- [Emergency Procedures](#emergency-procedures)

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment variables
cp .env.example .env

# Edit .env with your actual API keys
# REQUIRED: GOOGLE_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET

# Initialize Python environment
uv sync

# Initialize frontend (Phase II+)
npm install
```

### 2. Git Initialization
```bash
# If this is a new repository
git init
git add .
git commit -m "Initial commit: Todo Evolution project setup"

# If cloning existing repository
git clone <repository-url>
cd new_structure
```

### 3. Start Development
```bash
# Phase I: Console Application
uv run src/main.py

# Phase II+: Full Stack Application
# Backend
cd backend && uvicorn main:app --reload

# Frontend (in separate terminal)
cd frontend && npm run dev
```

---

## 📁 Project Structure

```
new_structure/
├── .specify/                    # Global Specifications & Memory
│   ├── memory/
│   │   └── constitution.md      # Global Memory (constitution)
│   ├── plans/                  # Implementation plans
│   └── tasks/                  # Atomic task breakdowns
├── .claude/
│   ├── agents/                 # 40 Specialist Agents
│   └── skills/                 # 8 Core Strategic Skills
├── specs/                      # Feature Specifications
│   ├── constitution.md         # Project constitution
│   ├── features/               # Phase-specific features
│   └── architecture/           # Architecture specs
├── src/                        # Phase I: Console app
├── backend/                    # Phase II+: FastAPI backend
├── frontend/                   # Phase II+: Next.js frontend
├── k8s/                        # Phase IV: Kubernetes manifests
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.md             # Master requirements
├── CLAUDE.md                   # Claude Code instructions
└── USER_GUIDE.md               # This file
```

---

## 🎯 The Command Bank

### 🏗️ Architecture & Planning Commands

#### Start a New Phase
```bash
# Phase I Planning
@.claude/agents/architect.md Plan Phase I console application

# Phase II Planning
@.claude/agents/architect.md Plan Phase II full stack application

# Phase III Planning
@.claude/agents/architect.md Plan Phase III AI chatbot integration

# Phase Transition
@.claude/agents/architect.md Create migration plan from Phase I to Phase II
```

#### Create Specifications
```bash
# Create feature specification
@.claude/agents/spec-kit-architect.md Create spec for user authentication

# Generate architecture plan
@.claude/agents/architect.md Create implementation plan for task CRUD

# Break down into tasks
@.claude/agents/task-breakdown-agent.md Break down task management feature
```

### 💻 Backend Development Commands

#### Python CLI (Phase I)
```bash
# Implement console application
@.claude/agents/python-cli.md Create main.py with task management commands

# Add rich terminal UI
@.claude/agents/python-cli.md Add Rich UI components for better UX

# Implement in-memory storage
@.claude/agents/python-cli.md Create TaskManager class with in-memory persistence
```

#### FastAPI Development (Phase II+)
```bash
# Create API endpoints
@.claude/agents/backend-specialist.md Implement CRUD endpoints for tasks

# Add authentication
@.claude/agents/backend-specialist.md Implement JWT authentication with Better Auth

# Database setup
@.claude/agents/database-migration-specialist.md Create SQLModel schemas and migrations

# MCP Tools (Phase III)
@.claude/agents/mcp-tools-developer.md Create MCP tools for task operations
```

### 🎨 Frontend Development Commands

#### Next.js Development (Phase II+)
```bash
# Create task management UI
@.claude/agents/frontend-specialist.md Build task list component with Next.js

# Implement authentication flow
@.claude/agents/frontend-specialist.md Create login/register forms with JWT

# Design system
@.claude/agents/ui-ux-designer.md Create design system with Tailwind CSS
```

#### AI Chat Integration (Phase III)
```bash
# ChatKit integration
@.claude/agents/ai-chatbot-specialist.md Integrate OpenAI ChatKit for conversations

# Custom AI backend
@.claude/agents/ai-chatbot-specialist.md Create FastAPI chat endpoints with Gemini

# Stateless agents
@.claude/agents/ai-workflow-orchestrator.md Implement stateless AI agent architecture
```

### 🧪 Testing & Quality Commands

#### Code Review
```bash
# Review specific file
@.claude/agents/code-reviewer.md Review src/main.py

# Review entire backend
@.claude/agents/code-reviewer.md Review backend/ directory

# Security review
@.claude/agents/code-reviewer.md Perform security audit on authentication
```

#### Testing
```bash
# Create test suite
@.claude/agents/test-engineer.md Create comprehensive test suite for task management

# API testing
@.claude/agents/test-engineer.md Create integration tests for all endpoints

# Performance testing
@.claude/agents/performance-analyst.md Analyze performance bottlenecks
```

### 🚀 Deployment Commands

#### Local Deployment
```bash
# Docker setup
@.claude/agents/docker-specialist.md Create Dockerfile for backend application

# Kubernetes (Phase IV)
@.claude/agents/kubernetes-engineer.md Create K8s manifests for deployment

# Dapr integration (Phase V)
@.claude/agents/dapr-specialist.md Configure Dapr components for microservices
```

---

## 🔄 Phase Navigation

### Phase I → Phase II Migration
```bash
# Step 1: Create migration plan
@.claude/agents/architect.md Plan migration from console to web application

# Step 2: Create database schemas
@.claude/agents/database-migration-specialist.md Create user and task tables

# Step 3: Implement FastAPI backend
@.claude/agents/backend-specialist.md Create API endpoints for existing functionality

# Step 4: Create Next.js frontend
@.claude/agents/frontend-specialist.md Build web UI for task management

# Step 5: Migrate data
@.claude/agents/database-migration-specialist.md Create data migration scripts
```

### Phase II → Phase III Enhancement
```bash
# Step 1: Plan AI integration
@.claude/agents/architect.md Design AI chatbot integration architecture

# Step 2: Add conversation tables
@.claude/agents/database-migration-specialist.md Create conversations and messages tables

# Step 3: Implement chat backend
@.claude/agents/ai-chatbot-specialist.md Create FastAPI chat endpoints

# Step 4: Integrate ChatKit
@.claude/agents/ai-chatbot-specialist.md Add ChatKit to frontend

# Step 5: Create MCP tools
@.claude/agents/mcp-tools-developer.md Implement task management MCP tools
```

---

## 👥 Agent Reference

### Architecture & Planning
- **`@.claude/agents/architect.md`** - System architecture and technical decisions
- **`@.claude/agents/spec-kit-architect.md`** - Specification governance and compliance
- **`@.claude/agents/task-breakdown-agent.md`** - Task decomposition and planning

### Backend Development
- **`@.claude/agents/backend-specialist.md`** - FastAPI, SQLModel, API development
- **`@.claude/agents/python-cli.md`** - Phase I console application development
- **`@.claude/agents/database-migration-specialist.md`** - Database migrations and schema changes

### Frontend Development
- **`@.claude/agents/frontend-specialist.md`** - Next.js, React, TypeScript development
- **`@.claude/agents/ui-ux-designer.md`** - Design system and user experience

### AI Systems
- **`@.claude/agents/ai-chatbot-specialist.md`** - AI chatbot and conversational interfaces
- **`@.claude/agents/mcp-tools-developer.md`** - MCP tool development
- **`@.claude/agents/ai-workflow-orchestrator.md`** - AI agent orchestration

### Quality Assurance
- **`@.claude/agents/code-reviewer.md`** - Code quality and security review
- **`@.claude/agents/test-engineer.md`** - Testing strategy and implementation
- **`@.claude/agents/performance-analyst.md`** - Performance optimization and monitoring

### Integration & Deployment
- **`@.claude/agents/api-integration-specialist.md`** - Frontend-backend integration
- **`@.claude/agents/kubernetes-engineer.md`** - Kubernetes deployment
- **`@.claude/agents/docker-specialist.md`** - Containerization and Docker

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### Environment Setup Problems
```bash
# Issue: Module not found errors
# Solution: Check virtual environment
which python
which uv

# Issue: Missing dependencies
# Solution: Re-sync dependencies
uv sync

# Issue: Environment variables not loading
# Solution: Verify .env file exists
ls -la .env
```

#### Database Issues
```bash
# Issue: Database connection failed
# Solution: Check DATABASE_URL in .env
echo $DATABASE_URL

# Issue: Migration errors
# Solution: Check database status
alembic current
alembic heads

# Issue: Table doesn't exist
# Solution: Run migrations
alembic upgrade head
```

#### API Issues
```bash
# Issue: CORS errors
# Solution: Check CORS configuration
@.claude/agents/cors-fixer.md Fix CORS errors between frontend and backend

# Issue: Authentication failed
# Solution: Check JWT configuration
@.claude/agents/backend-specialist.md Debug JWT authentication
```

#### Frontend Issues
```bash
# Issue: Build failed
# Solution: Check TypeScript errors
npm run build

# Issue: Component not rendering
# Solution: Check React dev tools
@.claude/agents/frontend-specialist.md Debug component rendering
```

### Agent-Specific Troubleshooting

#### Agent Not Responding
```bash
# Issue: Agent gives generic response
# Solution: Check agent's skill access
@.claude/agents/agent-name.md Review available skills and tools

# Issue: Agent doesn't know about project structure
# Solution: Update agent with current project context
@.claude/agents/agent-name.md Update with new_structure paths
```

#### Skill Not Working
```bash
# Issue: Skill tool not available
# Solution: Recreate skill with skill-creator
@.claude/skills/skill-creator Create skill-name

# Issue: Skill outdated
# Solution: Update skill with latest patterns
@.claude/skills/skill-name Update with new features
```

---

## 🚨 Emergency Procedures

### When to Escalate

1. **Critical System Failure**: Cannot start any application
2. **Database Corruption**: Data loss or inconsistency
3. **Security Breach**: Authentication or authorization failure
4. **Agent Malfunction**: Core agents not responding or giving wrong output

### Emergency Commands

#### System Recovery
```bash
# Reset to last known good state
git reset --hard HEAD

# Rebuild from scratch
rm -rf node_modules __pycache__ .pytest_cache
uv sync
npm install
```

#### Database Recovery
```bash
# Backup current data
pg_dump $DATABASE_URL > emergency_backup.sql

# Restore from backup
psql $DATABASE_URL < emergency_backup.sql
```

#### Agent Recovery
```bash
# Re-initialize agents
@.claude/agents/architect.md Re-validate system architecture

# Check agent health
@.claude/agents/backend-specialist.md Validate backend setup
@.claude/agents/frontend-specialist.md Validate frontend setup
```

### Getting Help

1. **Check Constitution First**: Always reference `CLAUDE.md` for project constraints
2. **Review Specifications**: Check `specs/constitution.md` for project requirements
3. **Use Skills Directly**: When agents fail, use skills with `@.claude/skills/skill-name`
4. **Create Issue**: Document problems in `specs/` directory for future reference

---

## 📚 Quick Reference Commands

### Development Workflow
```bash
# 1. Plan work
@.claude/agents/architect.md Plan [feature]

# 2. Create specification
@.claude/agents/spec-kit-architect.md Create spec for [feature]

# 3. Break down tasks
@.claude/agents/task-breakdown-agent.md Break down [feature]

# 4. Implement backend
@.claude/agents/backend-specialist.md Implement task T-[number]

# 5. Implement frontend
@.claude/agents/frontend-specialist.md Create component for [feature]

# 6. Test integration
@.claude/agents/test-engineer.md Test [feature]

# 7. Code review
@.claude/agents/code-reviewer.md Review [directory/file]

# 8. Deploy
@.claude/agents/kubernetes-engineer.md Deploy [service]
```

### Phase-Specific Commands
```bash
# Phase I: Console Development
@.claude/agents/python-cli.md Create main.py with task commands
@.claude/agents/python-cli.md Add Rich UI for better experience

# Phase II: Web Application
@.claude/agents/backend-specialist.md Create FastAPI endpoints
@.claude/agents/frontend-specialist.md Create Next.js pages
@.claude/agents/database-migration-specialist.md Setup database schema

# Phase III: AI Integration
@.claude/agents/ai-chatbot-specialist.md Integrate ChatKit
@.claude/agents/mcp-tools-developer.md Create MCP tools
@.claude/agents/ai-workflow-orchestrator.md Implement stateless agents

# Phase IV: Deployment
@.claude/agents/docker-specialist.md Create Docker images
@.claude/agents/kubernetes-engineer.md Deploy to K8s

# Phase V: Cloud Native
@.claude/agents/dapr-specialist.md Configure Dapr components
@.claude/agents/kafka-engineer.md Setup event streaming
```

---

## 🎯 Success Metrics

### Phase Completion Indicators
- **Phase I Complete**: ✅ Console app with full task management
- **Phase II Complete**: ✅ Full-stack web app with authentication
- **Phase III Complete**: ✅ AI chatbot with natural language task management
- **Phase IV Complete**: ✅ Kubernetes deployment with monitoring
- **Phase V Complete**: ✅ Event-driven microservices on cloud

### Quality Gates
- ✅ All tests passing
- ✅ Code review approved
- ✅ Security audit passed
- ✅ Performance benchmarks met
- ✅ Documentation complete

---

**Happy coding, Commander! 🚀**

*Remember: This project follows Spec-Driven Development. Always create specs before code!*

---

**Last Updated**: 2024-12-22
**Version**: 1.0
**Next Review**: After each phase completion