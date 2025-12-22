# Evolution of TODO - Agent Skills

This directory contains reusable agent skills for the PIAIC Hackathon II project.

---

## What are Agent Skills?

Agent skills are specialized, reusable capabilities that Claude Code can invoke to perform complex, multi-step operations. They act as intelligent subagents with specific expertise.

**Benefits**:
- **+200 Bonus Points**: Creating reusable intelligence via skills
- **Consistency**: Same workflow across all phases
- **Efficiency**: Automated complex tasks
- **Quality**: Best practices built-in

---

## Available Skills

### Phase Management

#### `phase-management/SKILL.md`
**Purpose**: Guide transitions between architectural phases

**Usage**:
```
/skill phase-transition target_phase=phase-ii
```

**What it does**:
- Validates current phase completion
- Creates migration ADR
- Updates constitution (MAJOR version bump)
- Generates migration spec
- Creates transition checklist

**Phases**: All → Next Phase

---

### Infrastructure

#### `infrastructure/SKILL.md`
**Purpose**: Set up Kubernetes environments (local & cloud)

**Usage**:
```
/skill kubernetes-setup environment=local
/skill kubernetes-setup environment=cloud provider=digitalocean
```

**What it does**:
- Creates Kubernetes manifests
- Generates Helm charts
- Sets up namespaces, secrets, configmaps
- Integrates kubectl-ai and kagent
- Documents deployment process

**Phases**: IV & V

---

### AI & MCP

#### `ai-mcp/SKILL.md`
**Purpose**: Build MCP server from slash commands

**Usage**:
```
/skill mcp-builder
```

**What it does**:
- Analyzes `.claude/commands/` directory
- Generates Python MCP server with Official SDK
- Creates `.mcp.json` configuration
- Converts commands to MCP prompts
- Tests and documents server

**Phases**: All (especially III+)

#### `ai-mcp/agent-builder/SKILL.md`
**Purpose**: Create AI agents with AsyncOpenAI and Google Gemini

**Usage**:
```
/skill agent-builder
```

**What it does**:
- Creates agent with Gemini integration
- Integrates MCP tools
- Implements conversation management
- Adds natural language understanding

**Phases**: III+

---

### Cloud & DevOps

#### `cloud-devops/SKILL.md`
**Purpose**: Deploy to cloud Kubernetes with Kafka and Dapr

**Usage**:
```
/skill cloud-deployment provider=digitalocean
/skill cloud-deployment provider=gke
/skill cloud-deployment provider=aks
```

**What it does**:
- Provisions cloud Kubernetes cluster
- Deploys Kafka (Strimzi or Redpanda Cloud)
- Integrates Dapr building blocks
- Implements event-driven architecture
- Sets up CI/CD pipeline with GitHub Actions

**Phases**: V

---

### Development

#### `development/SKILL.md`
**Purpose**: Generate comprehensive test suites

**Usage**:
```
/skill test-generator feature=todo-crud
```

**What it does**:
- Analyzes acceptance criteria from spec
- Generates unit tests (pytest, Jest)
- Creates integration tests (API, database)
- Builds E2E tests (Playwright)
- Sets up test infrastructure and CI

**Phases**: II+

---

## How to Use Skills

### Via Slash Command (If Integrated)
```
/skill <skill-name> <parameters>
```

### Via Claude Code Directly
Just mention the skill in your prompt:
```
"Use the kubernetes-setup skill to deploy to Minikube"
```

### Via Task Tool (Advanced)
```python
Task(
    subagent_type="kubernetes-setup",
    description="Setup local K8s",
    prompt="Set up Minikube environment for Phase IV"
)
```

---

## Skill Categories

| Category | Skills | Purpose |
|----------|--------|---------|
| **Phase Management** | phase-transition | Guide architectural phase upgrades |
| **Infrastructure** | kubernetes-setup | K8s deployment (local & cloud) |
| **AI & MCP** | mcp-builder, agent-builder | Build MCP servers and AI agents |
| **Cloud & DevOps** | cloud-deployment | Cloud K8s + Kafka + Dapr |
| **Development** | test-generator | Generate test suites |

---

## Creating New Skills

### Skill Template Structure

```markdown
# Skill Name

**Type**: Agent Skill
**Category**: [Phase Management | Infrastructure | AI & MCP | Cloud & DevOps | Development]
**Phases**: [Phase numbers this skill applies to]

---

## Purpose

[1-2 sentence description of what this skill does]

---

## Skill Invocation

```
/skill skill-name parameter=value
```

---

## What This Skill Does

1. **Step 1 Name**
   - Detail 1
   - Detail 2

2. **Step 2 Name**
   - Detail 1
   - Detail 2

[... more steps ...]

---

## Success Criteria

[What indicates this skill completed successfully]

1. ✅ Criterion 1
2. ✅ Criterion 2

---

## Deliverables

When this skill completes, you'll have:

1. ✅ Deliverable 1
2. ✅ Deliverable 2

---

**Skill Version**: 1.0.0
**Created**: YYYY-MM-DD
**Hackathon Points**: [How this contributes to scoring]
**Phase**: [Applicable phases]
```

