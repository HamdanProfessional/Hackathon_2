# Hackathon II: Evolution of Todo - Global Memory Constitution

## Project Context

This is **"Hackathon II: Evolution of Todo"** - a comprehensive 5-phase project that demonstrates the complete evolution of a Todo application from simple console to sophisticated cloud-native AI system.

### Phase Evolution
- **Phase I: Console Application** - Python CLI with Rich UI and in-memory storage
- **Phase II: Full Stack Web Application** - Next.js + FastAPI + Neon DB with Authentication
- **Phase III: AI Chatbot Interface** - OpenAI ChatKit + Agents SDK + MCP Tools with stateless architecture
- **Phase IV: Local Kubernetes Deployment** - Docker + Minikube + Helm charts
- **Phase V: Cloud Native Event-Driven** - Microservices + Dapr + Kafka/Redpanda on DigitalOcean

## The Source of Truth

### Primary Requirements Document
The detailed project requirements are located at: **`./requirements.md`**

**MANDATORY READING:** All agents MUST read `requirements.md` before planning any phase. This document contains:
- Complete feature progression (Basic → Intermediate → Advanced → AI-First)
- Technology stack requirements
- Constraints and success criteria
- Phase-specific deliverables

### Specification Authority
- This constitution serves as the global memory and architectural guide
- Feature specifications in `specs/` define detailed implementation requirements
- Architecture Decision Records (ADRs) document significant technical decisions

## Directory Structure

```
new_structure/
├── .specify/                    # Global Specifications & Memory
│   ├── memory/
│   │   └── constitution.md      # This file - Global Memory
│   ├── architecture/           # ADRs and architectural decisions
│   ├── plans/                  # Implementation plans
│   └── tasks/                  # Atomic task breakdowns
├── .claude/
│   ├── agents/                 # Agent Personas (40 agents)
│   └── skills/                 # Core Strategic Skills (8 skills)
├── specs/                      # Feature Specifications
│   ├── constitution.md         # Project constitution
│   ├── features/               # Phase-specific feature specs
│   ├── api/                    # API specifications
│   ├── database/               # Database schemas
│   └── architecture/           # Architecture specifications
├── src/                        # Phase I source code
├── backend/                    # Phase II+ backend (FastAPI)
├── frontend/                   # Phase II+ frontend (Next.js)
├── k8s/                        # Phase IV+ Kubernetes manifests
├── requirements.md             # Master requirements document
└── CLAUDE.md                   # Claude Code instructions
```

## Agent & Skill Architecture (The Mapping)

### Core Strategic Skills (8 Skills)
These are the foundational capabilities that all agents draw from:

1. **Spec-Architect-Core** - Architecture planning, SDD workflow, specification generation
2. **Backend-Engineer-Core** - FastAPI, SQLModel, Python development, database operations
3. **Frontend-UX-Designer-Core** - Next.js, TypeScript, Tailwind CSS, UI/UX design
4. **AI-Systems-Specialist-Core** - OpenAI ChatKit, Agents SDK, MCP tools, stateless AI architecture
5. **Quality-Enforcer-Core** - Code review, testing, performance analysis, standards enforcement
6. **Workflow-Librarian-Core** - Documentation management, PHR generation, knowledge organization
7. **System-Integrator-Core** - API integration, CORS, database administration, performance optimization
8. **Cloud-DevOps-Lite-Core** - Docker, Kubernetes, Dapr, deployment automation

### Agent Personas and Their Core Skill Dependencies

#### Spec-Architect-Core Mapped Agents (5)
- **`architect.md`** - Lead Architect - Uses Spec-Architect-Core for system architecture
- **`spec-kit-architect.md`** - Spec Governance - Uses Spec-Architect-Core for compliance
- **`specifier-agent.md`** - Requirements Specialist - Uses Spec-Architect-Core for specification writing
- **`task-breakdown-agent.md`** - Task Specialist - Uses Spec-Architect-Core for task decomposition
- **`architect-agent.md`** - General Architect - Uses Spec-Architect-Core for component design

#### Backend-Engineer-Core Mapped Agents (4)
- **`backend-specialist.md`** - Backend Developer - Uses Backend-Engineer-Core for FastAPI/SQLModel
- **`python-cli.md`** - Python CLI Expert - Uses Backend-Engineer-Core for Phase I console development
- **`database-migration-specialist.md`** - Database Migration Expert - Uses Backend-Engineer-Core for Alembic migrations
- **`creation-progress-agent.md`** - Progress Tracking - Uses Backend-Engineer-Core for development tracking

