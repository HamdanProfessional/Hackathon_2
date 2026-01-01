# Skill Creation - Evolution of TODO Edition

This guide documents how to create effective skills based on the actual patterns used in the Evolution of TODO project.

## Skill Structure

All skills follow this structure:

```
.claude/skills/<skill-name>/
├── SKILL.md                   # Main skill documentation
├── assets/
│   ├── examples/              # Real code examples from the project
│   ├── templates/             # Reusable templates (if applicable)
│   ├── scripts/               # Helper scripts (if applicable)
│   └── resources/             # External resources and best practices
└── references/                # Additional reference documentation
```

## SKILL.md Template

```markdown
# <Skill Name>

**Type**: Development / Infrastructure / Testing
**Author**: Evolution of TODO Project
**Created**: 2025-01-01
**Updated**: 2025-01-01

## Description
<Brief description of what this skill does, based on actual patterns used in the project>

## When to Use This Skill
Use this skill when:
- <Condition 1 based on project needs>
- <Condition 2 based on project needs>
- <Condition 3 based on project needs>

## Examples
See `assets/examples/` for:
- Real code examples from the Evolution of TODO project
- Patterns actually used in production
- Production-tested implementations

## Assets
- `examples/` - Code examples showing actual usage
- `templates/` - Reusable templates (if applicable)
- `scripts/` - Helper scripts (if applicable)
- `references/` - External resources and best practices

## Related Skills
- <Skill 1> - Related to this skill
- <Skill 2> - Often used together

## Files This Skill Helps With
- <File type 1>
- <File type 2>

## Project-Specific Patterns
This skill is based on the actual implementation patterns used in the Evolution of TODO project, which uses:
- <Technology 1>
- <Technology 2>
- <Technology 3>
```

## Example Skills from the Project

### backend-builder

**Purpose**: Generate FastAPI CRUD operations with async/await, SQLModel, and JWT auth

**When to Use**:
- Creating new API endpoints
- Scaffolding new models with CRUD
- After creating a feature spec

**Key Patterns**:
- Async/await with AsyncSession
- SQLModel with selectinload for relationships
- JWT authentication via get_current_user
- BackgroundTasks for non-blocking operations
- User isolation in all queries

**Files Generated**:
- `app/models/<model>.py` - SQLModel model
- `app/schemas/<model>.py` - Pydantic schemas
- `app/api/<model>.py` - FastAPI router
- `app/crud/<model>.py` - Database operations

### frontend

**Purpose**: Build Next.js 16+ App Router components with TypeScript and Tailwind CSS

**When to Use**:
- Building UI for new features
- Creating React components
- After backend API is ready

**Key Patterns**:
- Next.js App Router with Server/Client Components
- shadcn/ui components with dark theme
- API client with axios and interceptors
- Runtime config.json for API URL
- TypeScript interfaces for type safety

**Files Generated**:
- `app/<feature>/page.tsx` - Next.js page
- `components/<feature>/*.tsx` - React components
- `lib/<feature>-api.ts` - API client methods
- `lib/types.ts` - TypeScript interfaces

### qa-tester

**Purpose**: Create comprehensive tests for backend and frontend

**When to Use**:
- Testing new features
- Creating test coverage
- Validating API contracts

**Key Patterns**:
- pytest for backend testing
- AsyncSession with test database
- Fixtures for test data
- JSON reports for E2E tests
- Coverage reporting

**Files Generated**:
- `tests/test_<feature>.py` - Test files
- `tests/conftest.py` - Test fixtures
- `chatbot_test_report.json` - E2E test reports

### deployment

**Purpose**: Deploy to Docker Compose, Kubernetes, or Vercel

**When to Use**:
- Setting up local development
- Deploying to Kubernetes
- Deploying to production

**Key Patterns**:
- Multi-stage Dockerfiles
- Docker Compose for local dev
- Kubernetes with Helm charts
- DigitalOcean container registry
- Health checks and probes

**Files Generated**:
- `Dockerfile` - Container images
- `docker-compose.yml` - Local development
- `k8s/` - Kubernetes manifests
- `helm/` - Helm charts

### dapr-events

**Purpose**: Set up event-driven architecture with Dapr pub/sub

**When to Use**:
- Publishing events after DB operations
- Subscribing to events
- Email notifications with background tasks

**Key Patterns**:
- Fire-and-forget event publishing
- BackgroundTasks for async operations
- Event logging to database
- Dapr HTTP API calls

**Files Generated**:
- `app/services/event_publisher.py` - Event publisher
- `app/subscribers/` - Event subscribers
- `dapr/components/` - Dapr components

