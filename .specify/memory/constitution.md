# The Evolution of TODO: Project Constitution
<!--
SYNC IMPACT REPORT:
Version: 2.0.0 → 3.0.0
Change Type: MAJOR - Phase II complete, transitioning to Phase III (AI-Powered Chatbot)
Modified Sections:
  - Phase II: Modular Monolith → COMPLETED
  - Phase III: Agent-Augmented System → CURRENT
  - Agent System & Skills → NEW (v3.0.0)
Added Technologies:
  - OpenAI Agents SDK for AI agent orchestration
  - Model Context Protocol (MCP) for tool integration
  - OpenAI ChatKit for conversational UI
  - Conversation persistence (messages, conversations tables)
Added Principles:
  - AI Agent Integration Standards
  - MCP Tool Design Patterns
  - Stateless Agent Architecture
  - Conversation State Management
Breaking Changes:
  - New database tables: conversations, messages
  - New API endpoints: /api/chat, /api/conversations
  - New MCP server exposing task operations as tools
Templates Status:
  ✅ plan-template.md - Compatible with agent architecture
  ✅ spec-template.md - Compatible with conversational features
  ✅ tasks-template.md - Compatible with MCP implementation tasks
Follow-up TODOs:
  - Create Phase III migration ADR (Phase II → Phase III)
  - Document AI agent behavior and MCP tool specifications
  - Define conversation flow and state management strategy
-->

## Project Vision

**Project Name**: The Evolution of TODO

**Philosophy**: This application MUST evolve through distinct architectural phases, starting simple (CLI) and progressing to cloud-native AI-powered systems. Each phase builds upon the previous, demonstrating architectural evolution from monolithic scripts to event-driven microservices.

**Role Definition**: You are the Chief System Architect and Lead Engineer responsible for guiding this evolution while maintaining system integrity and spec-driven discipline at every stage.

## Core Principles (Across All Phases)

### I. Spec-First Development (NON-NEGOTIABLE)

Every feature MUST begin with a written specification before any code is written. The specification defines the business requirements, user stories, acceptance criteria, and success metrics in technology-agnostic terms.

**Rules:**
- NO code written until spec.md exists and is approved
- Specifications capture "what" and "why", never "how"
- All requirements MUST have testable acceptance criteria
- Unclear requirements marked with NEEDS CLARIFICATION
- Specs are versioned and maintained as living documents
- This principle applies to ALL phases without exception

**Rationale:** Prevents scope creep, misaligned implementations, and wasted development effort. Ensures all stakeholders agree on requirements before technical decisions are made. Critical for managing complexity as system evolves across phases.

### II. Evolutionary Architecture

The application MUST transition gracefully through defined architectural phases. Each phase introduces new capabilities while maintaining backward compatibility where feasible.

**Architecture Evolution Path:**
1. **Phase I**: Monolithic Script (single file CLI)
2. **Phase II**: Modular Monolith (web app with clear module boundaries)
3. **Phase III**: Agent-Augmented System (AI agents + MCP integration)
4. **Phase IV**: Microservices (containerized, orchestrated services)
5. **Phase V**: Event-Driven Architecture (Kafka + Dapr + cloud-native)

**Rules:**
- Each phase MUST complete fully before starting next phase
- Phase transitions require ADR (Architectural Decision Record) documenting rationale
- Migration path from previous phase MUST be documented in spec
- Breaking changes require major version bump and explicit justification
- No skipping phases (evolutionary, not revolutionary)

**Rationale:** Controlled evolution prevents "big bang" rewrites and allows learning from each architectural pattern. Demonstrates real-world progression from simple to complex systems.

### III. Technology Stack Governance

Each phase has a defined technology stack that MUST be respected. No premature introduction of future-phase technologies.

**Phase-Specific Stacks:**
- **Phase I**: Python 3.13+ CLI (standard library only)
- **Phase II**: Next.js frontend + FastAPI backend + Neon (PostgreSQL)
- **Phase III**: Phase II stack + AI Agents + MCP (Model Context Protocol)
- **Phase IV**: Phase III stack + Kubernetes + Helm charts
- **Phase V**: Phase IV stack + Kafka + Dapr + cloud services

**Rules:**
- Use ONLY technologies approved for current phase
- External dependencies require explicit constitution approval
- Technology choices documented in ADRs with rationale
- New technologies introduced only during phase transitions
- Backward compatibility maintained during stack evolution

**Rationale:** Enforces architectural discipline and prevents technology sprawl. Ensures each phase demonstrates specific architectural patterns without conflation.