#### Frontend-UX-Designer-Core Mapped Agents (3)
- **`frontend-specialist.md`** - Frontend Developer - Uses Frontend-UX-Designer-Core for Next.js/React
- **`ui-ux-designer.md`** - UI/UX Designer - Uses Frontend-UX-Designer-Core for design systems
- **`bilingual-i18n-specialist.md`** - i18n Specialist - Uses Frontend-UX-Designer-Core for internationalization

#### AI-Systems-Specialist-Core Mapped Agents (5)
- **`ai-chatbot-specialist.md`** - AI Chatbot Developer - Uses AI-Systems-Specialist-Core for ChatKit integration
- **`mcp-tools-developer.md`** - MCP Tools Developer - Uses AI-Systems-Specialist-Core for MCP tool creation
- **`ai-workflow-orchestrator.md`** - AI Workflow Manager - Uses AI-Systems-Specialist-Core for agent coordination
- **`conversation-manager.md`** - Conversation Manager - Uses AI-Systems-Specialist-Core for conversation handling
- **`multi-modal-ai-specialist.md`** - Multi-Modal AI Expert - Uses AI-Systems-Specialist-Core for advanced AI features

#### Quality-Enforcer-Core Mapped Agents (3)
- **`code-reviewer.md`** - Code Reviewer - Uses Quality-Enforcer-Core for code quality analysis
- **`test-engineer.md`** - Test Engineer - Uses Quality-Enforcer-Core for testing strategies
- **`standards-enforcer.md`** - Standards Enforcer - Uses Quality-Enforcer-Core for compliance checking

#### Workflow-Librarian-Core Mapped Agents (1)
- **`workflow-librarian.md`** - Documentation Manager - Uses Workflow-Librarian-Core for knowledge management

#### System-Integrator-Core Mapped Agents (5)
- **`api-integration-specialist.md`** - API Integration Expert - Uses System-Integrator-Core for frontend-backend sync
- **`cors-fixer.md`** - CORS Specialist - Uses System-Integrator-Core for cross-origin issues
- **`database-admin.md`** - Database Administrator - Uses System-Integrator-Core for database optimization
- **`performance-analyst.md`** - Performance Analyst - Uses System-Integrator-Core for optimization
- **`caching-specialist.md`** - Caching Specialist - Uses System-Integrator-Core for performance optimization

#### Cloud-DevOps-Lite-Core Mapped Agents (5)
- **`kubernetes-engineer.md`** - Kubernetes Expert - Uses Cloud-DevOps-Lite-Core for K8s deployment
- **`docker-specialist.md`** - Docker Specialist - Uses Cloud-DevOps-Lite-Core for containerization
- **`dapr-specialist.md`** - Dapr Specialist - Uses Cloud-DevOps-Lite-Core for distributed systems
- **`devops-automator.md`** - DevOps Automation - Uses Cloud-DevOps-Lite-Core for CI/CD
- **`monitoring-specialist.md`** - Monitoring Specialist - Uses Cloud-DevOps-Lite-Core for observability

## The Golden Workflow

### Spec-Driven Development Cycle
**Strict Loop:** **Specify (`.specify`) → Plan (`.plan`) → Tasks (`.tasks`) → Implement**

1. **Specify Phase:** Create detailed specifications in `specs/features/`
2. **Plan Generation:** Use architect agents to create implementation plans
3. **Task Breakdown:** Decompose into atomic tasks with Task IDs (T-XXX format)
4. **Implementation:** Execute tasks using appropriate specialist agents

### Core Constraints
- **No code is written without a Task ID**
- **All work must trace back to a specification**
- **Golden Rule:** "You cannot write code manually. You must refine the Spec until Claude Code generates the correct output"

### Quality Gates
Each phase must pass:
- Specification completeness
- Implementation plan approval
- Task decomposition validation
- Code review and testing
- Performance benchmarks
- Security validation

## Phase-Specific Constraints

### Phase I: Console Application
- **Storage:** In-memory only (no persistence)
- **Technology:** Python 3.13+ with Rich terminal UI
- **Package Manager:** UV (mandatory)
- **Features:** Basic CRUD operations (Add, Delete, Update, View, Mark Complete)