## Creating a New Skill

### Step 1: Identify Patterns

Look at the codebase for repeated patterns that could be abstracted:

```bash
# Find common patterns
grep -r "async def create_" app/crud/
grep -r "class APIRouter" app/api/
grep -r "export default function" frontend/app/
```

### Step 2: Extract Examples

Create example files showing the actual patterns:

```
.claude/skills/new-skill/
└── assets/examples/
    └── pattern-example.md  # Real code from project
```

### Step 3: Create Templates (if applicable)

If the pattern involves generating code, create a template:

```
.claude/skills/new-skill/
└── assets/templates/
    └── template.py  # Generic template
```

### Step 4: Document References

Add reference documentation:

```
.claude/skills/new-skill/
└── references/
    └── best-practices.md  # How to use the pattern
```

### Step 5: Write SKILL.md

Create the main skill documentation following the template.

## Skill Categories

### Development Skills
- **backend-builder**: FastAPI CRUD scaffolding
- **frontend**: Next.js component building
- **fastapi-crud**: Generate CRUD endpoints
- **mcp-tool-maker**: Create MCP tools for AI agents

### Infrastructure Skills
- **deployment**: Docker, Kubernetes, Helm
- **cloud-deployer**: Vercel, Railway, DOKS
- **dapr-events**: Event-driven architecture

### Testing Skills
- **qa-tester**: E2E and integration tests
- **test-builder**: Unit and component tests
- **integration-tester**: API contract testing

### Planning Skills
- **architecture-planner**: System design
- **task-breaker**: Work decomposition
- **spec-architect**: Spec-Kit Plus specifications

### Utility Skills
- **code-quality**: Linting, formatting, type checking
- **db-migration-wizard**: Alembic migrations
- **git-committer**: Conventional commits

## Best Practices for Skills

1. **Based on Real Code**: All examples should be from the actual project
2. **Tested Patterns**: Only include patterns that work in production
3. **Complete Examples**: Show full, working code
4. **Context Provided**: Explain when and why to use each pattern
5. **Updated Regularly**: Keep skills in sync with codebase changes
6. **Cross-Referenced**: Link to related skills
7. **Clear Documentation**: Explain the "why" not just the "how"

## Example: Creating a New Skill

Let's say we want to create a skill for "email-notifier":

```bash
# Create skill directory
mkdir -p .claude/skills/email-notifier/assets/examples
mkdir -p .claude/skills/email-notifier/assets/templates
mkdir -p .claude/skills/email-notifier/references

# Create SKILL.md
cat > .claude/skills/email-notifier/SKILL.md << 'EOF'
# Email Notifier

**Type**: Development
**Author**: Evolution of TODO Project
**Created**: 2025-01-01

## Description
Sends email notifications for task events (created, updated, completed, deleted) using Gmail API.

## When to Use This Skill
Use this skill when:
- Adding email notifications to new features
- Setting up Gmail OAuth integration
- Creating background email tasks

## Examples
See `assets/examples/gmail-integration.md` for the actual implementation.

## Assets
- `examples/gmail-integration.md` - Full Gmail integration example
- `templates/email-template.html` - Email HTML template
- `references/email-providers.md` - Comparison of email providers
EOF

# Create example file
cat > .claude/skills/email-notifier/assets/examples/gmail-integration.md << 'EOF'
# Gmail Integration Example

## Setup

1. Create OAuth credentials
2. Generate token
3. Configure environment variables

## Code

```python
# See backend/app/utils/email_notifier.py for full implementation
```
EOF
```

## Maintaining Skills

As the codebase evolves:

1. **Update Examples**: When patterns change, update the examples
2. **Add New Patterns**: When new patterns emerge, add new skills
3. **Deprecate Old Skills**: When patterns become obsolete, mark skills as deprecated
4. **Sync Documentation**: Keep SKILL.md in sync with code

## Skill Quality Checklist

Before creating a skill, ensure:
- [ ] Examples are from actual production code
- [ ] Code is tested and working
- [ ] Documentation is clear and complete
- [ ] Templates are generic and reusable
- [ ] References link to official docs
- [ ] Related skills are cross-referenced
- [ ] Use cases are well-defined
- [ ] File structure matches standard

## Summary

The Evolution of TODO project's skill system is based on:
1. **Real patterns** extracted from the codebase
2. **Production-tested** code examples
3. **Complete documentation** with context
4. **Cross-references** between related skills
5. **Regular updates** to stay in sync

This ensures that when you use a skill, you're getting patterns that actually work in the project.