### IV. Phase Transition Discipline

Transitioning between phases requires explicit governance and cannot occur mid-feature.

**Rules:**
- Phase transitions require updated constitution (MAJOR version bump)
- All Phase N features MUST be complete before Phase N+1 begins
- Migration strategy from Phase N to Phase N+1 documented in ADR
- No mixing of phase technologies (clean boundaries)
- User-facing features remain functional during transitions

**Rationale:** Prevents architectural chaos and ensures each phase is fully validated before evolution. Maintains system stability during transitions.

## Agent System & Skills Infrastructure (v3.0.0)

### Overview

The project implements a sophisticated multi-agent orchestration system with specialized agents and reusable skills. This infrastructure enables efficient delegation of complex tasks to domain-specific expert agents, each equipped with specialized capabilities through skills.

**Architecture:**
- **Orchestrator**: Meta-agent that coordinates specialist agents
- **Specialist Agents**: Domain-specific experts (backend, frontend, infrastructure, etc.)
- **Skills**: Reusable capabilities that can be invoked independently or by agents
- **Agent-Skill Relationship**: Each agent has access to multiple related skills

### Agent Categories & Specialist Agents

#### Backend Development Agents

**backend-specialist**
- **Purpose**: FastAPI, SQLModel, JWT auth, database operations, REST APIs
- **Skills**: backend-scaffolder, crud-builder, fastapi-endpoint-generator, sqlmodel-schema-builder, integration-tester, mcp-tool-maker, agent-orchestrator, chatkit-integrator, conversation-history-manager, stateless-agent-enforcer, performance-analyzer, phr-documenter, python-uv-setup, rag-indexer, rag-retriever, rag-answerer, rag-manager, task-breaker, test-builder, code-reviewer
- **Phases**: I, II, III, V

**database-migration-specialist**
- **Purpose**: Alembic migrations, schema changes, data integrity
- **Skills**: db-migration-wizard
- **Phases**: II+

#### Frontend Development Agents

**frontend-specialist**
- **Purpose**: Next.js, TypeScript, Tailwind CSS, OpenAI ChatKit, JWT handling
- **Skills**: frontend-component, api-schema-sync, cors-fixer, chatkit-integrator, i18n-bilingual-translator
- **Phases**: II, III

**api-integration-specialist**
- **Purpose**: Frontend-backend integration, schema sync, type safety
- **Skills**: api-schema-sync, cors-fixer, chatkit-integrator
- **Phases**: II+

#### Infrastructure & Deployment Agents

**cloudops-engineer**
- **Purpose**: Dockerfiles, docker-compose, Helm charts, Dapr, Kafka/Redpanda
- **Skills**: infrastructure, cloud-devops, deployment-validator, dapr-event-flow, k8s-deployer
- **Phases**: IV, V

**deployment-engineer**
- **Purpose**: Kubernetes deployments, Docker images, secrets, Dapr
- **Skills**: k8s-deployer, k8s-troubleshoot, deployment-validator, dapr-event-flow
- **Phases**: IV, V

**kubernetes-engineer**
- **Purpose**: Kubernetes, Docker, Helm charts, container orchestration
- **Skills**: k8s-deployer, k8s-troubleshoot
- **Phases**: IV, V

**dapr-event-specialist**
- **Purpose**: Dapr pub/sub, event publishing/subscribing, service communication
- **Skills**: dapr-event-flow
- **Phases**: V

#### Architecture & Planning Agents

**architect**
- **Purpose**: System architecture, design patterns, implementation strategies
- **Skills**: architecture-planner, adr-generator, spec-architect, doc-generator, monorepo-setup, performance-analyzer, phr-documenter
- **Phases**: All

**spec-kit-architect**
- **Purpose**: Spec-Kit Plus governance, CLAUDE.md, feature specs, compliance
- **Skills**: spec-architect, phr-documenter
- **Phases**: All

#### Leadership & Quality Agents

**lead-engineer**
- **Purpose**: Development standards, code quality, git workflow, testing
- **Skills**: git-committer, code-reviewer, performance-analyzer, test-builder, integration-tester, task-breaker, deployment-validator, phr-documenter
- **Phases**: All

**orchestrator**
- **Purpose**: Multi-agent coordination, complex workflows, task delegation
- **Skills**: agent-orchestrator, task-breaker, phase-management
- **Phases**: All

**code-reviewer**
- **Purpose**: Code quality, best practices, bug detection
- **Skills**: code-reviewer, performance-analyzer, integration-tester
- **Phases**: All

