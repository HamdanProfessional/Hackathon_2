# Evolution of TODO - Agent System

A comprehensive multi-agent system for spec-driven development across all hackathon phases.

---

## 🤖 What is the Agent System?

This project uses **specialized AI agents** (subagents) that work together to build the Evolution of TODO application through all 5 phases. Each agent has specific expertise and responsibilities.

**Benefits**:
- **+200 Bonus Points**: Reusable intelligence via agents/subagents
- **Specialization**: Each agent is an expert in their domain
- **Collaboration**: Agents hand off work to each other
- **Consistency**: Same workflow every time
- **Quality**: Built-in best practices

---

## 📊 Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                           │
│                (agent-orchestrator.yaml)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬────────────────┐
        │                │                │                │
┌───────▼────────┐ ┌────▼─────┐ ┌────────▼───────┐ ┌─────▼──────┐
│  Spec Workflow │ │  Phase   │ │ Infrastructure │ │   AI/MCP   │
│     Agents     │ │Developer │ │     Agents     │ │   Agents   │
│                │ │  Agents  │ │                │ │            │
│ • specifier    │ │ • phase-i│ │ • k8s-engineer │ │ • mcp-arch │
│ • architect    │ │ • phase-ii│ │ • cloud-arch  │ │ • agent-dev│
│ • task-break   │ │ • phase-iii│ │ • devops     │ │            │
│ • implementer  │ │ • phase-iv│ │                │ │            │
└────────────────┘ │ • phase-v│ └────────────────┘ └────────────┘
                   └──────────┘
        ┌────────────────┴────────────────┐
┌───────▼────────┐              ┌─────────▼────────┐
│    Quality     │              │   Specialized    │
│    Agents      │              │     Agents       │
│                │              │                  │
│ • code-reviewer│              │ • doc-generator  │
│ • tester       │              │ • diagram-maker  │
└────────────────┘              └──────────────────┘
```

---

## 🗂️ Agent Categories

### 1. Spec-Workflow Agents
**Purpose**: Execute the spec-driven development workflow

| Agent | Subagent Type | Expertise | Output |
|-------|---------------|-----------|--------|
| **Specifier** | `specifier` | Requirements, user stories | `spec.md` |
| **Architect** | `architect` | System design, planning | `plan.md` |
| **Task Breakdown** | `task-breakdown` | Task decomposition | `tasks.md` |
| **Implementer** | `implementer` | Code generation | Source code |

**Workflow**:
```
User Request → Specifier → Architect → Task Breakdown → Implementer → Code
```

---

### 2. Phase-Specific Developers
**Purpose**: Implement features according to phase constraints

| Agent | Phase | Technology Stack |
|-------|-------|-----------------|
| **Phase I Developer** | I | Python CLI, stdlib only |
| **Phase II Full-Stack** | II | Next.js, FastAPI, Neon |
| **Phase III AI Dev** | III | OpenAI Agents, MCP |
| **Phase IV K8s Dev** | IV | Docker, Kubernetes |
| **Phase V Cloud Dev** | V | Kafka, Dapr, Cloud |

**Phase Progression**:
```
Phase I (CLI) → Phase II (Web) → Phase III (AI) → Phase IV (K8s) → Phase V (Cloud)
```

---

### 3. Infrastructure Agents
**Purpose**: Handle deployment and infrastructure

| Agent | Expertise | Phase |
|-------|-----------|-------|
| **K8s Engineer** | Docker, Kubernetes, Helm | IV-V |
| **Cloud Architect** | Cloud deployment, scaling | V |
| **DevOps Engineer** | CI/CD, monitoring | IV-V |

---

### 4. AI & MCP Agents
**Purpose**: Build AI and MCP integrations

| Agent | Expertise | Phase |
|-------|-----------|-------|
| **MCP Architect** | MCP tools, protocol | III+ |
| **Agent Developer** | OpenAI Agents SDK | III+ |
| **Chatbot Builder** | Conversation UX | III+ |

---

### 5. Quality Assurance Agents
**Purpose**: Ensure code quality and correctness

| Agent | Focus | When |
|-------|-------|------|
| **Code Reviewer** | Standards, bugs | After implementation |
| **Test Generator** | Test suites | Per feature |
| **Security Auditor** | Vulnerabilities | Before deployment |

---

## 🚀 How to Use Agents

### Method 1: Via Task Tool (Programmatic)
```python
# Invoke specific agent
Task(
    subagent_type="architect",
    description="Create implementation plan",
    prompt="Design architecture for specs/001-todo-crud/spec.md following Phase I constraints"
)
```

### Method 2: Via Slash Commands
```bash
# Spec-workflow agents have slash commands
/sp.specify todo-crud
/sp.plan
/sp.tasks
/sp.implement
```

### Method 3: Via Direct Prompt
```
@architect: Create the implementation plan for todo CRUD

