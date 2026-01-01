---
name: planning
description: Comprehensive planning suite including architecture-planner (implementation plans with component architecture, data models, API design), task-breaker (work decomposition with dependencies and estimates), and spec-architect (Spec-Kit Plus compliant feature specifications). Use when planning features, designing architecture, breaking down tasks, or creating implementation roadmaps.
version: 2.0.0
category: planning
tags: [planning, architecture, task-breakdown, spec, implementation]
dependencies: []
---

# Planning Skill

Comprehensive planning suite for software development projects.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Basic plan, feature spec, task breakdown |
| Scripts | `scripts/` | `generate_plan.py` - Plan generator |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- User says "plan the implementation" or "design the architecture"
- Creating implementation plans from specifications
- Breaking down complex features into manageable tasks
- Creating Spec-Kit Plus compliant feature specifications
- Designing system architecture and component relationships
- Evaluating architectural tradeoffs

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Plan too vague | Missing acceptance criteria | Add specific, testable criteria |
| Dependencies unclear | Tasks not properly ordered | Create dependency graph |
| Estimates off | Not considering complexity | Use story point guidelines |

---

## Part 1: Architecture Planner

See `examples/basic-plan.md` for complete implementation plan template.

### Quick Start

```bash
python .claude/skills/planning/scripts/generate_plan.py specs/001-task-management/spec.md
```

---

## Part 2: Task Breaker

See `examples/task-breakdown.md` for complete task breakdown template.

### Story Point Guidelines

| Points | Time | Complexity |
|--------|------|------------|
| 1 | 1-2 hours | Trivial |
| 2 | 2-4 hours | Simple |
| 3 | 4-8 hours | Moderate |
| 5 | 1-2 days | Complex |
| 8 | 2-3 days | Very Complex |
| 13 | 3-5 days | Extremely Complex |

---

## Part 3: Spec Architect

See `examples/feature-spec.md` for complete feature specification template.

---

## Quality Checklist

Before finalizing plans:
- [ ] Spec has been read completely
- [ ] Architecture aligns with current phase
- [ ] Data model includes all fields and indexes
- [ ] API endpoints follow RESTful conventions
- [ ] All tasks have clear acceptance criteria
- [ ] Task dependencies identified
- [ ] Testing strategy covers unit/integration/E2E
- [ ] Risks identified with mitigations
- [ ] User stories have clear value propositions
- [ ] Acceptance criteria are testable
