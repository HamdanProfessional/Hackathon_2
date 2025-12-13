# Phase Transition Skill

**Type**: Agent Skill
**Category**: Phase Management
**Phases**: All → Next Phase

---

## Purpose

This skill guides the transition from one architectural phase to the next in the Evolution of TODO project. It validates phase completion, creates migration ADRs, and updates the constitution for the new phase.

---

## Skill Invocation

```
/skill phase-transition
```

Or via Claude Code Task tool:
```python
Task(
    subagent_type="phase-transition",
    description="Transition to Phase II",
    prompt="Validate Phase I completion and guide transition to Phase II (Full-Stack Web Application)"
)
```

---

## What This Skill Does

1. **Validates Current Phase Completion**
   - Checks all features are implemented
   - Verifies acceptance criteria met
   - Reviews technical debt
   - Ensures tests pass

2. **Creates Migration ADR**
   - Documents transition rationale
   - Lists new technologies
   - Defines migration strategy
   - Identifies risks

3. **Updates Constitution**
   - Bumps MAJOR version
   - Adds new phase constraints
   - Updates technology stack
   - Maintains phase history

4. **Generates Migration Spec**
   - Details transition steps
   - Plans data migration
   - Documents breaking changes
   - Sets success criteria

5. **Creates Transition Checklist**
   - Pre-transition tasks
   - Migration tasks
   - Post-transition validation
   - Rollback plan

---

## Phase Transition Paths

### Phase I → Phase II
**From**: Monolithic Script (CLI)
**To**: Full-Stack Web Application

**Changes**:
- Add Next.js frontend
- Add FastAPI backend
- Add Neon PostgreSQL database
- Add Better Auth authentication
- Migrate from in-memory to persistent storage

**Migration Strategy**:
1. Extract TaskManager logic → FastAPI service
2. Create database schema with SQLModel
3. Build Next.js UI consuming API
4. Add authentication layer
5. Deploy frontend (Vercel) + backend (cloud)

---

### Phase II → Phase III
**From**: Full-Stack Web Application
**To**: AI-Powered Chatbot

**Changes**:
- Add OpenAI ChatKit frontend
- Add OpenAI Agents SDK backend
- Create MCP server with Official MCP SDK
- Add conversation state management
- Build natural language interface

**Migration Strategy**:
1. Create MCP tools for CRUD operations
2. Build stateless chat endpoint
3. Integrate OpenAI Agents SDK
4. Add conversation history storage
5. Deploy ChatKit UI

---

### Phase III → Phase IV
**From**: AI-Powered Chatbot
**To**: Local Kubernetes Deployment

**Changes**:
- Containerize with Docker
- Create Kubernetes manifests
- Build Helm charts
- Deploy to Minikube
- Add health checks

**Migration Strategy**:
1. Create Dockerfiles for frontend/backend/MCP
2. Write Kubernetes service/deployment YAMLs
3. Package with Helm
4. Deploy to local Minikube cluster
5. Configure kubectl-ai and kagent

---

### Phase IV → Phase V
**From**: Local Kubernetes Deployment
**To**: Advanced Cloud Deployment

**Changes**:
- Add Kafka/Redpanda event streaming
- Integrate Dapr building blocks
- Deploy to cloud Kubernetes (DOKS/GKE/AKS)
- Implement event-driven architecture
- Set up CI/CD pipeline

**Migration Strategy**:
1. Add Kafka topics for events
2. Refactor to event-driven pattern
3. Add Dapr components (Pub/Sub, State, Bindings)
4. Deploy to cloud K8s cluster
5. Configure monitoring and logging

---

## Execution Flow

### Step 1: Pre-Transition Validation

```yaml
Checks:
  - All Phase N features complete
  - All acceptance criteria validated
  - All tests passing
  - Technical debt documented
  - README up to date
```

**Output**: Phase readiness report

---

### Step 2: Migration ADR Creation

**File**: `history/adr/XXX-phase-N-to-phase-N+1-migration.md`

**Contents**:
```markdown
# ADR-XXX: Phase N → Phase N+1 Migration

## Context
[Current phase status, reasons for transition]

## Decision
[Transition to Phase N+1, technology additions]

## Consequences
[Benefits, risks, breaking changes]

## Migration Path
[Step-by-step migration strategy]

## Rollback Plan
[How to revert if needed]

## Alternatives Considered
[Why not other approaches]
```

---

### Step 3: Constitution Update

**File**: `.specify/memory/constitution.md`

**Changes**:
- Bump version (MAJOR increment)
- Add Phase N+1 section
- Update technology stack
- Add new constraints
- Update roadmap progress

**Example**:
```markdown
<!--
SYNC IMPACT REPORT:
Version: 2.0.0 → 3.0.0
Change Type: MAJOR - Phase II transition
Modified Principles:
  - Technology Stack: Added Next.js, FastAPI, Neon
  - Storage: Changed from in-memory to PostgreSQL
  - Interface: Changed from CLI to Web UI + REST API
-->
```