@phase-i-developer: Implement tasks T-001 through T-005

@code-reviewer: Review the implementation in src/main.py
```

### Method 4: Via Orchestrator (Automated Workflow)
```yaml
# The orchestrator runs complete workflows
workflows:
  spec-driven-development:
    - specifier
    - architect
    - task-breakdown
    - implementer
    - code-reviewer
```

---

## 📋 Complete Workflows

### Workflow 1: Spec-Driven Development
**Goal**: Build a feature from requirements to code

```
1. User Request: "Build todo CRUD operations"
   ↓
2. @specifier: Creates specs/001-todo-crud/spec.md
   - User stories
   - Acceptance criteria
   - Requirements
   ↓
3. @architect: Creates specs/001-todo-crud/plan.md
   - Component design
   - Data structures
   - Architecture
   ↓
4. @task-breakdown: Creates specs/001-todo-crud/tasks.md
   - Atomic tasks
   - Dependencies
   - Acceptance criteria
   ↓
5. @implementer: Executes tasks
   - Writes code
   - Creates tests
   - Validates acceptance criteria
   ↓
6. @code-reviewer: Reviews implementation
   - Checks constitution compliance
   - Validates quality
   - Suggests improvements
   ↓
7. Done! Feature complete
```

---

### Workflow 2: Phase Transition
**Goal**: Upgrade from Phase N to Phase N+1

```
1. User: "Transition to Phase II"
   ↓
2. @phase-validator: Validates Phase I complete
   - All features done
   - Tests passing
   - Technical debt documented
   ↓
3. @architect: Creates migration ADR
   - Documents transition rationale
   - Lists technology changes
   - Plans migration strategy
   ↓
4. @constitution-updater: Updates constitution
   - MAJOR version bump
   - New phase constraints
   - Technology stack update
   ↓
5. @specifier: Creates migration spec
   - Migration steps
   - Breaking changes
   - Success criteria
   ↓
6. @implementer: Executes migration
   - Updates code structure
   - Adds new dependencies
   - Migrates data
   ↓
7. @phase-ii-fullstack: Takes over development
   - Implements web features
   - Uses new tech stack
   ↓
8. Done! Phase II ready
```

---

## 🎯 Agent Collaboration Patterns

### Pattern 1: Sequential Handoff
One agent completes, passes artifact to next

```
Specifier → spec.md → Architect → plan.md → Task Breakdown → tasks.md → Implementer
```

### Pattern 2: Parallel Execution
Multiple agents work simultaneously

```
                    ┌→ Frontend Developer
Implementation  ────┼→ Backend Developer
                    └→ Database Designer
```

### Pattern 3: Review & Iterate
Reviewer gives feedback, implementer improves

```
Implementer → Code → Code Reviewer → Feedback → Implementer (iterate)
```

### Pattern 4: Specialist Consultation
Agent asks specialist for help

```
Implementer → Question → MCP Architect → Answer → Implementer
```

---

## 📖 Agent Invocation Examples

### Example 1: Complete Feature (Phase I)
```python
# Step 1: Create spec
Task(
    subagent_type="specifier",
    description="Create feature spec",
    prompt="Specify todo CRUD operations for Phase I CLI app"
)
# Output: specs/001-todo-crud/spec.md

# Step 2: Create plan
Task(
    subagent_type="architect",
    description="Design architecture",
    prompt="Create implementation plan from specs/001-todo-crud/spec.md"
)
# Output: specs/001-todo-crud/plan.md

# Step 3: Break into tasks
Task(
    subagent_type="task-breakdown",
    description="Generate tasks",
    prompt="Break down specs/001-todo-crud/plan.md into atomic tasks"
)
# Output: specs/001-todo-crud/tasks.md

# Step 4: Implement
Task(
    subagent_type="phase-i-developer",
    description="Implement Phase I tasks",
    prompt="Execute tasks T-001 through T-010 from specs/001-todo-crud/tasks.md"
)
# Output: src/main.py

