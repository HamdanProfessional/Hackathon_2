---
name: project-setup
description: Complete project initialization with monorepo-setup (workspace management, build orchestration), python-uv-setup (fast Python 3.13+ project scaffolding), and Phase I CLI app initialization. Use when starting new projects, setting up development environments, or configuring monorepo architecture.
version: 2.0.0
category: setup
tags: [setup, monorepo, python, cli, project-init]
dependencies: [uv, node, git]
---

# Project Setup Skill

Complete project initialization and scaffolding.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Project structure templates |
| Scripts | `scripts/` | Setup automation scripts |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- User says "Initialize project" or "Set up new repo"
- Creating new Python projects with uv
- Setting up monorepo structure
- Configuring development environments
- Scaffolding Phase I console apps

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| uv not found | Not installed | Install with `pip install uv` |
| Node modules large | Missing .gitignore | Add node_modules to .gitignore |
| Build failures | Missing dependencies | Run `uv sync` or `npm install` |

---

## Part 1: Monorepo Setup

See main SKILL.md (already comprehensive) for complete monorepo structure.

---

## Part 2: Python UV Setup

**Quick init**:
```bash
uv init --package backend
uv add fastapi sqlmodel uvicorn
```

---

## Part 3: CLI App Setup (Phase I)

**Rich CLI template** with Click/Typer

---

## Quality Checklist

- [ ] .gitignore configured
- [ ] README.md created
- [ ] Dependencies installed
- [ ] Linting configured (ruff, eslint)
- [ ] Tests scaffolded
- [ ] CI/CD pipeline ready
