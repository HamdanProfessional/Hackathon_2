---
name: dev-utilities
description: Essential development utilities including git-committer (Conventional Commits enforcement), cors-fixer (Cross-Origin Resource Sharing diagnostics), and api-schema-sync (FastAPI/Pydantic to TypeScript synchronization). Use when enforcing git standards, fixing CORS errors, or synchronizing API contracts between backend and frontend.
version: 2.0.0
category: utilities
tags: [git, commits, cors, api-sync, typescript, fastapi]
dependencies: [git, fastapi, typescript]
---

# Development Utilities Skill

Essential utilities for day-to-day development workflows.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Commit examples, CORS fixes, schema sync |
| Scripts | `scripts/` | `validate_commit.py`, `validate_schema.py` |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- User says "make a commit" or "create conventional commit"
- Fixing "blocked by CORS policy" errors
- Synchronizing API schemas between backend and frontend
- Setting up git commit hooks
- Validating commit message format

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Commit format rejected | Not following Conventional Commits | Check format with `validate_commit.py` |
| CORS errors on frontend | Credentials mode conflict | Remove `credentials: include`, use JWT in header |
| Type mismatches | Pydantic/TS types don't match | Use type conversion map and validate |

---

## Part 1: Git Committer

See `examples/commit-examples.md` for commit message examples.

### Quick Validation

```bash
python .claude/skills/dev-utilities/scripts/validate_commit.py "feat(auth): add OAuth2"
```

---

## Part 2: CORS Fixer

See `examples/cors-fixes.md` for complete CORS error solutions.

### Quick Fix

Remove `credentials: "include"` from frontend fetch calls and use JWT in Authorization header only.

---

## Part 3: API Schema Sync

See `examples/schema-sync-examples.md` for complete schema synchronization examples.

### Validation Script

```bash
python .claude/skills/dev-utilities/scripts/validate_schema.py \
  backend/app/schemas/task.py \
  frontend/lib/types.ts
```

---

## Quality Checklist

For git commits:
- [ ] Commit message follows Conventional Commits format
- [ ] Type is valid (feat, fix, docs, etc.)
- [ ] Description starts with lowercase, no period
- [ ] Header length under 72 characters
- [ ] Breaking changes use both `!` and footer
- [ ] Issue references included (if applicable)

For CORS:
- [ ] No CORS errors in browser console
- [ ] Backend CORS middleware configured
- [ ] Frontend removed credentials mode
- [ ] JWT in Authorization header only
- [ ] Environment-specific origins set
- [ ] Preflight OPTIONS requests succeed

For API sync:
- [ ] Backend Pydantic schemas defined
- [ ] Frontend TypeScript interfaces match
- [ ] Type conversions correct (UUID→string, datetime→string)
- [ ] Optional fields mapped to `| null`
- [ ] Enum types defined on both sides
- [ ] Validation tests pass