**tester**
- **Purpose**: Test execution, debugging, coverage measurement
- **Skills**: development, console-app-tester, integration-tester
- **Phases**: All

**qa-tester**
- **Purpose**: Comprehensive test suites, validation, bug verification
- **Skills**: development, console-app-tester, integration-tester
- **Phases**: All

#### Python & CLI Agents

**python-cli**
- **Purpose**: Python 3.13+, CLI applications, scripting, Phase I development
- **Skills**: cli-builder, console-ui-builder, python-uv-setup
- **Phases**: I

### Skills Library

Skills are specialized, reusable capabilities that can be invoked independently or by agents. They are organized in `.claude/skills/` by category.

#### Phase Management Skills

**phase-management**
- **Purpose**: Guide transitions between architectural phases
- **Usage**: `/skill phase-transition target_phase=phase-ii`
- **Provides**: Migration ADR, constitution update, migration spec, transition checklist

#### Deployment Skills

**deploy-vercel**
- **Purpose**: Deploy Next.js and FastAPI apps to Vercel
- **Usage**: `/skill deploy-vercel app=frontend`
- **Provides**: Automated deployment, environment configuration, build optimization, health checks

#### Testing Skills

**console-app-tester**
- **Purpose**: Test Python console applications
- **Usage**: `/skill console-app-tester path=src`
- **Provides**: File structure validation, model verification, CLI command testing, input validation

**development (test-builder)**
- **Purpose**: Generate comprehensive test suites
- **Usage**: `/skill test-generator feature=todo-crud`
- **Provides**: Unit tests, integration tests, E2E tests, test infrastructure

**integration-tester**
- **Purpose**: Create comprehensive integration tests
- **Usage**: User says "test the integration"
- **Provides**: API endpoint tests, database operations tests, third-party service tests

#### Infrastructure Skills

**infrastructure (kubernetes-setup)**
- **Purpose**: Set up Kubernetes environments (local & cloud)
- **Usage**: `/skill kubernetes-setup environment=local`
- **Provides**: Kubernetes manifests, Helm charts, namespace configuration, kubectl-ai integration

#### AI & MCP Skills

**ai-mcp**
- **Purpose**: Build MCP server from slash commands
- **Usage**: `/skill mcp-builder`
- **Provides**: MCP server generation, `.mcp.json` configuration, command-to-prompt conversion

**ai-mcp/agent-builder**
- **Purpose**: Create AI agents with AsyncOpenAI and Google Gemini
- **Usage**: `/skill agent-builder`
- **Provides**: Gemini integration, MCP tool integration, conversation management

#### Cloud & DevOps Skills

**cloud-devops**
- **Purpose**: Deploy to cloud Kubernetes with Kafka and Dapr
- **Usage**: `/skill cloud-deployment provider=digitalocean`
- **Provides**: Cluster provisioning, Kafka deployment, Dapr integration, CI/CD pipeline

#### Development Skills

**development**
- **Purpose**: Generate comprehensive test suites
- **Usage**: `/skill test-generator feature=todo-crud`
- **Provides**: Unit tests, integration tests, E2E tests, CI configuration

#### Backend Skills

**backend-scaffolder**
- **Purpose**: Scaffold complete FastAPI vertical slices
- **Usage**: User says "implement the backend"
- **Provides**: SQLModel models, Pydantic schemas, FastAPI routers, JWT auth, pytest tests

**crud-builder**
- **Purpose**: Generate complete CRUD operations
- **Usage**: User says "Create CRUD for..."
- **Provides**: SQLModel schemas, Pydantic models, FastAPI routers with 5 CRUD endpoints, pagination

**fastapi-endpoint-generator**
- **Purpose**: Generate custom FastAPI endpoints
- **Usage**: User says "Create endpoint for..."
- **Provides**: Custom endpoints with validation, error handling, OpenAPI docs

**sqlmodel-schema-builder**
- **Purpose**: Build SQLModel database schemas
- **Usage**: User says "Create database schema"
- **Provides**: Schema design, Alembic migrations, relationships, best practices

**db-migration-wizard**
- **Purpose**: Automate Alembic database migrations
- **Usage**: User says "Add a new database column"
- **Provides**: Migration generation, schema changes, data type conversion, rollback testing

**mcp-tool-maker**
- **Purpose**: Create MCP tools for AI agents
- **Usage**: Phase III - "expose this function to AI"
- **Provides**: MCP server setup, tool registration, FastAPI integration, JWT auth

