# AGENTS.md

## Purpose

This project uses **Spec-Driven Development (SDD)** — a workflow where **no agent is allowed to write code until the specification is complete and approved**.

All AI agents (Claude Code, Copilot, Gemini, local LLMs, etc.) must follow the **Spec-Kit lifecycle**:

> **Specify → Plan → Tasks → Implement**

This prevents "vibe coding," ensures alignment across agents, and guarantees that every implementation step maps back to an explicit requirement.

---

## How Agents Must Work

Every agent in this project MUST obey these rules:

1. **Never generate code without a referenced Task ID.**
2. **Never modify architecture without updating the plan.**
3. **Never propose features without updating the spec (WHAT).**
4. **Never change approach without updating constitution (Principles).**
5. **Every code file must contain a comment linking it to the Task and Spec sections.**

If an agent cannot find the required spec, it must **stop and request it**, not improvise.

---

## Spec-Kit Workflow (Source of Truth)

### 1. Constitution (WHY — Principles & Constraints)

**File**: `.specify/memory/constitution.md`

Defines the project's non-negotiables: architecture values, security rules, tech stack constraints, performance expectations, and patterns allowed.

**Agents must check this before proposing solutions.**

**Current Phase**: Phase I - Monolithic Script
- Python 3.13+ standard library only
- In-memory storage only
- CLI menu-driven interface
- No external dependencies

---

### 2. Specify (WHAT — Requirements, Journeys & Acceptance Criteria)

**File**: `specs/<feature>/spec.md`

Contains:
- User journeys
- Requirements (FR-XXX format)
- Acceptance criteria (SC-XXX format)
- Domain rules
- Business constraints

**Agents must not infer missing requirements** — they must request clarification or propose specification updates.

---

### 3. Plan (HOW — Architecture, Components, Interfaces)

**File**: `specs/<feature>/plan.md`

Includes:
- Component breakdown
- APIs & schema diagrams
- Service boundaries
- System responsibilities
- High-level sequencing

**All architectural output MUST be generated from the Specify file.**

---

### 4. Tasks (BREAKDOWN — Atomic, Testable Work Units)

**File**: `specs/<feature>/tasks.md`

Each Task must contain:
- Task ID (T-XXX format)
- Clear description
- Preconditions
- Expected outputs
- Artifacts to modify
- Links back to Specify + Plan sections

**Agents implement only what these tasks define.**

---

### 5. Implement (CODE — Write Only What the Tasks Authorize)

Agents now write code, but must:
- Reference Task IDs in code comments
- Follow the Plan exactly
- Not invent new features or flows
- Stop and request clarification if anything is underspecified

> **The golden rule: No task = No code.**

---

## Phase-Specific Agent Behavior

### Phase I: Monolithic Script (CURRENT)
**Constraints**:
- Use only Python standard library
- In-memory storage only (dict/list)
- Single file in `src/main.py`
- CLI menu-driven loop

**Agent Must**:
- Reject any external pip packages
- Reject any persistence mechanisms
- Use type hints for all functions
- Include Google-style docstrings

---

### Phase II: Full-Stack Web Application (FUTURE)
**New Technologies**:
- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel
- Auth: Better Auth with JWT

**Agent Must**:
- Create monorepo structure (frontend/ and backend/)
- Implement RESTful API endpoints
- Add authentication to all endpoints
- Follow separation of concerns

---

### Phase III: AI-Powered Chatbot (FUTURE)
**New Technologies**:
- OpenAI ChatKit (frontend)
- OpenAI Agents SDK (backend)
- Official MCP SDK (tool server)

**Agent Must**:
- Build stateless MCP tools
- Persist conversation state to database
- Implement natural language command parsing
- Create chat endpoint with conversation history

---

### Phase IV: Local Kubernetes Deployment (FUTURE)
**New Technologies**:
- Docker & Docker Compose
- Kubernetes (Minikube)
- Helm Charts
- kubectl-ai, kagent

**Agent Must**:
- Create Dockerfiles for each service
- Write Kubernetes manifests
- Create Helm charts
- Document deployment steps

---

### Phase V: Advanced Cloud Deployment (FUTURE)
**New Technologies**:
- Kafka or Redpanda (event streaming)
- Dapr (distributed runtime)
- Cloud providers (DigitalOcean DOKS, GKE, or AKS)

**Agent Must**:
- Implement event-driven architecture
- Use Dapr building blocks (Pub/Sub, State, Bindings, Secrets)
- Deploy to production Kubernetes cluster
- Set up CI/CD pipeline

---

## Agent Behavior in This Project

### When generating code:

Agents must reference:

```
[Task]: T-001
[From]: specs/001-todo-crud/spec.md §2.1, specs/001-todo-crud/plan.md §3.4
```

### When proposing architecture:

Agents must reference:

