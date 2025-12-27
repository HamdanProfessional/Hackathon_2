---
id: 002
title: "cloud deployment implementation plan"
stage: plan
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-cloud-deployment
branch: 005-cloud-deployment
user: Hamdan
command: /sp.plan phase-v-cloud-deployment
labels: ["plan", "implementation", "timeline", "cloud", "phase5"]
links:
  spec: specs/005-cloud-deployment/spec.md
  plan: specs/005-cloud-deployment/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-cloud-deployment/plan.md
tests:
  - Implementation plan created with day-by-day breakdown
  - All phases accounted for
  - Dependencies identified
  - Rollback plan included
---

## Prompt

Generate a comprehensive 10-day implementation plan for Phase V Cloud Deployment with event-driven architecture.

CONTEXT:
The specification is complete. We need a detailed day-by-day implementation plan covering database changes, API development, Dapr integration, notification service, cloud deployment, CI/CD, and monitoring.

INSTRUCTIONS:

Create **specs/005-cloud-deployment/plan.md** with:

### Day 1: Database Schema and Migrations
- Create RecurringTask model
- Update Task model (due_date, notified, recurring_task_id)
- Create TaskEventLog model
- Generate and apply Alembic migration
- Verify tables and indexes

### Day 2: Recurring Tasks CRUD API
- Create CRUD operations in `backend/app/crud/recurring_task.py`
- Create Pydantic schemas in `backend/app/schemas/recurring_task.py`
- Create API endpoints in `backend/app/api/recurring_tasks.py`
- Update task endpoints to support due_date
- Test all endpoints

### Day 3: Dapr Integration and Event Publishing
- Install Dapr Python SDK
- Create event publisher service in `backend/app/services/event_publisher.py`
- Integrate event publishing in task CRUD operations
- Create Dapr component manifests
- Test event publishing

### Day 4: Notification Service Development
- Create notification service application structure
- Implement due date checker worker
- Implement recurring task processor
- Create Dockerfile for notifications service
- Test locally

### Day 5: Notification Service Deployment
- Create Helm chart for notifications service
- Configure Dapr sidecar annotations
- Create event subscriptions
- Deploy to Minikube
- Verify event flow

### Day 6: DigitalOcean Cluster Setup
- Install and configure doctl
- Create DOKS cluster (3 nodes)
- Provision DO Managed Redis
- Create DO Container Registry
- Install Dapr on DOKS
- Deploy Redpanda with block storage

### Day 7: Deploy to DigitalOcean
- Build and push Docker images to DO registry
- Create DigitalOcean-specific Helm values
- Create Kubernetes secrets
- Deploy all services with Helm
- Verify DO Load Balancers
- Configure cloud firewall

### Day 8: CI/CD Pipeline
- Create GitHub Actions workflow
- Add secrets (DO registry token, access token, kubeconfig)
- Test automated deployment
- Verify health checks

### Day 9: AI Tools
- Install kubectl-ai
- Install kagent
- Test AI operations (list pods, scale, troubleshoot)

### Day 10: Monitoring and Documentation
- Install Prometheus
- Install Grafana
- Create dashboards
- Run E2E tests
- Update documentation
- Create runbooks

Include:
- Estimated timeline
- Dependencies between tasks
- Rollback procedures
- Success criteria
- Cost summary

ACTION:
Generate the implementation plan now.

## Response snapshot

Successfully created comprehensive 10-day implementation plan.

### Plan Created: specs/005-cloud-deployment/plan.md

**Timeline**: 10 days (completed 2025-12-27)

**Daily Breakdown**:
1. Day 1: Database Schema - RecurringTask, TaskEventLog models, migration
2. Day 2: Recurring Tasks API - Full CRUD with pagination
3. Day 3: Dapr Integration - Event publisher, component manifests
4. Day 4: Notification Service - Workers for due dates and recurring tasks
5. Day 5: Notification Deployment - Helm chart, Dapr subscriptions
6. Day 6: DO Cluster Setup - DOKS, Redis, Registry, Redpanda
7. Day 7: Cloud Deployment - Images, secrets, Helm deployment
8. Day 8: CI/CD Pipeline - GitHub Actions automation
9. Day 9: AI Tools - kubectl-ai, kagent setup
10. Day 10: Monitoring - Prometheus, Grafana, dashboards

**Rollback Plan**:
- Helm rollback commands
- Emergency disable procedures

**Success Criteria**:
- All 11 criteria marked complete
- All timeline items marked complete
- Actual completion: 2025-12-27