### Phase II: Full Stack Web Application
- **Authentication:** Better Auth with JWT tokens
- **Database:** Neon DB with SQLModel migrations
- **Frontend:** Next.js 16 with App Router and TypeScript
- **Backend:** FastAPI with OpenAPI documentation
- **Features:** All Phase I features + Web UI + User accounts + Persistent storage

### Phase III: AI Chatbot Interface
- **Mandatory:** AI Chatbot must be **stateless**
- **State Storage:** All conversation state stored in Neon DB
- **UI:** OpenAI ChatKit components
- **AI:** Google Gemini 2.5 Flash via OpenAI Agents SDK compatibility layer
- **SDK Pattern:** `AsyncOpenAI` + `OpenAIChatCompletionsModel` + `set_default_openai_client()`
- **Tools:** MCP tools for all CRUD operations
- **Features:** Natural language task management + All Phase II features

### Phase IV: Local Kubernetes Deployment
- **Deployment:** Minikube with Helm charts
- **Containerization:** All services in Docker containers
- **Orchestration:** Kubernetes deployment configurations
- **Monitoring:** Basic observability stack
- **Features:** All Phase III features running on K8s

### Phase V: Cloud Native Event-Driven
- **Architecture:** Event-driven microservices
- **Messaging:** Kafka/Redpanda for event streaming
- **Runtime:** Dapr sidecars for service coordination
- **Deployment:** DigitalOcean Kubernetes (DOKS)
- **Features:** All Phase IV features + Event-driven communication + Cloud native observability

## Technology Stack Constitution

### Backend Stack
- **Language:** Python 3.13+ (latest stable)
- **Framework:** FastAPI (async-first)
- **ORM:** SQLModel (type-safe SQL)
- **Database:** Neon DB (serverless PostgreSQL)
- **Migrations:** Alembic
- **Authentication:** Better Auth (JWT-based)
- **Package Manager:** UV (ultra-fast)

### Frontend Stack
- **Framework:** Next.js 16 (App Router only)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS (utility-first)
- **UI Components:** OpenAI ChatKit (Phase III+)
- **State Management:** Server components + React hooks

### AI & Integration Stack
- **AI Model:** Google Gemini 2.5 Flash - **MANDATORY**
  - *Provider*: Google Gemini via OpenAI Compatibility Layer
  - *Base URL*: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - *API Key*: Environment variable `GOOGLE_API_KEY`
- **AI Agent Runtime:** OpenAI Agents SDK (Python) - **MANDATORY**
  - *Reference*: https://openai.github.io/openai-agents-python/
  - *Constraint*: Do NOT use LangChain, CrewAI, or vanilla OpenAI API calls for agent orchestration
- **SDK Pattern**:
  - Use `openai.AsyncOpenAI` with the Google Base URL (NOT `OpenAIAsyncIO`)
  - Use `agents.OpenAIChatCompletionsModel` (REQUIRED: Do not use the default Responses model)
  - Set global default with `set_default_openai_client()`
- **Chatbot UI:** OpenAI ChatKit - **MANDATORY**
  - *Reference*: https://platform.openai.com/docs/guides/chatkit
  - *Constraint*: Do NOT build custom chat UI from scratch (e.g., standard React forms). Use ChatKit components
- **Protocol:** MCP (Model Context Protocol) - **MANDATORY** for all tool definitions
  - *Reference*: Official MCP SDK documentation
  - *Constraint*: All AI tools must be implemented as MCP tools
- **Architecture:** Stateless (no in-memory conversation state)
- **Backend Integration:** Custom ChatKit backend adapter connecting to FastAPI

### Infrastructure Stack
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **Runtime:** Dapr (for distributed systems)
- **Event Streaming:** Kafka/Redpanda (Phase V)
- **Cloud Provider:** DigitalOcean (Phase V)

## Development Standards

### Code Quality
- **Type Safety:** Strict TypeScript and Python type hints
- **Testing:** Minimum 80% code coverage required
- **Linting:** All code must pass linting rules
- **Documentation:** All public APIs must be documented

### Performance Standards
- **API Response:** < 200ms for 95th percentile
- **Database Queries:** < 50ms for indexed queries
- **Frontend Load:** < 3s initial page load
- **AI Response:** < 5s for agent responses