---

### Step 4: Migration Spec Creation

**File**: `specs/migration-phase-N-to-N+1/spec.md`

**Sections**:
1. Migration Overview
2. User Stories (what stays/changes)
3. Functional Requirements (new tech integration)
4. Success Criteria (all Phase N features work in Phase N+1)
5. Data Migration Plan
6. Rollback Strategy

---

### Step 5: Transition Checklist

Generate checklist in `specs/migration-phase-N-to-N+1/checklists/transition.md`

```markdown
## Pre-Transition
- [ ] All Phase N features complete
- [ ] Tests passing
- [ ] Technical debt documented
- [ ] Backup current state

## Migration
- [ ] Install new dependencies
- [ ] Create new infrastructure
- [ ] Migrate data
- [ ] Update code structure
- [ ] Deploy to new environment

## Post-Transition
- [ ] All Phase N features still work
- [ ] New Phase N+1 features work
- [ ] Tests updated and passing
- [ ] Documentation updated
- [ ] Constitution ratified
- [ ] Git tag created
```

---

## Phase-Specific Constraints

### Phase I Constraints (Removed After Transition)
- ❌ Python standard library only
- ❌ In-memory storage only
- ❌ Single file CLI

### Phase II Constraints (Added)
- ✅ Monorepo structure (frontend/ + backend/)
- ✅ RESTful API design
- ✅ JWT authentication required
- ✅ Persistent storage (Neon PostgreSQL)

### Phase III Constraints (Added)
- ✅ Stateless MCP tools
- ✅ Conversation state in database
- ✅ Natural language parsing

### Phase IV Constraints (Added)
- ✅ Containerized services
- ✅ Kubernetes manifests required
- ✅ Health checks implemented
- ✅ Horizontal scaling ready

### Phase V Constraints (Added)
- ✅ Event-driven architecture
- ✅ CQRS pattern for read/write
- ✅ Multi-cloud compatible
- ✅ CI/CD pipeline

---

## Success Criteria

A phase transition is successful when:

1. **Backward Compatibility**: All Phase N features still work
2. **New Capabilities**: Phase N+1 features implemented
3. **Tests Passing**: All test suites green
4. **Documentation Updated**: README, constitution, ADRs current
5. **Git Tagged**: Release marked with `vN.0.0`
6. **Deployment Verified**: App runs in new environment

---

## Error Handling

### If Validation Fails
- Report which features incomplete
- List failing acceptance criteria
- Block transition until resolved

### If Migration Fails
- Execute rollback plan
- Document failure in ADR
- Update checklist with blockers

### If Tests Fail Post-Migration
- Identify regressions
- Fix or document breaking changes
- Update migration strategy

---

## Example Usage

### User Request:
```
"We've completed all Phase I features. I want to move to Phase II."
```

### Skill Response:
```
🔍 Validating Phase I completion...
✅ All features implemented
✅ Acceptance criteria met
✅ Tests passing

📋 Creating migration ADR (ADR-002-phase-i-to-ii-migration.md)...
📝 Updating constitution (2.0.0 → 3.0.0)...
📄 Generating migration spec (specs/migration-phase-i-to-ii/spec.md)...
✅ Transition checklist created

Next steps:
1. Review ADR-002-phase-i-to-ii-migration.md
2. Ratify constitution v3.0.0
3. Run /sp.plan on migration spec
4. Execute migration tasks
5. Validate Phase I features in Phase II environment
6. Tag release v3.0.0
```

---

## Integration with Spec-Kit

This skill integrates with existing commands:

```bash
# After validation passes
/sp.specify migration-phase-i-to-ii  # Generate migration spec
/sp.plan                             # Create migration plan
/sp.tasks                            # Break down migration tasks
/sp.implement                        # Execute migration
/sp.adr "Phase I → II Migration"     # Document decision
```

---

## Tools Available to This Skill

- Read: Access current phase files
- Write: Create ADRs, specs, checklists
- Edit: Update constitution
- Bash: Run validation commands (tests, builds)
- Glob/Grep: Analyze codebase completeness

---

## Deliverables

When this skill completes, you'll have:

1. ✅ Phase readiness report
2. ✅ Migration ADR (`history/adr/XXX-migration.md`)
3. ✅ Updated constitution (MAJOR version bump)
4. ✅ Migration spec (`specs/migration-*/spec.md`)
5. ✅ Transition checklist
6. ✅ Rollback plan
7. ✅ Git tag ready (`vN.0.0`)

---

**Skill Version**: 1.0.0
**Created**: 2025-12-13
**Hackathon Points**: Contributes to +200 bonus (Reusable Intelligence)
