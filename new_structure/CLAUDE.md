@.specify/memory/constitution.md

# Todo Evolution Project - Claude Code Instructions

## Project Overview
You are working on the **Todo Evolution** project - "Hackathon II: Evolution of Todo" - a comprehensive 5-phase hackathon project that evolves from simple console to sophisticated cloud-native AI system. This is a Spec-Driven Development (SDD) project where all code generation must be driven by detailed specifications.

## Project Commands

### Phase I: Console Application
```bash
# Run the console application
uv run src/main.py
```

### Phase II+: Full-Stack Web Application
```bash
# Run the backend API server
cd backend && uvicorn main:app --reload

# Run the frontend development server
npm run dev --prefix frontend
```

### Phase IV: Docker Deployment
```bash
# Run the application with Docker Compose
docker-compose up
```

### Spec-Kit Commands
```bash
# Run Spec-Kit for specification management
uv run specify

# Alternative commands based on your setup
python -m specify
specify
```

## Agent System

This project uses a consolidated agent system with **40 specialized agents** organized into **8 Core Strategic Skills**. All agents draw their capabilities from the core skills.

### Agent Reference System
To invoke an agent persona, reference: `@.claude/agents/[agent-name].md`

**Available Agents by Category:**

#### Architecture & Planning
- `@.claude/agents/architect.md` - Lead Architect
- `@.claude/agents/spec-kit-architect.md` - Spec Governance
- `@.claude/agents/specifier-agent.md` - Requirements Specialist
- `@.claude/agents/task-breakdown-agent.md` - Task Specialist

#### Backend Development
- `@.claude/agents/backend-specialist.md` - Backend Developer (FastAPI/SQLModel)
- `@.claude/agents/python-cli.md` - Python CLI Expert (Phase I)
- `@.claude/agents/database-migration-specialist.md` - Database Migration Expert

#### Frontend Development
- `@.claude/agents/frontend-specialist.md` - Frontend Developer (Next.js/React)
- `@.claude/agents/ui-ux-designer.md` - UI/UX Designer

#### AI Systems
- `@.claude/agents/ai-chatbot-specialist.md` - AI Chatbot Developer
- `@.claude/agents/mcp-tools-developer.md` - MCP Tools Developer
- `@.claude/agents/ai-workflow-orchestrator.md` - AI Workflow Manager

#### Quality Assurance
- `@.claude/agents/code-reviewer.md` - Code Reviewer
- `@.claude/agents/test-engineer.md` - Test Engineer

#### System Integration
- `@.claude/agents/api-integration-specialist.md` - API Integration Expert
- `@.claude/agents/cors-fixer.md` - CORS Specialist
- `@.claude/agents/database-admin.md` - Database Administrator
- `@.claude/agents/performance-analyst.md` - Performance Analyst

#### Cloud & DevOps
- `@.claude/agents/kubernetes-engineer.md` - Kubernetes Expert
- `@.claude/agents/docker-specialist.md` - Docker Specialist
- `@.claude/agents/dapr-specialist.md` - Dapr Specialist
- `@.claude/agents/devops-automator.md` - DevOps Automation

#### Documentation
- `@.claude/agents/workflow-librarian.md` - Documentation Manager

### Core Skills Reference
To use a core skill directly, reference: `@.claude/skills/[skill-name]`

**Available Core Skills:**
- `@.claude/skills/spec-architect-core` - Architecture planning & SDD workflow
- `@.claude/skills/backend-engineer-core` - FastAPI, SQLModel, Python development
- `@.claude/skills/frontend-ux-designer-core` - Next.js, TypeScript, Tailwind CSS
- `@.claude/skills/ai-systems-specialist-core` - OpenAI ChatKit, Agents SDK, MCP tools
- `@.claude/skills/quality-enforcer-core` - Code review, testing, performance analysis
- `@.claude/skills/workflow-librarian-core` - Documentation management, PHR generation
- `@.claude/skills/system-integrator-core` - API integration, CORS, database optimization
- `@.claude/skills/cloud-devops-lite-core` - Docker, Kubernetes, Dapr, deployment

## Technology Stack

### Backend
- **Python 3.13+**: Latest Python version
- **FastAPI**: Modern async web framework
- **SQLModel**: Type-safe SQL ORM
- **Alembic**: Database migrations
- **Neon DB**: Serverless PostgreSQL
- **Better Auth**: Authentication & Authorization
- **UV**: Ultra-fast Python package manager

### Frontend
- **Next.js 16**: With App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS
- **OpenAI ChatKit**: Conversational UI components

### AI & Integration
- **OpenAI Agents SDK**: AI agent framework
- **Official MCP SDK**: Model Context Protocol
- **Stateless Architecture**: No in-memory conversation state

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Dapr**: Distributed application runtime
- **Kafka/Redpanda**: Event streaming

## Development Workflow

