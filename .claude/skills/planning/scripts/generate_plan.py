#!/usr/bin/env python3
"""Generate implementation plan from spec."""
import argparse
from pathlib import Path
import re

PLAN_TEMPLATE = """# Implementation Plan: {feature_name}

**Spec**: @specs/{feature_slug}/spec.md
**Phase**: {phase}
**Estimated Complexity**: {complexity}
**Timeline**: {timeline}

---

## Overview

{overview}

**Success Criteria**:
{success_criteria}

---

## Architecture

### Component Diagram

```
{component_diagram}
```

### Component Responsibilities

{component_responsibilities}

---

## Data Model

### Tables Required

{data_model}

---

## API Design

### Endpoints

{api_design}

---

## Implementation Tasks

{tasks}

---

## Testing Strategy

{testing_strategy}

---

## Risks & Mitigations

{risks}

---

## Success Metrics

{success_metrics}
"""

def generate_plan(spec_file: Path, output_dir: Path):
    """Generate implementation plan from spec."""
    content = spec_file.read_text()

    # Extract info from spec
    feature_name = spec_file.stem.replace("-", " ").title()
    feature_slug = spec_file.stem

    # Parse sections
    overview = extract_section(content, "Overview")
    user_stories = extract_section(content, "User Stories")
    acceptance_criteria = extract_section(content, "Acceptance Criteria")
    data_model = extract_section(content, "Data Model")
    api_endpoints = extract_section(content, "API Endpoints")

    # Generate plan
    plan = PLAN_TEMPLATE.format(
        feature_name=feature_name,
        feature_slug=feature_slug,
        phase="II",
        complexity="Moderate",
        timeline="2 weeks",
        overview=overview,
        success_criteria=format_acceptance(acceptance_criteria),
        component_diagram="""
Frontend (Next.js)
       |
       v
Backend API (FastAPI)
       |
       v
Database (PostgreSQL)
        """.strip(),
        component_responsibilities=format_components(),
        data_model=data_model,
        api_design=format_api(api_endpoints),
        tasks=format_tasks(extract_tasks(user_stories)),
        testing_strategy="""
**Unit Tests**: Test each endpoint independently
**Integration Tests**: Test request/response cycle
**E2E Tests**: Test complete user workflows
        """.strip(),
        risks="""
**Risk 1**: Database migration complexity
**Mitigation**: Test migration on staging first

**Risk 2**: API response time
**Mitigation**: Add database indexes, implement caching
        """.strip(),
        success_metrics="""
- [ ] All acceptance criteria met
- [ ] API response time < 200ms
- [ ] 80%+ code coverage
        """.strip()
    )

    # Write plan
    output_file = output_dir / "docs" / "plans" / f"{feature_slug}-plan.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(plan)

    print(f"Generated plan: {output_file}")

def extract_section(content: str, section: str) -> str:
    """Extract a section from markdown content."""
    pattern = rf"## {section}.*?\n(.*?)(?=\n## |\n*$|---)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""

def format_acceptance(criteria: str) -> str:
    """Format acceptance criteria as checklist."""
    lines = []
    for line in criteria.split("\n"):
        line = line.strip()
        if line.startswith("-") or line.startswith("*"):
            lines.append(f"- {line[1:].strip()}")
    return "\n".join(lines)

def format_components() -> str:
    """Format component responsibilities."""
    return """
**1. Frontend**:
- Location: `frontend/app/[feature]/`
- Key Files:
  - `page.tsx`
  - `components/[Component].tsx`
  - `lib/[feature]-api.ts`

**2. Backend**:
- Location: `backend/app/routers/[feature].py`
- Key Files:
  - `models/[feature].py`
  - `schemas/[feature].py`
  - `routers/[feature].py`
    """.strip()

def format_api(api_text: str) -> str:
    """Format API endpoints section."""
    return api_text if api_text else "### API Endpoints\n\nSee spec for details."

def format_tasks(stories: str) -> str:
    """Format implementation tasks from user stories."""
    return """
### Task 1: Database Schema
**Complexity**: Simple
**Acceptance Criteria**:
- [ ] SQLModel class created
- [ ] Migration generated
- [ ] Migration tested

### Task 2: Backend API
**Complexity**: Moderate
**Dependencies**: Task 1
**Acceptance Criteria**:
- [ ] Pydantic schemas created
- [ ] CRUD endpoints implemented
- [ ] Tests passing

### Task 3: Frontend Components
**Complexity**: Moderate
**Dependencies**: Task 2
**Acceptance Criteria**:
- [ ] Page component created
- [ ] API client implemented
- [ ] UI working end-to-end
    """.strip()

def extract_tasks(stories: str) -> list:
    """Extract tasks from user stories."""
    tasks = []
    for line in stories.split("\n"):
        if line.strip().startswith("-"):
            tasks.append(line.strip()[1:])
    return tasks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate implementation plan from spec")
    parser.add_argument("spec", help="Path to spec file")
    parser.add_argument("--output", default=".", help="Output directory")

    args = parser.parse_args()
    generate_plan(Path(args.spec), Path(args.output))