**agent-orchestrator**
- **Purpose**: Orchestrate AI agent initialization
- **Usage**: Phase III - "create an AI agent"
- **Provides**: Conversation models, AgentOrchestrator class, FastAPI chat router, JWT integration

**chatkit-integrator**
- **Purpose**: Integrate OpenAI Chatkit with database persistence
- **Usage**: Phase III - "Implement Chatkit backend"
- **Provides**: Complete setup, stateless agent, chat endpoints, implementation guide

**conversation-history-manager**
- **Purpose**: Conversation history management for AI chat
- **Usage**: Phase III - "Implement conversation persistence"
- **Provides**: Query patterns, context loading, pagination, soft delete, polling

**stateless-agent-enforcer**
- **Purpose**: Validate stateless agent architecture
- **Usage**: Phase III - "validate stateless architecture"
- **Provides**: Static analysis validator, compliance tests, code review checklist

#### Frontend Skills

**frontend-component**
- **Purpose**: Build Next.js App Router components
- **Usage**: User says "build the UI"
- **Provides**: TypeScript interfaces, API clients, page structure, state management, Tailwind styling

**api-schema-sync**
- **Purpose**: Sync FastAPI (Pydantic) and Next.js (TypeScript) schemas
- **Usage**: Backend schema changed
- **Provides**: Updated TypeScript interfaces, type conversion helpers, API client methods

**cors-fixer**
- **Purpose**: Fix CORS errors between frontend and backend
- **Usage**: "Blocked by CORS policy" error
- **Provides**: FastAPI CORSMiddleware fixes, frontend fetch adjustments, environment-specific policies

**i18n-bilingual-translator**
- **Purpose**: English/Urdu bilingual support with RTL
- **Usage**: Phase III - "Add Urdu translation"
- **Provides**: next-intl setup, translation files, LanguageSwitcher component, RTL styles

#### CLI Skills

**cli-builder**
- **Purpose**: Build CLI applications
- **Usage**: Phase I - "Create CLI"
- **Provides**: Typer/Click/argparse templates, todo CLI example, Git-style subcommands

**console-ui-builder**
- **Purpose**: Build rich terminal UIs
- **Usage**: Phase I - "Create console UI"
- **Provides**: Rich/Textual templates, progress bars, tables, interactive prompts

**python-uv-setup**
- **Purpose**: Set up Python with uv package manager
- **Usage**: "Set up Python with uv"
- **Provides**: uv installation, project initialization, virtual environment, dependency management

#### Architecture Skills

**architecture-planner**
- **Purpose**: Create comprehensive implementation plans
- **Usage**: User says "plan the implementation"
- **Provides**: Component architecture, data models, API design, task breakdown, testing strategy

**adr-generator**
- **Purpose**: Create Architecture Decision Records
- **Usage**: Significant architectural decision made
- **Provides**: Complete ADR with context, options, rationale, consequences

**doc-generator**
- **Purpose**: Generate comprehensive documentation
- **Usage**: User says "Generate documentation for..."
- **Provides**: README, API docs, architecture docs, deployment guides

**monorepo-setup**
- **Purpose**: Set up monorepo structure
- **Usage**: "Set up monorepo"
- **Provides**: pnpm workspace, Turborepo build orchestration, shared packages, TypeScript references

**performance-analyzer**
- **Purpose**: Analyze application performance
- **Usage**: User says "Analyze performance"
- **Provides**: API performance analysis, database query analysis, resource usage monitoring

**spec-architect**
- **Purpose**: Generate Spec-Kit Plus compliant feature specifications
- **Usage**: User says "design a new feature"
- **Provides**: Complete feature specification, automatic PHR creation

**phr-documenter**
- **Purpose**: Automate Prompt History Record creation
- **Usage**: After completing implementation work
- **Provides**: Automated PHR generation with frontmatter, routing, ID allocation

**task-breaker**
- **Purpose**: Break down large tasks into subtasks
- **Usage**: User says "break down this feature"
- **Provides**: Task decomposition, acceptance criteria, story points, dependencies

**test-builder**
- **Purpose**: Build comprehensive test suites
- **Usage**: User says "write tests"
- **Provides**: Backend tests (pytest), frontend tests (Jest), E2E tests (Playwright)

**code-reviewer**
- **Purpose**: Perform comprehensive code review
- **Usage**: User says "review this code"
- **Provides**: Multi-tool analysis, security scan, best practices validation

#### Event-Driven Skills

**dapr-event-flow**
- **Purpose**: Automate Dapr event-driven architecture
- **Usage**: User says "set up Dapr pub/sub"
- **Provides**: Event schemas, Dapr components, publishers, subscribers, testing

