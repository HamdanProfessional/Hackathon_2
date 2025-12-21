# Todo Evolution Project Constitution

## Purpose
This constitution serves as the source of truth for the Todo Evolution hackathon project. All architectural decisions, development practices, and technical choices must align with these principles.

## Core Principles

### 1. Spec-Driven Development (SDD)
- **Rule**: No code shall be written without a corresponding specification
- **Implementation**: All development follows: Specify → Plan → Tasks → Implement
- **Enforcement**: If code generation is incorrect, the specification must be refined
- **Golden Rule**: **"You cannot write code manually. You must refine the Spec until Claude Code generates the correct output."**

### 2. Cloud-Native First
- **Design Principle**: All architectures must be deployable to cloud environments
- **State Management**: Stateless services wherever possible
- **Scalability**: Horizontal scalability must be considered from Phase I
- **Observability**: Logging, monitoring, and tracing are mandatory

### 3. Stateless AI Architecture
- **AI Agents**: Must maintain no in-memory conversation state
- **Context Loading**: All conversation context loaded from database per request
- **Scalability**: AI services must support horizontal scaling
- **Tenancy**: Proper tenant isolation is mandatory

## Technology Stack Constitution

### Backend Stack
```yaml
Language: Python 3.13+ (Latest stable)
Framework: FastAPI (Async-first)
ORM: SQLModel (Type-safe SQL on top of SQLAlchemy)
Database: Neon DB (Serverless PostgreSQL)
Migrations: Alembic
Authentication: Better Auth (JWT-based)
Package Manager: UV (Ultra-fast package management)
```

### Frontend Stack
```yaml
Framework: Next.js 16 (App Router only)
Language: TypeScript (Strict mode)
Styling: Tailwind CSS (Utility-first)
UI Components: OpenAI ChatKit (For Phase III)
State Management: Server components + React hooks
```

### AI & Integration Stack
```yaml
AI SDK: OpenAI Agents SDK (Latest)
MCP: Official MCP SDK (Model Context Protocol)
Architecture: Stateless (No in-memory conversation state)
Backend Integration: Custom ChatKit backend adapter
```

### Infrastructure Stack
```yaml
Containerization: Docker
Orchestration: Kubernetes
Runtime: Dapr (for distributed systems)
Event Streaming: Kafka/Redpanda (for Phase V)
Monitoring: TBD (Cloud-native observability)
```

## Development Constraints

### Forbidden Practices
1. **No Manual Code Writing**: All code must be generated from specifications
2. **No "Vibe Coding**: Requirements must be explicit and testable
3. **No Hard-coded Secrets**: All secrets must be environment-based
4. **No In-Memory State**: AI agents must be stateless (Phase III+)
5. **No Skipping Tests**: All features must include automated tests
6. **No Unarchitectural Decisions**: All tech choices must be justified

### Mandatory Practices
1. **Specification First**: Every feature must have a detailed spec
2. **Task ID Tracking**: All work must reference specific task IDs
3. **Code Review**: All generated code must be reviewed
4. **Documentation**: All decisions must be documented
5. **Performance Validation**: All features must meet performance criteria
6. **Security Review**: All phases must pass security validation

## Phase Evolution Constitution

### Phase I: Console Application
- **Duration**: 2-3 days
- **Storage**: In-memory (demo persistence allowed)
- **UI**: Rich terminal UI using Rich library
- **Core Features**: CRUD operations on tasks
- **Package Manager**: UV must be used

### Phase II: Full Stack Web Application
- **Duration**: 3-4 days
- **Architecture**: Monorepo structure
- **Database**: Neon DB with SQLModel migrations
- **Authentication**: Better Auth with JWT
- **API**: RESTful API with OpenAPI documentation

### Phase III: AI Chatbot Interface
- **Duration**: 4-5 days
- **UI**: OpenAI ChatKit components
- **Backend**: Custom ChatKit adapter
- **AI**: OpenAI Agents SDK integration
- **Architecture**: Stateless agent system with database persistence

### Phase IV: Kubernetes Deployment
- **Duration**: 2-3 days
- **Containerization**: All services in Docker
- **Orchestration**: Kubernetes deployment
- **Configuration**: Helm charts for all services
- **Monitoring**: Basic observability stack

### Phase V: Cloud Native Event-Driven
- **Duration**: 3-4 days
- **Architecture**: Microservices with Dapr
- **Communication**: Event-driven with Kafka/Redpanda
- **Scalability**: Full cloud-native deployment
- **Observability**: Comprehensive monitoring and tracing

## Quality Standards

### Code Quality
- **Type Safety**: Strict TypeScript and Python type hints
- **Testing**: Minimum 80% code coverage required
- **Linting**: All code must pass linting rules
- **Documentation**: All public APIs must be documented

### Performance Standards
- **API Response**: < 200ms for 95th percentile
- **Database Queries**: < 50ms for indexed queries
- **Frontend Load**: < 3s initial page load
- **AI Response**: < 5s for agent responses

### Security Standards
- **Authentication**: MFA required in production
- **Authorization**: Role-based access control
- **Data Encryption**: Encryption at rest and in transit
- **Audit Trail**: All actions must be auditable

## Governance

### Change Management
- **Constitution Changes**: Require 2/3 team approval
- **Tech Stack Changes**: Must create ADR (Architecture Decision Record)
- **Phase Transitions**: Must pass phase completion criteria
- **Emergency Changes**: Must be documented retrospectively

### Compliance
- **Code Reviews**: Mandatory for all changes
- **Security Reviews**: Required for all phases
- **Performance Reviews**: Required before phase transitions
- **Documentation Reviews**: Required for all specifications

## Success Criteria

### Project Success
1. **All Phases Completed**: Evolution through all 5 phases
2. **Spec Adherence**: 100% spec-driven development
3. **Quality Gates**: All quality criteria met
4. **Performance**: All performance benchmarks achieved
5. **Team Learning**: Documentation and knowledge transfer complete

### Technical Success
1. **Scalability**: System handles projected load
2. **Maintainability**: Code is clean and documented
3. **Security**: No critical vulnerabilities
4. **Reliability**: 99.9% uptime target
5. **Observability**: Full system observability

## Enforcement

### Violation Categories
1. **Critical**: Breaking the Golden Rule or security violations
2. **Major**: Skipping quality gates or architecture violations
3. **Minor**: Documentation or minor standard violations

### Remediation
1. **Critical**: Immediate rollback and review
2. **Major**: Phase transition blocked until fixed
3. **Minor**: Must be addressed before next phase

---

**This constitution is living and may be updated with team consensus. All team members are responsible for upholding these principles and practices.**

**Last Updated**: 2025-12-21
**Version**: 1.0