```
Update required in specs/<feature>/plan.md → add component X
```

### When proposing new behavior or a new feature:

Agents must reference:

```
Requires update in specs/<feature>/spec.md (WHAT)
```

### When changing principles:

Agents must reference:

```
Modify .specify/memory/constitution.md → Principle #X
```

---

## Agent Failure Modes (What Agents MUST Avoid)

Agents are NOT allowed to:

- Freestyle code or architecture
- Generate missing requirements
- Create tasks on their own
- Alter stack choices without justification
- Add endpoints, fields, or flows that aren't in the spec
- Ignore acceptance criteria
- Produce "creative" implementations that violate the plan
- **Skip phases or introduce future-phase technologies prematurely**

If a conflict arises between spec files, the **Constitution > Specify > Plan > Tasks** hierarchy applies.

---

## Developer–Agent Alignment

Humans and agents collaborate, but the **spec is the single source of truth**.

Before every session, agents should re-read:

1. `.specify/memory/constitution.md` - Current phase constraints
2. `specs/<feature>/spec.md` - What to build
3. `specs/<feature>/plan.md` - How to build it
4. `specs/<feature>/tasks.md` - Step-by-step breakdown

This ensures predictable, deterministic development.

---

## Available Slash Commands

Agents can use these commands to manage the spec-driven workflow:

- `/sp.constitution` - Create or update project constitution
- `/sp.specify` - Create feature specification
- `/sp.plan` - Generate implementation plan
- `/sp.tasks` - Generate actionable task list
- `/sp.implement` - Execute tasks
- `/sp.clarify` - Identify underspecified areas
- `/sp.analyze` - Cross-artifact consistency analysis
- `/sp.checklist` - Generate custom checklist
- `/sp.adr` - Create Architectural Decision Record
- `/sp.phr` - Create Prompt History Record
- `/sp.git.commit_pr` - Git workflow automation

---

## Available Skills

Agents can invoke specialized skills for complex operations:

### Phase Management
- `phase-transition` - Guide phase upgrade with validation
- `phase-validator` - Validate current phase compliance

### Infrastructure
- `kubernetes-setup` - Set up Kubernetes environment (Phase IV)
- `docker-builder` - Create optimized Dockerfiles
- `helm-chart-generator` - Generate Helm charts

### AI & MCP
- `mcp-builder` - Build MCP servers from slash commands
- `agent-builder` - Create OpenAI Agents SDK agents
- `chatkit-setup` - Configure OpenAI ChatKit frontend

### Cloud & DevOps
- `cloud-deployment` - Deploy to cloud Kubernetes
- `dapr-integration` - Add Dapr building blocks
- `kafka-setup` - Configure Kafka/Redpanda
- `cicd-pipeline` - Generate GitHub Actions workflows

### Development
- `test-generator` - Generate test suites
- `api-documentation` - Generate OpenAPI/Swagger docs
- `migration-builder` - Create database migrations

---

## Hackathon-Specific Rules

### Submission Requirements
1. **No Manual Coding**: All code MUST be generated via Claude Code using spec-driven workflow
2. **Prompt History Records**: Create PHR after every major user interaction
3. **ADRs for Decisions**: Document architectural decisions in `history/adr/`
4. **Spec Review**: Judges review specs, prompts, and iteration history
5. **Demo Video**: 90 seconds max showing spec → implementation flow

### Bonus Points Strategy
- **+200 pts**: Create reusable agents and skills
- **+200 pts**: Use Cloud-Native Blueprints via Agent Skills
- **+100 pts**: Multi-language support (Urdu chatbot)
- **+200 pts**: Voice commands for todo operations

### Best Practices
- Start each phase with `/sp.specify`
- Always run `/sp.plan` before implementing
- Use `/sp.tasks` to break down work
- Create PHRs with `/sp.phr` after completing features
- Document decisions with `/sp.adr`
- Commit with `/sp.git.commit_pr` when ready

---

## MCP Server Integration

This project can be enhanced with an MCP server that exposes all slash commands as prompts.

**Setup Process**:
1. Use the `mcp-builder` skill
2. Convert `.claude/commands/**` to MCP prompts
3. Register MCP server in `.mcp.json`
4. Test with any MCP-compatible IDE

**Benefit**: Reusable spec-driven workflow across all AI development tools.

---

## Constitution Compliance

**When in doubt, agents MUST**:
1. Check `.specify/memory/constitution.md` for current phase
2. Verify technology stack compliance
3. Confirm storage constraints
4. Validate interface requirements
5. Ask user if still uncertain

**Violations result in**:
- Rejected code changes
- Request to update spec/plan/tasks
- Constitution amendment proposal

---

**Version**: 1.0.0
**Created**: 2025-12-13
**Project**: Evolution of TODO - PIAIC Hackathon II
**Phases**: I (Current) → II → III → IV → V