**dapr-events**
- **Purpose**: Dapr event-driven architecture expertise
- **Usage**: Phase V microservices communication
- **Provides**: Pub/sub, state management, service invocation, secrets management

#### RAG Skills (Retrieval-Augmented Generation)

**rag-indexer**
- **Purpose**: Index documents for RAG
- **Usage**: Phase III - "Index documents for RAG"
- **Provides**: Document chunking, embedding generation, vector database integration

**rag-retriever**
- **Purpose**: Retrieve relevant documents from vector databases
- **Usage**: Phase III - "Search documents"
- **Provides**: Semantic search, hybrid search, MMR, reranking

**rag-answerer**
- **Purpose**: Generate answers from retrieved context
- **Usage**: Phase III - "Answer with sources"
- **Provides**: Answer generation, source citation, confidence scoring, hallucination reduction

**rag-manager**
- **Purpose**: Orchestrate complete RAG pipelines
- **Usage**: Phase III - "Set up RAG system"
- **Provides**: Pipeline management, multi-collection support, scheduled updates, monitoring

### Agent-Skill Invocation Patterns

#### Pattern 1: Direct Skill Invocation
```
User: "Use the kubernetes-setup skill to deploy to Minikube"
→ Skill tool invoked directly with kubernetes-setup
```

#### Pattern 2: Agent with Skill
```
User: "Implement the backend for the task CRUD feature"
→ backend-specialist agent launched
→ Agent uses backend-scaffolder skill to generate boilerplate
→ Agent implements custom logic
→ Agent uses test-builder skill to create tests
```

#### Pattern 3: Orchestrator Coordination
```
User: "Build the complete task management feature"
→ orchestrator agent analyzes requirements
→ orchestrator launches architect to create plan
→ orchestrator launches backend-specialist (with backend-scaffolder)
→ orchestrator launches frontend-specialist (with frontend-component)
→ orchestrator collects and synthesizes results
```

### Agent Orchestration Workflow

#### 1. Task Analysis
- Analyze user request complexity
- Identify required domains (backend, frontend, infrastructure, etc.)
- Determine execution strategy (parallel vs. sequential)

#### 2. Agent Selection
Choose appropriate specialist agent(s):
- **Backend tasks** → backend-specialist, database-migration-specialist
- **Frontend tasks** → frontend-specialist, api-integration-specialist
- **Infrastructure** → cloudops-engineer, deployment-engineer, dapr-event-specialist
- **Architecture** → architect, spec-kit-architect
- **Quality** → lead-engineer, code-reviewer, tester, qa-tester

#### 3. Skill Invocation
Agents can use skills directly:
```
Skill({ skill: "skill-name" })
```

#### 4. Result Synthesis
- Collect outputs from all agents
- Verify integration between components
- Present unified summary to user

### Agent Coordination Patterns

#### Parallel Execution
Tasks with no dependencies run simultaneously:
```
Task tool: backend-specialist (build API)
Task tool: frontend-specialist (build UI)
→ Both run in parallel
```

#### Sequential Execution
Tasks with dependencies run in order:
```
Task tool: database-migration-specialist (create tables)
→ Wait for completion
Task tool: backend-specialist (use new schema)
→ Wait for completion
Task tool: frontend-specialist (consume API)
```

#### Batch Execution
Group related tasks for same agent:
```
backend-specialist: Create multiple endpoints in single invocation
```

### Skills vs Agents Decision Tree

#### Use Skills Directly When:
- Task is well-defined and narrow in scope
- You need specific functionality (e.g., generate CRUD, fix CORS)
- Task doesn't require full agent workflow coordination

#### Use Agents When:
- Task requires analysis and planning
- Multiple decisions need to be made
- Task involves multiple related subtasks
- You need expertise in a specific domain

#### Combining Agents and Skills
Often the best approach:
1. Agent analyzes and plans
2. Skills execute specific pieces
3. Agent validates and integrates

### Quality Assurance

#### Before Agent/Skill Invocation:
- Verify task requirements are clear
- Check if existing code needs review
- Identify dependencies and blockers

#### During Execution:
- Monitor agent/skill progress
- Handle errors and retries
- Validate outputs against requirements

#### After Completion:
- Verify all tests pass
- Check code quality standards
- Ensure integration points work
- Create PHR documenting work
- Commit with conventional commit format

### Git Workflow (MANDATORY)