### Skill Naming Conventions

- Use kebab-case: `kubernetes-setup.md`
- Be descriptive: `cloud-deployment.md` not `deploy.md`
- Group by category in subdirectories

### Skill Documentation Standards

- **Clear Purpose**: One-sentence summary
- **Explicit Steps**: What the skill does, step-by-step
- **Success Criteria**: How to know it worked
- **Examples**: Show usage and expected output
- **Deliverables**: What artifacts are created

---

## Skill Integration with Spec-Kit Plus

Skills complement the Spec-Kit Plus workflow:

```
User Request
    ↓
/sp.specify → Create specification
    ↓
/sp.plan → Generate plan
    ↓
/sp.tasks → Break into tasks
    ↓
/sp.implement → Execute tasks
    ↓
/skill <name> → Use specialized skill for complex operations
    ↓
/sp.adr → Document architectural decisions
    ↓
/sp.phr → Create prompt history record
```

---

## Hackathon Bonus Points

### +200 Points: Reusable Intelligence
- Create custom agent skills
- Show skills being reused across features
- Document skill usage in PHRs

### +200 Points: Cloud-Native Blueprints
- Use infrastructure skills (kubernetes-setup, cloud-deployment)
- Create deployment blueprints
- Demonstrate spec-driven infrastructure

**Tip**: The skills in this directory are designed to help you earn these bonus points!

---

## Maintenance

### Adding a New Skill
1. Create markdown file in appropriate category directory
2. Follow the skill template structure
3. Add entry to this README
4. Test the skill thoroughly
5. Document in AGENTS.md if needed

### Updating a Skill
1. Increment version number
2. Document changes in skill file
3. Update this README if needed
4. Create ADR for significant changes

---

## Directory Structure

```
.claude/skills/
├── README.md (this file)
├── phase-management/
│   └── SKILL.md
├── infrastructure/
│   └── SKILL.md
├── ai-mcp/
│   ├── SKILL.md
│   └── agent-builder/
│       └── SKILL.md
├── cloud-devops/
│   └── SKILL.md
├── development/
│   └── SKILL.md
└── skill-creator/
    └── SKILL.md
```

---

## Related Files

- **AGENTS.md**: Agent behavior rules and constraints
- **CLAUDE.md**: Claude Code instructions (references AGENTS.md)
- **.claude/commands/**: Slash commands for Spec-Kit workflow
- **.specify/**: Templates and scripts for spec-driven development

---

## Resources

- [Claude Code Documentation](https://claude.com/product/claude-code)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Dapr Documentation](https://docs.dapr.io/)

---

**Last Updated**: 2025-12-22
**Project**: Evolution of TODO - PIAIC Hackathon II
**Total Skills**: 40+

---

## Bonus Points Status: ✅ EARNED (+200)

### Reusable Intelligence: Complete
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Create custom agent skills | ✅ | 40+ skills in .claude/skills/ |
| Show skills being reused | ✅ | Used across Phases I-III |
| Document skill usage | ✅ | PHRs and specs reference skills |
| **Bonus Points** | **+200** | **Full bonus earned** |

### Cloud-Native Blueprints: Pending
| Requirement | Status | Notes |
|-------------|--------|-------|
| Infrastructure skills | ⏳ | Ready for Phase IV/V |
| Deployment blueprints | ⏳ | Ready for Phase IV/V |
| Spec-driven infrastructure | ⏳ | Ready for Phase IV/V |
| **Bonus Points** | **0** | **Unlocked in Phase IV** |

---

## Key Skills Used in Phases I-III

### Phase I: Console App
- `cli-builder` - Built Python console app with Rich UI
- `console-ui-builder` - Enhanced terminal interface

### Phase II: Full-Stack Web
- `backend-scaffolder` - Generated FastAPI + SQLModel backend
- `frontend-component` - Built Next.js UI components
- `crud-builder` - Task CRUD operations

### Phase III: AI Chatbot
- `ai-chatbot-builder` - Built AI assistant with MCP tools
- `chatkit-integrator` - Chat interface implementation
- `i18n-bilingual` - English/Urdu language support
- `mcp-tool-maker` - Created 5 MCP tools
- `stateless-agent-enforcer` - Stateless architecture validation
