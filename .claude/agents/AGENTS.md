# Agent Skills Directory

This project includes **44 Agent Skills** (21 skills + 23 agents) for comprehensive development automation using Claude Code.

---

## Skills (.claude/skills/)

Specialized capabilities that can be invoked directly:

| # | Skill | Description |
|---|-------|-------------|
| 1 | **ai-agent-suite** | Comprehensive AI agent suite with async OpenAI, orchestration, conversation history, and monitoring |
| 2 | **backend-builder** | Complete FastAPI backend scaffolding including vertical slices (Model, Schema, Router), CRUD generation |
| 3 | **chatkit-integrator** | Integrate OpenAI Chatkit into Next.js applications with database-backed conversation persistence |
| 4 | **cli-builder** | Build command-line interface (CLI) applications using Click, Typer, or argparse |
| 5 | **cloud-deployer** | Deployment automation for local (Docker Compose, Minikube), backend (systemd, PM2), cloud (Vercel, Kubernetes) |
| 6 | **code-quality** | Comprehensive code quality analysis including code review, security, performance analysis for Python/TypeScript/SQL |
| 7 | **console-ui-builder** | Build rich, interactive console UIs using Rich, Textual, and other terminal UI libraries |
| 8 | **dapr-events** | Dapr event-driven architecture skills for pub/sub, state management, and service-to-service communication |
| 9 | **db-migration-wizard** | Automates Alembic database migrations: generates migration scripts, handles schema changes, ensures database-code alignment |
| 10 | **deployment** | Complete deployment suite including kubernetes (Docker, Helm charts, K8s manifests, Minikube/DOKS/GKE/AKS), vercel-deploy |
| 11 | **development** | Generate comprehensive test suites for Evolution of TODO project including unit tests, integration tests, and E2E tests |
| 12 | **dev-utilities** | Essential development utilities including git-committer (Conventional Commits), cors-fixer, api-schema-sync |
| 13 | **documentation** | Comprehensive documentation generation including doc-generator (README, API docs, architecture diagrams), ADR generator |
| 14 | **fastapi-crud** | Complete FastAPI CRUD generation including backend scaffolding (Model, Schema, Router with JWT auth), CRUD builder |
| 15 | **frontend** | Complete frontend suite including frontend-component (Next.js 16+ App Router components with TypeScript and Tailwind CSS), i18n-bilingual-translator |
| 16 | **mcp-integration** | MCP (Model Context Protocol) integration including tool maker, stateless agent enforcement, slash command to MCP server conversion |
| 17 | **phase-management** | Guide architectural phase transitions in Evolution of TODO project. Validates current phase completion, creates migration ADRs |
| 18 | **planning** | Comprehensive planning suite including architecture-planner (implementation plans), task-breaker (work decomposition), spec-architect |
| 19 | **project-setup** | Complete project initialization with monorepo-setup (workspace management), python-uv-setup (fast Python 3.13+ project scaffolding) |
| 20 | **qa-tester** | Comprehensive QA testing skill for E2E tests, integration tests, unit tests, console app testing, pytest, jest, and playwright |
| 21 | **skill-creator** | Guide for creating effective skills that extend Claude's capabilities with specialized knowledge, workflows, or tool integrations |

---

## Agents (.claude/agents/)

Specialist agents that coordinate complex workflows:

| # | Agent | Description |
|---|-------|-------------|
| 1 | **agent-orchestrator** | Orchestrate complex, multi-step tasks by delegating to appropriate specialist agents |
| 2 | **agent-orchestrator.yaml** | YAML configuration for agent orchestration workflows |
| 3 | **api-integration-specialist** | Synchronizing frontend-backend schemas, fixing CORS errors, configuring API clients |
| 4 | **architect** | Planning system architecture, designing implementation strategies, creating feature implementation plans |
| 5 | **architect-agent** | Architecture decision maker for complex features requiring design patterns and technology choices |
| 6 | **backend-specialist** | FastAPI, SQLModel, JWT auth, database operations, REST APIs, Chatkit backend adapter, MCP tools |
| 7 | **cloudops-engineer** | Dockerfiles, docker-compose, Helm charts, Dapr components, Kafka/Redpanda, deployment strategy |
| 8 | **code-reviewer** | Code quality, best practices, bug detection, security scanning, performance anti-pattern identification |
| 9 | **dapr-event-specialist** | Dapr pub/sub, event publishing/subscribing, Dapr components, Kafka topics, event flow testing |
| 10 | **database-migration-specialist** | Alembic migrations, schema changes, data migrations, database-code alignment |
| 11 | **deployment-engineer** | Building and pushing Docker images, deploying to Minikube or DOKS, managing Kubernetes secrets |
| 12 | **frontend-specialist** | Next.js, TypeScript, Tailwind CSS, OpenAI ChatKit, JWT handling, i18n-bilingual-translator |
| 13 | **implementer-agent** | Execute implementation plans following specifications and architecture decisions |
| 14 | **kubernetes-engineer** | Kubernetes, Docker, Helm charts, container orchestration, Minikube/DOKS/GKE/AKS deployments |
| 15 | **lead-engineer** | Development standards, code quality, git workflow, testing strategy, project governance |
| 16 | **mcp-architect** | Design MCP tool schemas, create MCP tool implementations, integrate tools with agent workflows |
| 17 | **orchestrator** | Multi-agent coordination, complex workflows, task delegation to appropriate subagents |
| 18 | **python-cli** | Python 3.13+, CLI applications, scripting, Phase I monolithic script work, environment setup |
| 19 | **qa-tester** | Comprehensive test suites for backend (FastAPI), frontend (Next.js/React), and full-stack testing |
| 20 | **specifier-agent** | Create or update feature specifications following Spec-Kit Plus template structure |
| 21 | **spec-kit-architect** | Spec-Kit Plus governance, CLAUDE.md, feature specs, compliance validation |
| 22 | **task-breakdown-agent** | Breaking down large tasks into smaller, manageable subtasks with dependencies and estimates |
| 23 | **vercel-deployer** | Deployment specialist for Vercel cloud platform for Next.js frontends and FastAPI backends |
| 24 | **tester** | General testing agent for unit tests, integration tests, and E2E test creation |

---

## Agent Categories

### Backend Development
- **backend-specialist** - FastAPI, SQLModel, JWT auth, REST APIs, MCP tools
- **database-migration-specialist** - Alembic migrations, schema changes
- **python-cli** - Python 3.13+ scripting, CLI applications

### Frontend Development
- **frontend-specialist** - Next.js, TypeScript, Tailwind CSS, ChatKit, i18n
- **api-integration-specialist** - Frontend-backend integration, schema sync, CORS

### Infrastructure & Deployment
- **cloudops-engineer** - Docker, Helm charts, Dapr, Kafka/Redpanda
- **deployment-engineer** - Kubernetes deployments (Minikube/DOKS)
- **kubernetes-engineer** - K8s manifests, Helm charts, container orchestration
- **vercel-deployer** - Vercel deployment automation

### Architecture & Planning
- **architect** - System architecture, implementation strategies
- **spec-kit-architect** - Spec-Kit Plus governance, feature specifications
- **agent-orchestrator** - Multi-agent coordination

### Leadership & Quality
- **lead-engineer** - Development standards, code quality, git workflow
- **code-reviewer** - Code review, best practices, bug detection

### Specialized
- **dapr-event-specialist** - Dapr pub/sub, event streaming
- **mcp-architect** - MCP tool design and integration

---

## Usage

### Using Skills Directly

Skills can be invoked via the Skill tool when you need specific functionality:

```
Skill: backend-scaffolder
Skill: db-migration-wizard
Skill: code-reviewer
```

### Using Agents

Agents are launched via the Task tool for complex, multi-domain tasks:

```
Task: Launch backend-specialist
Task: Launch frontend-specialist
Task: Launch cloudops-engineer
```

---

## Spec-Kit Plus Workflow

The **spec-kit-architect** agent ensures all development follows the Spec-Kit Plus workflow:

1. **Specify** (`/sp.specify`) - Create feature specification
2. **Plan** (`/sp.plan`) - Generate implementation plan
3. **Tasks** (`/sp.tasks`) - Generate actionable tasks
4. **Implement** (`/sp.implement`) - Execute implementation

See `specs/006-fix-email/` for a complete example.

---

## Total Count

- **21 Skills** - Domain-specific capabilities
- **23 Agents** - Workflow coordination specialists
- **44 Total** - Comprehensive development automation

---

**Last Updated**: 2025-12-27
