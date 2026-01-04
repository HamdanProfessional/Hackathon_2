---
name: phase-transition
description: Validate phase completion by reading specs/[phase]/spec.md and checking all acceptance criteria in tests/ are passing, create migration ADRs in docs/adr/XXX-phase-migration.md with Context/Decision/Consequences for CLI→Web→AI→Kubernetes→Cloud transitions, update CLAUDE.md constitution with new Phase constraints, and generate transition checklists with Pre/Migration/Post sections. Use when moving from Phase I CLI to Phase II Web, validating Phase III AI readiness, or planning Phase V event-driven architecture.
---

# Phase Transition

Guides transitions between architectural phases.

## Quick Start

Initiate phase transition:
```bash
/skill phase-transition target_phase=phase-ii
```

## Phase Transition Paths

| From | To | Key Changes |
|------|----|-------------|
| I (CLI) | II (Web) | Add Next.js, FastAPI, PostgreSQL |
| II (Web) | III (AI) | Add Gemini, MCP tools, chat interface |
| III (AI) | IV (K8s) | Containerize, add manifests, Helm charts |
| IV (K8s) | V (Cloud) | Add Kafka, Dapr, CI/CD, event-driven |

## Implementation Steps

### 1. Validate Current Phase
Check completion criteria:
- All features implemented
- Acceptance criteria met
- Tests passing
- Technical debt documented

### 2. Create Migration ADR
Document architectural decision:
```markdown
# ADR-XXX: Phase N → Phase N+1 Migration

## Context
Current state and transition rationale

## Decision
Technologies and architecture changes

## Consequences
Benefits, risks, breaking changes

## Migration Path
Step-by-step implementation strategy
```

### 3. Update Constitution
Bump MAJOR version and add new constraints:
```markdown
**Version**: N.0.0 → N+1.0.0
**Phase Status**: Phase N ✅ COMPLETED → Phase N+1 ⚙️ IN PROGRESS
**New Constraints**: [List Phase N+1 requirements]
```

### 4. Generate Migration Spec
Create migration specification:
- Functional requirements
- Data migration plan
- Success criteria
- Rollback strategy

### 5. Create Transition Checklist
Pre, during, and post-migration tasks:
```markdown
## Pre-Transition
- [ ] All features complete
- [ ] Backup current state

## Migration
- [ ] Install dependencies
- [ ] Deploy infrastructure
- [ ] Migrate data

## Post-Transition
- [ ] Validate all features
- [ ] Update documentation
- [ ] Tag release
```

## Phase-Specific Constraints

### Phase I → II
**Add**: Web UI, REST API, persistent storage
**Remove**: CLI-only interface
**Key**: Maintain data compatibility

### Phase II → III
**Add**: AI chat, MCP tools, conversation state
**Maintain**: All CRUD functionality
**Key**: Natural language interface

### Phase III → IV
**Add**: Containers, Kubernetes, Helm
**Maintain**: AI functionality
**Key**: Stateless deployment

### Phase IV → V
**Add**: Event streaming, Dapr, CI/CD
**Maintain**: All existing features
**Key**: Event-driven architecture

## Success Criteria

Transition successful when:
- [ ] Previous phase features still work
- [ ] New phase features implemented
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Release tagged `vN.0.0`

## Error Handling

### Validation Failures
- Report incomplete features
- Block transition until resolved
- Document blockers

### Migration Failures
- Execute rollback plan
- Update ADR with lessons learned
- Adjust migration strategy

## Integration Commands

Use with Spec-Kit workflow:
```bash
/sp.specify migration-phase-i-to-ii
/sp.plan
/sp.tasks
/sp.implement
/sp.adr "Migration decision"
```