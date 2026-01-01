# ADR Example

Architecture Decision Record for a technical choice.

```markdown
# ADR-001: Use SQLModel for Database ORM

**Status**: Accepted
**Date**: 2025-01-15
**Decision Makers**: Development Team
**Tags**: #backend #database #orm

---

## Context

Our application needs an ORM for database operations while maintaining
type safety with Pydantic for FastAPI integration.

**Problem Statement**:
We need a database layer that:
1. Works seamlessly with FastAPI and Pydantic
2. Provides type safety with Python type hints
3. Supports migrations with Alembic
4. Is maintainable and well-documented

**Constraints**:
- Must support PostgreSQL
- Must integrate with FastAPI's dependency injection
- Must support async operations (future requirement)

---

## Decision

Use **SQLModel** as the database ORM.

**Chosen Option**: SQLModel (built on SQLAlchemy + Pydantic)

**Rationale**:
- Native Pydantic integration - models are Pydantic models
- SQLAlchemy under the hood - battle-tested and mature
- Type hints throughout - excellent IDE support
- Alembic compatible - proven migration strategy
- FastAPI first-class citizen - designed for this use case

---

## Options Considered

### Option 1: SQLModel (CHOSEN)

**Description**:
Pydantic models that are also SQLAlchemy models.

**Pros**:
- Single model definition for API and database
- Native FastAPI integration
- Excellent TypeScript support
- Active development by FastAPI creator

**Cons**:
- Relatively new (but stable)
- Smaller community than pure SQLAlchemy

**Cost/Complexity**: Low

---

### Option 2: SQLAlchemy + Pydantic (Separate)

**Description**:
Use SQLAlchemy for database, separate Pydantic schemas for API.

**Pros**:
- SQLAlchemy is mature and battle-tested
- Large community and resources
- More control over database layer

**Cons**:
- Duplicate model definitions (DRY violation)
- More boilerplate code
- Synchronization overhead between models

**Cost/Complexity**: Medium

---

### Option 3: Pure Pydantic with `pydantic-connect`

**Description**:
Use Pydantic with database connectors.

**Pros**:
- Pydantic-first approach
- Minimal boilerplate

**Cons**:
- Less mature ecosystem
- Limited migration support
- Less control over database operations

**Cost/Complexity**: Medium

---

## Consequences

### Positive

- **Reduced Boilerplate**: One model definition serves both API and database
- **Type Safety**: End-to-end type hints from database to API
- **Fast Integration**: Works out-of-the-box with FastAPI
- **Maintainability**: Less code to maintain and keep in sync

### Negative

- **Learning Curve**: Team needs to learn SQLModel patterns
- **Newer Technology**: Less community resources than pure SQLAlchemy

### Neutral

- **Migration Path**: Can fall back to SQLAlchemy if needed
- **Performance**: Similar to SQLAlchemy (same underlying engine)

---

## Implementation Notes

**Immediate Actions**:
1. Install `sqlmodel>=0.0.8`
2. Define all models in `backend/app/models/`
3. Create Pydantic schemas in `backend/app/schemas/`
4. Generate Alembic migrations

**Migration Path**:
- New project - start with SQLModel
- Existing SQLAlchemy - gradually migrate models

**Testing Strategy**:
- Unit tests for model validation
- Integration tests for database operations
- Migration tests for schema changes

**Rollback Plan**:
- SQLModel is compatible with SQLAlchemy
- Can use raw SQLAlchemy if needed
- Models can be extracted to separate layers

---

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI SQLModel Tutorial](https://fastapi.tiangolo.com/tutorial/sqlmodel/)
- ADR-000: Example ADR template
```