After EVERY task completion:
1. Review changes: `git status`
2. Stage files: `git add files`
3. Commit with conventional commit format:
   ```
   <type>(<scope>): <description>

   [optional body]

   [optional footer]
   ```
4. Push: `git push origin main`

### Bonus Points Achievement

#### Reusable Intelligence (+200 points)
- ✅ 49 Agent Skills created
- ✅ Skills used across Phases I-III
- ✅ Skills documented in PHRs and specs
- ✅ Agent-skill relationships documented

#### Cloud-Native Blueprints (+200 points)
- ✅ Infrastructure skills ready for Phase IV/V
- ✅ Deployment blueprints documented
- ✅ Spec-driven infrastructure patterns

## Phase I: Monolithic Script ✅ COMPLETED

### Storage Constraints

For Phase I ONLY, the application MUST use in-memory data structures (lists, dictionaries) for all data storage. NO persistent storage mechanisms are permitted in Phase I.

**Rules (Phase I Only):**
- NO SQL databases (PostgreSQL, MySQL, SQLite, etc.)
- NO NoSQL databases (MongoDB, Redis, etc.)
- NO file-based persistence (JSON, CSV, pickle, etc.)
- Data stored ONLY in Python lists, dictionaries, or similar in-memory structures
- Data loss on application restart is EXPECTED and ACCEPTABLE for Phase I

**Phase Transition:** Phase II will introduce Neon (PostgreSQL) for persistence. Migration ADR required.

**Rationale:** Phase I focuses on core business logic and user experience without persistence complexity. Simplifies initial implementation and testing. Validates core CRUD operations before adding persistence.

### Dependency Constraints

All Phase I implementation MUST use only Python's standard library. NO external dependencies or third-party packages are permitted in Phase I.

**Rules (Phase I Only):**
- NO pip packages or external libraries
- Use built-in modules only (typing, datetime, sys, dataclasses, etc.)
- NO framework dependencies (Flask, FastAPI, Click, etc.)
- Database drivers explicitly forbidden (psycopg2, pymongo, etc.)

**Phase Transition:** Phase II will introduce FastAPI, Next.js, and Neon client libraries.

**Rationale:** Eliminates dependency management complexity in initial phase. Forces clear understanding of core Python capabilities. Demonstrates that complex frameworks aren't needed for simple CLIs.

### Interface Constraints

Phase I application MUST run in a continuous interactive loop until the user explicitly chooses to exit. The application provides a menu-driven interface for all operations.

**Rules (Phase I Only):**
- Application runs in infinite `while True` loop
- User presented with menu of options after each operation
- Only "Exit" or equivalent option terminates the application
- Invalid input handled gracefully with error messages and re-prompt
- Each operation returns control to main menu

**Phase Transition:** Phase II will replace CLI with Next.js web UI + FastAPI REST endpoints.

**Rationale:** Standard pattern for CLI tools. Provides intuitive user experience for console applications. Allows multiple operations without restarting.

### Code Quality Standards (Phase I)

**Language & Version:**
- Python 3.13+
- Type hints REQUIRED for all function signatures and class attributes
- Docstrings REQUIRED for all public functions and classes (Google style)

**Project Structure:**
- Single file implementation in `src/main.py`
- Entry point: `if __name__ == "__main__":` block required
- Modularity: Functions and classes for organization even within single file

**Error Handling:**
- Try-except blocks for user input and validation
- Input validation before processing (type checks, range checks, null checks)
- Graceful error messages (no stack traces shown to users)

**Naming Conventions:**
- snake_case for functions/variables
- PascalCase for classes
- UPPER_CASE for constants

**Comments:**
- Inline comments for complex logic only
- Prefer self-documenting code (clear names, simple logic)
- Docstrings explain "why", not "what"

## Phase III: AI Agent Integration Standards

### AI Agent Architecture Principles

**Stateless Agent Design:**
- ALL agent endpoints MUST be stateless (no in-memory session state)
- Conversation history stored in database (conversations, messages tables)
- Each request contains full context (conversation_id + message history)
- Server can restart without losing conversation state
- Horizontally scalable design (any instance handles any request)

**MCP Tool Integration:**
- Task operations exposed as MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
- Each MCP tool MUST validate user ownership (user_id parameter required)
- MCP tools are stateless and database-backed
- Tools return structured responses (task_id, status, data)
- Error handling with specific error codes and messages

**Conversation State Management:**
- Conversations table: user_id, conversation_id, created_at, updated_at
- Messages table: conversation_id, role (user/assistant), content, created_at
- Conversation history loaded from database on each request
- Message history passed to AI agent with each turn
- Conversation lifecycle: create → append messages → retrieve history