### 1. Spec-Driven Development (SDD)
All development follows the SDD workflow:
1. **Specify**: Create detailed specifications in `specs/features/`
2. **Plan**: Generate implementation plans in `.specify/plans/`
3. **Tasks**: Break down into atomic tasks in `.specify/tasks/`
4. **Implement**: Generate code from specifications

### 2. Golden Workflow
**Strict Loop:** **Specify (`.specify`) → Plan (`.plan`) → Tasks (`.tasks`) → Implement**

### 3. Phase Evolution
- **Phase I**: In-memory Python console app
- **Phase II**: Full-stack web app with database
- **Phase III**: AI-powered chatbot interface (stateless)
- **Phase IV**: Kubernetes deployment
- **Phase V**: Cloud-native event-driven architecture

## The Golden Rule ⚠️

**You cannot write code manually. You must refine the Spec until Claude Code generates the correct output.**

- If code generation is incorrect → **Improve the specification**
- If implementation is incomplete → **Add more detail to the spec**
- If behavior is wrong → **Clarify requirements in the spec**
- **No code is written without a Task ID**

## Project Structure

```
new_structure/
├── .specify/                    # Global Specifications & Memory
│   ├── memory/
│   │   └── constitution.md      # Global Memory (loaded first)
│   ├── architecture/           # ADRs and architectural decisions
│   ├── plans/                  # Implementation plans
│   ├── tasks/                  # Atomic task breakdowns
│   ├── scripts/                # PowerShell scripts for workflows
│   └── templates/              # Document templates
├── .claude/
│   ├── agents/                 # Agent Personas (40 agents)
│   └── skills/                 # Core Strategic Skills (8 skills)
├── specs/                      # Feature Specifications
│   ├── constitution.md         # Project constitution
│   ├── features/               # Phase-specific feature specs
│   ├── api/                    # API specifications
│   ├── database/               # Database schemas
│   └── architecture/           # Architecture specifications
├── src/                        # Phase I console app
├── backend/                    # Phase II+ backend (FastAPI)
├── frontend/                   # Phase II+ frontend (Next.js)
├── k8s/                        # Phase IV+ Kubernetes manifests
├── requirements.md             # Master requirements document
└── CLAUDE.md                   # This file
```

## Quality Standards

### Code Quality
- All code must be reviewed by the `@.claude/agents/code-reviewer.md` agent
- Tests must be written by the `@.claude/agents/test-engineer.md` agent
- Performance must be validated by the `@.claude/agents/performance-analyst.md` agent

### Documentation
- All decisions must be documented by the `@.claude/agents/workflow-librarian.md` agent
- PHRs (Prompt History Records) must be generated for significant work
- Architecture decisions require ADRs in `.specify/architecture/`

### Security
- Security must be validated in all phases
- Authentication and authorization are mandatory
- No hard-coded secrets or credentials

## Getting Started

1. **Load Global Memory**: The constitution is automatically loaded via `@.specify/memory/constitution.md`
2. **Read Requirements**: Master requirements at `./requirements.md` - MANDATORY for all agents
3. **Understand Current Phase**: Check `specs/features/` for phase-specific requirements
4. **Use Appropriate Agents**: Reference agents using `@.claude/agents/[agent-name].md`
5. **Follow SDD Workflow**: Always Specify → Plan → Tasks → Implement
6. **Remember the Golden Rule**: Never write code manually - refine the spec instead

## Agent Usage Examples

### Architecture Tasks
```
@.claude/agents/architect.md Plan the Phase III AI chatbot architecture considering stateless design requirements
```

### Backend Development
```
@.claude/agents/backend-specialist.md Implement FastAPI endpoints for task management with SQLModel
```

### Frontend Development
```
@.claude/agents/frontend-specialist.md Create a responsive task list component using Next.js 16 and Tailwind CSS
```

### AI Integration
```
@.claude/agents/ai-chatbot-specialist.md Integrate OpenAI ChatKit with custom backend adapter for stateless conversations
```

### Quality Assurance
```
@.claude/agents/code-reviewer.md Review the authentication implementation for security vulnerabilities
```

## Emergency Contacts

- **For architectural issues**: `@.claude/agents/architect.md`
- **For spec-related problems**: `@.claude/agents/spec-kit-architect.md`
- **For code quality concerns**: `@.claude/agents/code-reviewer.md`
- **For integration problems**: `@.claude/agents/api-integration-specialist.md`
- **For AI/ChatKit issues**: `@.claude/agents/ai-chatbot-specialist.md`
- **For DevOps/Deployment**: `@.claude/agents/kubernetes-engineer.md`

---

**Remember**: The success of this project depends on disciplined adherence to specifications, proper use of the agent system, and strict compliance with the Golden Rule. Quality comes from well-defined requirements, not from manual code editing.

**Global Memory Loaded**: `@.specify/memory/constitution.md`