# Step 5: Review
Task(
    subagent_type="code-reviewer",
    description="Review implementation",
    prompt="Review src/main.py for Phase I compliance and quality"
)
# Output: Review feedback
```

---

### Example 2: Build MCP Server (Phase III)
```python
# Design MCP tools
Task(
    subagent_type="mcp-architect",
    description="Design MCP tools",
    prompt="Design MCP tool schemas for todo CRUD operations"
)

# Build MCP server
Task(
    subagent_type="mcp-builder",
    description="Build MCP server",
    prompt="Convert .claude/commands to MCP server using Official SDK"
)

# Test integration
Task(
    subagent_type="agent-developer",
    description="Integrate with AI agent",
    prompt="Create OpenAI agent that uses the MCP tools"
)
```

---

### Example 3: Deploy to Kubernetes (Phase IV)
```python
# Containerize
Task(
    subagent_type="k8s-engineer",
    description="Create Dockerfiles",
    prompt="Create optimized Dockerfiles for frontend and backend"
)

# Generate K8s manifests
Task(
    subagent_type="k8s-engineer",
    description="Create K8s manifests",
    prompt="Generate Kubernetes manifests for all services"
)

# Create Helm chart
Task(
    subagent_type="k8s-engineer",
    description="Package with Helm",
    prompt="Create Helm chart for the todo application"
)

# Deploy
Task(
    subagent_type="k8s-engineer",
    description="Deploy to Minikube",
    prompt="Deploy application to local Minikube cluster"
)
```

---

## 🎓 Best Practices

### 1. Always Start with Specifier
Don't skip specification - it catches ambiguities early

### 2. Use Phase-Appropriate Agents
Phase I? Use `phase-i-developer`, not generic implementer

### 3. Let Agents Collaborate
Don't try to do everything in one agent invocation

### 4. Review After Implementation
Always run `code-reviewer` before committing

### 5. Document Decisions
Let `architect` suggest ADRs for significant choices

---

## 🏆 Hackathon Scoring

### How Agents Help You Win

**Phase Completion Points**:
- Agents ensure correct implementation per phase
- No phase constraint violations
- Clean transitions between phases

**Bonus Points (+200 each)**:
1. **Reusable Intelligence**: This entire agent system!
2. **Cloud-Native Blueprints**: K8s and cloud deployment agents

**Quality Points**:
- Code reviewer ensures high quality
- Test generator creates comprehensive tests
- No manual coding violations

---

## 📁 Directory Structure

```
.claude/agents/
├── README.md (this file)
├── agent-orchestrator.yaml
├── spec-workflow/
│   ├── specifier-agent.md
│   ├── architect-agent.md
│   ├── task-breakdown-agent.md
│   └── implementer-agent.md
├── phase-developers/
│   ├── phase-i-developer.md
│   ├── phase-ii-fullstack-developer.md
│   ├── phase-iii-ai-developer.md
│   ├── phase-iv-k8s-developer.md
│   └── phase-v-cloud-developer.md
├── infrastructure/
│   ├── kubernetes-engineer.md
│   ├── cloud-architect.md
│   └── devops-engineer.md
├── ai-mcp/
│   ├── mcp-architect.md
│   ├── agent-developer.md
│   └── chatbot-builder.md
├── quality/
│   ├── code-reviewer.md
│   ├── test-generator.md
│   └── security-auditor.md
└── specialized/
    ├── documentation-generator.md
    └── diagram-generator.md
```

---

## 🔗 Related Files

- **AGENTS.md**: Agent behavior rules and constraints
- **CLAUDE.md**: Claude Code instructions
- **.claude/skills/**: Reusable skills (complement to agents)
- **.claude/commands/**: Slash commands for workflows
- **.specify/**: Spec-Kit Plus templates

---

## 🚦 Quick Start

### Start a New Feature (Phase I)
```bash
# 1. Specify
/sp.specify my-feature

# 2. Plan
/sp.plan

# 3. Break into tasks
/sp.tasks

# 4. Implement
/sp.implement

# Done! Feature complete with spec-driven approach
```

### Transition to Next Phase
```python
Task(
    subagent_type="phase-transition",
    description="Upgrade to Phase II",
    prompt="Validate Phase I complete and transition to Phase II"
)
```

---

**Last Updated**: 2025-12-13
**Project**: Evolution of TODO - PIAIC Hackathon II
**Total Agents**: 10+
**Total Workflows**: 2 main workflows
**Supported Phases**: I → II → III → IV → V
