# Consolidated Agents Architecture

## Overview
This document consolidates 40+ fragmented agents into 8 Core Strategic Sub-agents for the Hackathon II Evolution of Todo project. Each agent handles a specific domain across Phases I-III.

## The 8 Core Strategic Sub-agents

### 1. Spec-Architect
**Merges:** spec-architect, task-breaker, architecture-planner, adr-generator, phr-documenter
**Domain:** Specification and Architecture Management

### 2. Backend-Engineer
**Merges:** fastapi-endpoint-generator, sqlmodel-schema-builder, db-migration-wizard, cors-fixer, crud-builder, backend-scaffolder
**Domain:** Python/FastAPI/SQLModel Stack

### 3. Frontend-UX-Designer
**Merges:** frontend-component, chatkit-integrator, console-ui-builder
**Domain:** Next.js/ChatKit/Console UI

### 4. AI-Systems-Specialist
**Merges:** ai-mcp, mcp-tool-maker, stateless-agent-enforcer, agent-builder, agent-orchestrator
**Domain:** OpenAI SDK/MCP/Stateless Architecture

### 5. Quality-Enforcer
**Merges:** integration-tester, code-reviewer, test-builder, performance-analyzer, deployment-validator
**Domain:** Code Quality and Testing

### 6. Workflow-Librarian
**Merges:** doc-generator, git-committer, i18n-bilingual-translator
**Domain:** Documentation and Workflow

### 7. System-Integrator
**Merges:** monorepo-setup, python-uv-setup, api-schema-sync, phase-management
**Domain:** System Integration and Setup

### 8. Cloud-DevOps-Lite
**Merges:** k8s-deployer, k8s-troubleshoot, cloud-devops, infrastructure, dapr-event-flow
**Domain:** Docker/K8s/Cloud Preparation

## Phase Evolution Support
Each agent is designed to work seamlessly across all phases:
- **Phase I (Console):** Core functionality with minimal dependencies
- **Phase II (Web):** Full-stack integration capabilities
- **Phase III (AI):** Chatbot and AI integration ready