**Natural Language Processing:**
- AI agent interprets user intent from natural language
- Agent selects appropriate MCP tools based on intent
- Agent can chain multiple tool calls in single response
- Agent provides friendly confirmations for actions taken
- Agent handles ambiguity by asking clarifying questions

### Technology Stack (Phase III)

**AI Framework:**
- OpenAI Agents SDK for agent orchestration
- OpenAI API (GPT-4 or Claude via OpenAI-compatible endpoint)
- Async/await pattern for all agent operations

**MCP Server:**
- Official MCP SDK (Python)
- Tools defined with JSON schemas
- HTTP/stdio transport for tool invocation
- Integrated with FastAPI backend

**Frontend:**
- OpenAI ChatKit for conversational UI
- Domain allowlist configured for production deployment
- Message streaming for real-time responses
- Markdown rendering for agent responses

**Backend:**
- Phase II stack (FastAPI + SQLAlchemy + Neon)
- New endpoints: POST /api/chat, GET /api/conversations
- Async message processing
- Token usage tracking and limits

### Code Quality Standards (Phase III)

**Agent Integration:**
- Agent behavior documented in spec (intent mapping → tool calls)
- Agent prompts versioned and tested
- Fallback behavior for agent failures
- Rate limiting on chat endpoints
- Token budget management

**Testing:**
- Unit tests for MCP tools
- Integration tests for agent → tool → database flow
- Conversation flow tests (multi-turn scenarios)
- Edge case handling (malformed input, missing context)

**Security:**
- User_id validation on all MCP tools
- Conversation ownership validation
- Input sanitization for AI-generated content
- Rate limiting to prevent abuse
- Token usage monitoring

## Evolutionary Architecture Roadmap

### Phase I: Monolithic Script ✅ COMPLETED
**Goal**: Validate core CRUD functionality with minimal complexity
**Duration**: Single feature implementation
**Architecture**: Single Python file with layered structure (Model/Logic/Presentation)
**Technology**: Python 3.13+ standard library only
**Storage**: In-memory (dict/list)
**Interface**: CLI menu-driven loop
**Deployment**: Local execution (`python src/main.py`)
**Success Criteria**: All CRUD operations working with error handling

### Phase II: Modular Monolith ✅ COMPLETED
**Goal**: Add persistence, web UI, and API layer while maintaining modularity
**Architecture**: Separate frontend/backend with clear module boundaries
**Technology**: Next.js (frontend) + FastAPI (backend) + Neon PostgreSQL (database)
**Storage**: Neon (PostgreSQL) with migrations
**Interface**: Web UI (Next.js React components) + REST API (FastAPI endpoints)
**Deployment**: Vercel (frontend) + Cloud provider (backend) + Neon (database)
**Success Criteria**: Web CRUD with persistence, authentication, multi-user support ✅
**Migration Path**: Extract TaskManager logic → FastAPI endpoints, build Next.js UI consuming API ✅

### Phase III: Agent-Augmented System ⚙️ CURRENT
**Goal**: Integrate AI agents for intelligent task management and assistance
**Architecture**: Phase II stack + AI agent layer + MCP integration
**Technology**: Phase II stack + AI Agents (Claude, GPT) + MCP (Model Context Protocol)
**Storage**: Phase II storage + agent conversation history
**Interface**: Phase II UI + agent chat interface + MCP tools
**Deployment**: Phase II deployment + agent orchestration layer
**Success Criteria**: AI agents can create/update/prioritize tasks, natural language input, MCP tool integration
**Migration Path**: Add agent endpoints to FastAPI, integrate MCP, build agent UI components

### Phase IV: Microservices
**Goal**: Decompose monolith into independently deployable services
**Architecture**: Task Service, User Service, Agent Service, Notification Service (independent microservices)
**Technology**: Phase III stack + Kubernetes + Helm charts + Service mesh
**Storage**: Database per service pattern (separate schemas/databases)
**Interface**: API Gateway + Phase III UI (consuming multiple services)
**Deployment**: Kubernetes cluster with Helm charts, auto-scaling, health checks
**Success Criteria**: Services independently deployable, fault-tolerant, scalable
**Migration Path**: Extract bounded contexts → separate services, deploy to K8s, implement service discovery

