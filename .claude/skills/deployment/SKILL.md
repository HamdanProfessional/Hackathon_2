---
name: deployment
description: Complete deployment suite including kubernetes (Docker, Helm charts, K8s manifests, Minikube/DOKS/GKE/AKS, Dapr sidecars), vercel-deploy (frontend and backend deployment automation), and deployment-validator (health checks, configuration validation, production readiness).
version: 2.0.0
category: infrastructure
tags: [kubernetes, docker, helm, vercel, deployment, dapr, monitoring]
dependencies: [kubectl, helm, docker, vercel-cli]
---

# Deployment Skill

Comprehensive deployment automation and validation.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Docker, Helm, deployment patterns |
| Scripts | `scripts/` | Validation and deployment scripts |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- Deploying applications to Kubernetes
- Creating Docker images and containers
- Writing Helm charts
- Deploying to Vercel
- Validating deployment health
- Setting up Dapr sidecars

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| ImagePullBackOff | Wrong registry/secret | Create/update docker-registry secret |
| CrashLoopBackOff | Missing env vars | Add secrets, increase limits |
| Pod not ready | Health check failing | Check probe paths, add delays |

---

## Part 1: Kubernetes Deployment

See main SKILL.md (already comprehensive) for Docker, Helm, and K8s templates.

---

## Part 2: Vercel Deployment

**Quick deploy**:
```bash
vercel --prod
```

---

## Part 3: Deployment Validator

**Health check script**:
```bash
python scripts/health_check.py
```

---

## Quality Checklist

- [ ] Secrets in environment variables
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Multi-stage Docker builds
- [ ] Non-root containers
- [ ] HTTPS enforced
- [ ] Connection pooling
- [ ] Logging to stdout
- [ ] Graceful shutdown
- [ ] Pods READY (2/2 for Dapr, 1/1 otherwise)