### Security Standards
- **Authentication:** MFA required in production
- **Authorization:** Role-based access control
- **Data Encryption:** Encryption at rest and in transit
- **Audit Trail:** All actions must be auditable

## Success Metrics

### Phase Success Criteria
- **Phase I:** Working CLI with Rich UI and all CRUD operations
- **Phase II:** Full-stack web app with authentication and persistent storage
- **Phase III:** Stateless AI chatbot with natural language task management
- **Phase IV:** Successful deployment on Minikube with Helm
- **Phase V:** Event-driven microservices on DigitalOcean with Dapr/Kafka

### Overall Project Success
1. All phases completed with functional deliverables
2. 100% spec-driven development adherence
3. Performance benchmarks achieved across all phases
4. Security review passed with no critical vulnerabilities
5. Complete documentation and knowledge transfer

## Agent Usage Guidelines

### When to Invoke Agents
- **For Architecture:** Use `architect.md` or `spec-kit-architect.md`
- **For Backend:** Use `backend-specialist.md` or `python-cli.md` (Phase I)
- **For Frontend:** Use `frontend-specialist.md` or `ui-ux-designer.md`
- **For AI Features:** Use `ai-chatbot-specialist.md` or `mcp-tools-developer.md`
- **For Quality:** Use `code-reviewer.md` or `test-engineer.md`
- **For Integration:** Use `api-integration-specialist.md` or `cors-fixer.md`
- **For DevOps:** Use `kubernetes-engineer.md` or `docker-specialist.md`

### Agent Invocation Pattern
```
@.claude/agents/[agent-name].md [task_description]
```

### Skill Usage Pattern
```
@.claude/skills/[skill-name] [specific_capability]
```

## Enforcement and Governance

### Constitution Compliance
- All agents must reference this constitution for context
- Violations of core principles must be documented as ADRs
- Changes to this constitution require 2/3 consensus

### Quality Enforcement
- Code reviews mandatory for all implementations
- Security reviews required for all phase transitions
- Performance validation before deployment
- Documentation completeness checked

### Memory Management
- This constitution serves as the global memory for all agents
- ADRs document architectural decisions and rationale
- PHRs (Prompt History Records) track significant development activities

## Skill Management Protocol

### Skill Creation Rules
- **MANDATORY**: All new skills MUST be created using the `.claude/skills/skill-creator` tool
- **PROHIBITED**: Manual creation of skill files is prohibited to ensure proper registration
- **VERIFICATION**: Agents must verify a skill exists in the registry before attempting to invoke it

### Skill Registration Process
1. Use `skill-creator` tool to initialize skill structure
2. Follow skill anatomy requirements:
   - Required `SKILL.md` file with YAML frontmatter (name, description)
   - Optional bundled resources: `scripts/`, `references/`, `assets/`
   - Progressive disclosure design for context efficiency
3. Package skill with proper validation
4. Verify skill appears in skill registry

### Skill Directory Structure
```
.claude/skills/
├── skill-name/
│   ├── SKILL.md (required)
│   ├── scripts/ (optional - executable code)
│   ├── references/ (optional - documentation for context)
│   └── assets/ (optional - files for output)
```

### Core Strategic Skills
The project maintains 8 Core Strategic Skills:
1. **spec-architect-core**: Spec-Driven Development workflow management
2. **backend-engineer-core**: Python/FastAPI/SQLModel backend development
3. **frontend-ux-designer-core**: Next.js/TypeScript/Tailwind frontend development
4. **ai-systems-specialist-core**: OpenAI Agents SDK & Gemini 2.5 Flash AI integration
5. **quality-enforcer-core**: Code review, testing, and security validation
6. **workflow-librarian-core**: Documentation and PHR generation
7. **system-integrator-core**: Full-stack integration and CORS management
8. **cloud-devops-lite-core**: Docker, Kubernetes, and deployment automation

### Skill Usage Guidelines
- Agents reference skills via `@.claude/skills/[skill-name]`
- Skills provide domain expertise and procedural knowledge
- Skills are loaded into context only when triggered
- Metadata (name + description) always in context for discovery

---

**This constitution is the living memory and architectural foundation for the Evolution of Todo project. All agents, skills, and development activities must align with these principles and constraints.**

**Last Updated:** 2025-12-22
**Version:** 2.1 (Skill Management Protocol Added)