### Phase V: Event-Driven Architecture
**Goal**: Achieve cloud-native architecture with event streaming and eventual consistency
**Architecture**: Event-driven microservices with Kafka backbone + Dapr runtime
**Technology**: Phase IV stack + Kafka (event streaming) + Dapr (service mesh) + Cloud-native services
**Storage**: Event store (Kafka) + CQRS pattern (read/write separation)
**Interface**: Phase IV UI + real-time event-driven updates
**Deployment**: Multi-cloud Kubernetes + Kafka cluster + Dapr sidecars
**Success Criteria**: Event sourcing, CQRS, real-time collaboration, multi-cloud deployment
**Migration Path**: Implement event sourcing, add Kafka backbone, refactor to CQRS, deploy Dapr sidecars

## Development Workflow

### Specification (All Phases)
1. Write feature specification in `specs/<feature>/spec.md`
2. Define user stories with priorities (P1, P2, P3)
3. List functional requirements (FR-001, FR-002, etc.)
4. Define success criteria (SC-001, SC-002, etc.)
5. Get stakeholder approval before proceeding

### Planning (All Phases)
1. Run `/sp.plan` to generate implementation plan
2. Verify Constitution Check passes (phase-specific constraints)
3. Define data structures (appropriate for current phase storage)
4. Design interfaces (CLI for Phase I, API for Phase II+)
5. Identify edge cases and error scenarios
6. Document phase-appropriate architecture decisions in ADRs

### Task Generation (All Phases)
1. Run `/sp.tasks` to generate actionable task list
2. Tasks organized by user story priority
3. Each task includes exact file path and acceptance criteria
4. Foundational tasks (setup, infrastructure) before user stories
5. User stories can be implemented independently

### Implementation (All Phases)
1. Run `/sp.implement` to execute tasks
2. Implement in priority order (P1 → P2 → P3)
3. Test each user story independently before proceeding
4. Commit after completing each user story
5. Validate against spec acceptance criteria

### Validation (All Phases)
1. Testing appropriate to phase (manual for Phase I, automated for Phase II+)
2. Edge case validation
3. Error handling verification
4. Performance check (phase-appropriate benchmarks)
5. Update documentation (specs, ADRs, README)

## Phase Transition Rules

### Transition Trigger Conditions
A phase transition can ONLY occur when:
1. All planned features for current phase are complete
2. All acceptance criteria validated
3. Technical debt addressed or documented
4. Migration strategy documented in ADR
5. Updated constitution ratified (new MAJOR version)

### Transition Process
1. **Assessment**: Review current phase completeness
2. **Planning**: Draft migration ADR with strategy and risks
3. **Constitution Update**: Amend constitution for next phase (MAJOR version bump)
4. **Specification**: Write migration spec detailing transition steps
5. **Implementation**: Execute migration tasks (data, code, infrastructure)
6. **Validation**: Verify all Phase N features still work in Phase N+1
7. **Commit**: Tag release marking phase transition

### Backward Compatibility
- User-facing features MUST remain functional during transitions
- Data migration MUST preserve all existing data
- Breaking API changes require versioning (v1 → v2)
- Deprecation warnings for removed features (at least one phase notice)

## Governance

### Amendment Process
1. Proposed changes documented in constitution update commit
2. Version number incremented following semantic versioning:
   - **MAJOR**: Phase transition, backward-incompatible governance changes, principle removal/redefinition
   - **MINOR**: New principles added, materially expanded guidance (within same phase)
   - **PATCH**: Clarifications, wording improvements, typo fixes, non-semantic refinements
3. All dependent templates reviewed and updated
4. Team approval required before merge
5. Changes tracked in Sync Impact Report

### Compliance Verification
- All code reviews MUST verify constitution compliance
- Phase-appropriate constraints MUST be enforced during planning
- Constitution violations require explicit justification in Complexity Tracking section of plan.md
- Unjustified violations result in change request
- No premature introduction of future-phase technologies

### Constitution Supersedes Defaults
- When constitution conflicts with standard practices, constitution wins
- Agents MUST follow constitution rules exactly as written
- Constitution takes precedence over internal knowledge or assumptions
- Phase constraints are non-negotiable (cannot skip or merge phases)

### Living Document
- Constitution evolves with project phases
- Changes tracked in version history and Sync Impact Report
- Each phase transition updates constitution (MAJOR version)
- Principles remain consistent; constraints evolve per phase

### Architecture Decision Records (ADRs)
- Significant technical decisions MUST be documented in ADRs
- Phase transitions require migration ADR
- Technology stack changes require justification ADR
- ADRs stored in `history/adr/` directory
- ADR format: Context, Decision, Consequences, Alternatives Considered

**Version**: 3.0.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-29
