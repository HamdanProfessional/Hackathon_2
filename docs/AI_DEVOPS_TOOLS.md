# AI DevOps Tools Quick Reference

This guide covers the installation and usage of AI-powered DevOps tools for Kubernetes management in the Todo app Phase V deployment.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [kubectl-ai Usage](#kubectl-ai-usage)
4. [kagent Usage](#kagent-usage)
5. [Common Workflows](#common-workflows)
6. [API Key Configuration](#api-key-configuration)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### kubectl-ai

**Description**: AI-powered kubectl plugin that converts natural language into kubectl commands and Kubernetes manifests.

**Maintainer**: GoogleCloudPlatform
**Repository**: https://github.com/GoogleCloudPlatform/kubectl-ai
**License**: Apache 2.0

**Key Features**:
- Generate kubectl commands from natural language
- Create Kubernetes YAML manifests automatically
- Supports multiple LLM providers (OpenAI, Anthropic, Azure, etc.)
- Works as both kubectl plugin and standalone tool

### kagent

**Description**: Agentic AI framework for building, deploying, and managing AI-powered solutions in Kubernetes environments.

**Maintainer**: kagent-dev
**Website**: https://kagent.dev/
**Repository**: https://github.com/kagent-dev/kagent
**License**: Apache 2.0

**Key Features**:
- Deploy AI agents with MCP (Model Context Protocol) tools
- Multi-provider support (OpenAI, Anthropic, Gemini, Ollama)
- Built-in governance and security controls
- Tool framework for agent-environment interaction
- Helm chart-based installation

---

## Installation

### Quick Install (Automated)

#### Windows (PowerShell)

```powershell
# Run the installation script
.\scripts\install-devops-tools.ps1

# Or manually
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\install-devops-tools.ps1
```

#### Linux/macOS (Bash)

```bash
# Make script executable
chmod +x scripts/install-devops-tools.sh

# Run installation
./scripts/install-devops-tools.sh
```

### Manual Installation

#### kubectl-ai

**Prerequisites**:
- kubectl v1.12 or later
- Krew plugin manager

**Step 1: Install Krew**

```bash
# Linux/macOS
curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew.{tar.gz,yaml}"
tar zxvf krew.tar.gz
./krew-linux_amd64 install krew

# Add to PATH
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-windows_amd64.exe" -OutFile krew.exe
.\krew.exe install --manifest=krew.exe --bin-dir=.\bin
```

**Step 2: Install kubectl-ai**

```bash
kubectl krew install ai

# Verify
kubectl ai --help
```

#### kagent

**Option 1: Using install script (Recommended)**

```bash
# Download and run installer
curl https://raw.githubusercontent.com/kagent-dev/kagent/refs/heads/main/scripts/get-kagent | bash

# Or for Windows
Invoke-WebRequest -Uri "https://github.com/kagent-dev/kagent/releases/latest/download/kagent-windows-amd64.exe" -OutFile kagent.exe
```

**Option 2: Using Go**

```bash
go install github.com/kagent-dev/kagent/cmd/kagent@latest
```

**Option 3: Using Helm**

```bash
# Install CRDs first
helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
  --namespace kagent \
  --create-namespace

# Install kagent
helm install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent \
  --namespace kagent \
  --set providers.default=openAI \
  --set providers.openAI.apiKey=$OPENAI_API_KEY
```

---

## kubectl-ai Usage

### Basic Syntax

```bash
kubectl ai "<natural language command>"
```

### Common Commands

#### List Resources

```bash
# List all pods
kubectl ai "list all pods in production namespace"

# Show all resources
kubectl ai "show me all deployments in default namespace"

# Get services
kubectl ai "display all services with their cluster IPs"
```

#### Inspect Resources

```bash
# Get deployment details
kubectl ai "show me the backend service details"

# Check pod status
kubectl ai "what is the status of frontend pods?"

# View logs
kubectl ai "show logs from the backend-xyz pod"
```

#### Troubleshooting

```bash
# Diagnose pod failures
kubectl ai "why is the backend pod crashing?"

# Find resource issues
kubectl ai "what's wrong with the todo-app deployment?"

# Check resource usage
kubectl ai "show me resource usage for all pods"
```

#### Generate Manifests

```bash
# Create deployment
kubectl ai "create a deployment for nginx with 3 replicas"

# Create service
kubectl ai "generate a service manifest for the todo-app backend"

# Create configmap
kubectl ai "create a configmap with environment variables"
```

### Configuration

**Set API key (required)**:

```bash
# OpenAI (default)
export OPENAI_API_KEY="sk-..."

# Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Azure OpenAI
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."

# Google Gemini
export GEMINI_API_KEY="..."
```

**Set model**:

```bash
# Use specific model
kubectl ai "create deployment" --model gpt-4

# Use Anthropic
kubectl ai "list pods" --provider anthropic --model claude-3-opus-20240229
```

---

## kagent Usage

### Installation to Cluster

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Install with demo profile (includes sample agents and tools)
kagent install --profile demo

# Install minimal profile (no default agents)
kagent install --profile minimal

# Verify installation
kagent list agents
```

### Agent Management

#### List Agents

```bash
# List all agents
kagent list agents

# Get agent details
kagent get agent <agent-name>

# Describe agent configuration
kagent describe agent <agent-name>
```

#### Create Agent

```bash
# Create new agent
kagent create agent my-agent \
  --model gpt-4 \
  --provider openai \
  --tools "mcp-kubernetes,mcp-git"

# Or using YAML manifest
kubectl apply -f my-agent.yaml
```

#### Delete Agent

```bash
kagent delete agent my-agent
```

### Tool Management

#### List Available Tools

```bash
# List all MCP tools
kagent list tools

# Show tool details
kagent get tool <tool-name>
```

#### Register Tool

```bash
# Register MCP tool
kagent register tool my-tool \
  --type mcp \
  --endpoint http://my-tool:8080
```

### Agent Interaction

#### Execute Agent

```bash
# Run agent
kagent run my-agent

# Run with input
kagent run my-agent --input "list all pods"

# Stream agent output
kagent run my-agent --follow
```

#### Query Agent

```bash
# Query agent status
kagent query "what services are running?"

# Get agent response
kagent ask my-agent "scale backend to 5 replicas"
```

### Cluster Operations

```bash
# Scale deployment via agent
kagent ask scale-agent "scale backend deployment to 4 replicas"

# Diagnose issues
kagent diagnose backend pods

# Query cluster state
kagent query "what deployments are in the todo namespace?"
```

---

## Common Workflows

### Workflow 1: Diagnose Deployment Issues

```bash
# Step 1: Use kubectl-ai to identify the problem
kubectl ai "why is the todo-app-backend deployment failing?"

# Step 2: Use kagent to get detailed analysis
kagent diagnose todo-app-backend

# Step 3: Apply suggested fix
kubectl ai "create a patch to fix the todo-app-backend deployment"
```

### Workflow 2: Generate and Apply Manifests

```bash
# Step 1: Generate manifest with kubectl-ai
kubectl ai "create a deployment for todo-backend with 3 replicas and image todoapp/backend:v1.0" > deployment.yaml

# Step 2: Review and apply
kubectl apply -f deployment.yaml

# Step 3: Verify with kagent
kagent query "is the todo-backend deployment healthy?"
```

### Workflow 3: Scale Applications

```bash
# Option 1: Using kubectl-ai
kubectl ai "scale frontend deployment to 5 replicas"

# Option 2: Using kagent
kagent ask scaling-agent "scale frontend to handle increased load"

# Option 3: Traditional kubectl
kubectl scale deployment frontend --replicas=5
```

### Workflow 4: Monitor Resources

```bash
# Get resource usage with kubectl-ai
kubectl ai "show resource usage for all namespaces"

# Get AI-powered insights with kagent
kagent query "which pods are consuming the most memory?"

# Get detailed metrics
kubectl top pods -A
```

### Workflow 5: Debug Pod Failures

```bash
# Identify failing pods
kubectl ai "show all pods with CrashLoopBackOff status"

# Get logs for failed pod
kubectl logs <pod-name> --previous

# AI-powered root cause analysis
kagent diagnose <pod-name>

# Generate fix
kubectl ai "create a configmap with the missing environment variables"
```

---

## API Key Configuration

### OpenAI

```bash
export OPENAI_API_KEY="sk-proj-..."

# With kagent
kagent install --providers.default=openAI --providers.openAI.apiKey=$OPENAI_API_KEY
```

### Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

# With kagent
kagent install --providers.default=anthropic --providers.anthropic.apiKey=$ANTHROPIC_API_KEY
```

### Google Gemini

```bash
export GEMINI_API_KEY="..."

# With kagent
kagent install --providers.default=gemini --providers.gemini.apiKey=$GEMINI_API_KEY
```

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."

# With kagent
kagent install \
  --providers.default=azureOpenAI \
  --providers.azureOpenAI.apiKey=$AZURE_OPENAI_API_KEY \
  --providers.azureOpenAI.endpoint=$AZURE_OPENAI_ENDPOINT
```

### Ollama (Local)

```bash
# No API key needed for local Ollama
kagent install --providers.default=ollama
```

---

## Troubleshooting

### kubectl-ai Issues

**Problem**: `kubectl: ai: not found`

**Solution**:
```bash
# Verify krew installation
kubectl krew list

# Reinstall ai plugin
kubectl krew install ai

# Check PATH
echo $PATH | grep krew
```

**Problem**: API key errors

**Solution**:
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Set correct key
export OPENAI_API_KEY="your-key"

# Try different provider
kubectl ai "list pods" --provider anthropic
```

**Problem**: Slow responses

**Solution**:
```bash
# Use faster model
kubectl ai "list pods" --model gpt-3.5-turbo

# Reduce context
kubectl ai "list pods" --context 1000
```

### kagent Issues

**Problem**: `kagent: command not found`

**Solution**:
```bash
# Verify installation
which kagent

# Add to PATH
export PATH=$PATH:/usr/local/bin

# Reinstall
curl https://raw.githubusercontent.com/kagent-dev/kagent/refs/heads/main/scripts/get-kagent | bash
```

**Problem**: Installation to cluster fails

**Solution**:
```bash
# Check cluster connectivity
kubectl cluster-info

# Check kagent namespace
kubectl get ns kagent

# View kagent pods
kubectl get pods -n kagent

# Check pod logs
kubectl logs -n kagent deployment/kagent-controller
```

**Problem**: Agent not responding

**Solution**:
```bash
# Check agent status
kagent get agent my-agent

# Check agent pods
kubectl get pods -l agent=my-agent

# View agent logs
kubectl logs -l agent=my-agent --tail=100

# Restart agent
kagent restart agent my-agent
```

### General Issues

**Problem**: Tools not working after installation

**Solution**:
```bash
# Restart shell/terminal
exec $SHELL  # Linux/macOS
# Or close and reopen terminal on Windows

# Verify installations
kubectl ai version
kagent version
```

**Problem**: Permission denied

**Solution**:
```bash
# Linux/macOS: Use sudo for system-wide installation
sudo kubectl krew install ai

# Or install to user directory
export KREW_ROOT=$HOME/.krew
kubectl krew install ai
```

---

## Best Practices

1. **Start with demo profile**: When installing kagent, use `--profile demo` to get pre-configured agents and tools
2. **Set API keys securely**: Use environment variables or secret management, never hardcode in scripts
3. **Use version control**: Commit generated manifests to Git before applying
4. **Test in dev first**: Always test AI-generated commands in development namespace
5. **Review AI output**: Always review kubectl-ai output before executing
6. **Monitor costs**: AI API calls can be expensive, set usage limits and monitor spending
7. **Keep tools updated**: Regularly update kubectl-ai and kagent to get latest features
8. **Use profiles**: Create different agent profiles for dev, staging, and production

---

## Additional Resources

### Official Documentation

- **kubectl-ai**: https://github.com/GoogleCloudPlatform/kubectl-ai
- **kagent**: https://kagent.dev/docs/
- **Krew**: https://krew.sigs.k8s.io/docs/user-guide/setup/install/
- **Kubernetes**: https://kubernetes.io/docs/

### Community

- **kagent Blog**: https://kagent.dev/blog/
- **Kubernetes Slack**: #kubectl-ai and #kagent channels
- **GitHub Discussions**:
  - https://github.com/GoogleCloudPlatform/kubectl-ai/discussions
  - https://github.com/kagent-dev/kagent/discussions

### Tutorials

- "AI Agents for Kubernetes: Getting Started with Kagent" (September 2025)
- "Let AI Write Your Kubernetes YAML: A Normal Dev's Guide to kubectl-ai"
- "Deploying AI Agent with kagent: A Test Drive"

---

## Version Information

- **Document Version**: 1.0.0
- **Last Updated**: 2025-12-26
- **Project**: Evolution of TODO - Phase V Cloud Deployment
- **Maintainer**: CloudOps Engineer

---

## Quick Reference Card

### kubectl-ai

```bash
# Install
kubectl krew install ai

# Use
kubectl ai "<natural language>"

# Examples
kubectl ai "list all pods"
kubectl ai "create deployment for nginx"
kubectl ai "why is backend crashing?"
```

### kagent

```bash
# Install
kagent install --profile demo

# Use
kagent list agents
kagent run my-agent
kagent query "cluster status"

# Examples
kagent diagnose backend
kagent ask agent "scale frontend"
```

---

**Sources**:
- [Installing kagent - Official Documentation](https://kagent.dev/docs/kagent/introduction/installation)
- [kubectl-ai - GitHub Repository](https://github.com/GoogleCloudPlatform/kubectl-ai)
- [Krew Plugin Index](https://krew.sigs.k8s.io/plugins/)
- [kagent Official Website](https://kagent.dev/)
- [AI Agents for Kubernetes - Getting Started Guide](https://www.infracloud.io/blogs/ai-agents-for-kubernetes/)
- [Boost Kubernetes Productivity with kubectl-ai](https://kodekloud.com/blog/no-more-kubectl-commands/)
