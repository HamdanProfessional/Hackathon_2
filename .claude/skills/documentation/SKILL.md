---
name: documentation
description: Generate README.md with # Project Name, ## Installation, ## Usage sections using pip install/npm install commands, create ADR (Architecture Decision Records) in docs/adr/XXX-title.md with Context/Decision/Consequences sections, and record PHR (Prompt History Records) in history/prompts/XXX/ with routing metadata, timestamp, and conversation summary. Use when documenting API endpoints at /docs, capturing architectural decisions like 'chose PostgreSQL over MongoDB', or creating AI conversation traceability.
---

# Documentation Skill

Comprehensive documentation generation for projects.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | README, ADR, PHR, API docs examples |
| Scripts | `scripts/` | `generate_adr.py` - ADR generator |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- User says "Generate documentation for..." or "Create README for..."
- API endpoints lack documentation
- New feature needs user-facing documentation
- Architecture changes require updated diagrams
- Significant architectural decisions need ADR documentation
- Prompt History Records (PHR) need to be created after work completion

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Documentation out of sync | Code changed without doc updates | Run doc generation after feature completion |
| ADR missing context | Not enough background info | Include problem statement and constraints |
| PHR routing errors | Stage not detected | Check PHR routing rules in spec |

---

## Part 1: Documentation Generator

### README Template

See `examples/readme-example.md` for complete README template.

### API Documentation Template

See `examples/api-docs-example.md` for complete API documentation.

### Auto-Generated Documentation

**FastAPI auto-docs** (Swagger UI):
```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="My API",
    description="API description",
    version="1.0.0"
)

# Access at /docs
```

---

## Part 2: ADR Generator

### When to Create an ADR

- Significant architectural decision made (passes 3-part test)
- Need to document technology choices, patterns, or design decisions
- Team needs alignment on technical direction
- Future developers need to understand "why" decisions were made

### 3-Part Significance Test

Before creating an ADR, verify:
1. **Impact**: Does this have long-term architectural consequences?
2. **Alternatives**: Were multiple viable options considered?
3. **Scope**: Is this cross-cutting or system-defining?

### Quick Generation

```bash
python .claude/skills/documentation/scripts/generate_adr.py \
  "Use SQLModel for ORM" \
  --context "Need ORM for FastAPI integration" \
  --problem "Multiple ORM options available" \
  --chosen "SQLModel" \
  --rationale "Native Pydantic integration, FastAPI support"
```

See `examples/adr-example.md` for complete ADR template.

---

## Part 3: PHR Documenter

### PHR Workflow

1. **Detect Stage**: Determine stage (constitution, spec, plan, tasks, red, green, refactor, misc, general)
2. **Resolve Route**: Determine destination directory
3. **Allocate ID**: Get sequential ID for target directory
4. **Extract Metadata**: Gather context from conversation
5. **Fill Template**: Replace all placeholders
6. **Validate PHR**: Ensure completeness
7. **Write PHR**: Save to appropriate location

See `examples/phr-example.md` for complete PHR template.

### Routing Rules

**Constitution PHR**:
- Stage: `constitution`
- Path: `history/prompts/constitution/`
- Filename: `<ID>-<slug>.constitution.prompt.md`

**Feature PHR**:
- Stages: `spec`, `plan`, `tasks`, `red`, `green`, `refactor`, `explainer`, `misc`
- Path: `history/prompts/<feature-name>/`
- Filename: `<ID>-<slug>.<stage>.prompt.md`

**General PHR**:
- Stage: `general`
- Path: `history/prompts/general/`
- Filename: `<ID>-<slug>.general.prompt.md`

---

## Quality Checklist

Before finalizing documentation:
- [ ] All code examples are tested and correct
- [ ] Commands work on both Windows and Unix
- [ ] Environment variables documented
- [ ] Prerequisites clearly listed
- [ ] Installation steps are sequential and complete
- [ ] API endpoints include request/response examples
- [ ] Error responses documented
- [ ] Architecture diagrams are accurate
- [ ] Links to external resources work
- [ ] ADR passes 3-part significance test
- [ ] ADR includes at least 2-3 options with honest pros/cons
- [ ] PHR has no unresolved placeholders
- [ ] PHR path matches routing rules
