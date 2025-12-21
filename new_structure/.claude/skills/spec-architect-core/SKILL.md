---
name: spec-architect-core
description: Manages the complete Spec-Driven Development workflow from Constitution to implementation. Oversees architecture planning, task breakdown, ADR creation, and ensures all development follows the Specify → Plan → Tasks → Implement lifecycle. Use for transitioning between phases, creating feature specifications, and maintaining architectural consistency across the Todo app evolution.
---

# Spec Architect Core

## Quick Start

```bash
# Full SDD workflow with hardcoded paths
cd /path/to/new_structure  # ⚠️ MANDATORY: Run from project root

# Phase I: Console App
speckit specify "Add task creation feature" --output-dir ./specs/features/
speckit plan --input-dir ./specs/features/ --output-dir ./.specify/plans/
speckit tasks --input-dir ./.specify/plans/ --output-dir ./.specify/tasks/
speckit implement --tasks-dir ./.specify/tasks/

# Phase transition
speckit specify "Migrate from console to web app" --target-phase=2
speckit plan --phase-transition --target-phase=2
```

## Project Structure Mapping

### ⚠️ MANDATORY Path Configuration
```python
import os
from pathlib import Path
from typing import Dict, Optional

class ProjectPathResolver:
    """Resolves hardcoded paths for the Todo Evolution monorepo structure."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()

        # ⚠️ MANDATORY: Hardcoded path mappings for new_structure/
        self.paths = {
            # Core specification directories
            "specs_dir": self.project_root / "specs",
            "specs_features": self.project_root / "specs" / "features",
            "specs_api": self.project_root / "specs" / "api",
            "specs_database": self.project_root / "specs" / "database",
            "specs_architecture": self.project_root / "specs" / "architecture",

            # Specify-Kit directories
            "specify_dir": self.project_root / ".specify",
            "specify_memory": self.project_root / ".specify" / "memory",
            "specify_plans": self.project_root / ".specify" / "plans",
            "specify_tasks": self.project_root / ".specify" / "tasks",
            "specify_architecture": self.project_root / ".specify" / "architecture",
            "specify_scripts": self.project_root / ".specify" / "scripts",

            # Phase-specific directories
            "phase1_src": self.project_root / "src",
            "phase2_backend": self.project_root / "backend",
            "phase2_frontend": self.project_root / "frontend",
            "phase3_ai": self.project_root / "backend" / "app" / "ai",

            # Core files
            "constitution": self.project_root / "specs" / "constitution.md",
            "requirements": self.project_root / "requirements.md",
            "claude_md": self.project_root / "CLAUDE.md",
            "global_memory": self.project_root / ".specify" / "memory" / "constitution.md"
        }

    def get_path(self, key: str) -> Path:
        """Get a path by key."""
        if key not in self.paths:
            raise ValueError(f"Unknown path key: {key}")
        return self.paths[key]

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for path_key, path_obj in self.paths.items():
            if "dir" in path_key and not path_obj.exists():
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created directory: {path_obj}")

    def validate_structure(self) -> Dict[str, bool]:
        """Validate that the project structure is correct."""
        validation = {}

        # Core required paths
        required_paths = [
            "specs_dir", "specify_dir", "constitution", "requirements"
        ]

        for path_key in required_paths:
            path_obj = self.get_path(path_key)
            validation[path_key] = path_obj.exists()

        return validation

# Global resolver instance
resolver = ProjectPathResolver()

# Usage examples
def get_specs_directory() -> Path:
    """Get the specifications directory."""
    return resolver.get_path("specs_dir")

def get_current_phase() -> int:
    """Detect current project phase."""
    if resolver.get_path("phase1_src").exists():
        return 1
    elif resolver.get_path("phase2_backend").exists():
        return 2
    elif resolver.get_path("phase3_ai").exists():
        return 3
    return 1

def get_phase_specific_paths(phase: int) -> Dict[str, Path]:
    """Get phase-specific paths."""
    phase_paths = {}
    if phase == 1:
        phase_paths["src"] = resolver.get_path("phase1_src")
    elif phase >= 2:
        phase_paths["backend"] = resolver.get_path("phase2_backend")
        phase_paths["frontend"] = resolver.get_path("phase2_frontend")
    if phase >= 3:
        phase_paths["ai"] = resolver.get_path("phase3_ai")

    return phase_paths
```

## Core Responsibilities

### 1. Constitution Management with Path Awareness
- Maintain project constitution at `specs/constitution.md`
- Define architecture values with hardcoded path references
- Set performance expectations for each phase
- Govern non-negotiable development rules with path validation

### 2. Specification Workflow with Path Resolution
Guide through the SDD lifecycle with exact path mappings:

#### Specify Phase (WHAT)
```markdown
# ⚠️ CAPTURES IN: ./specs/features/
- User stories and journeys → ./specs/features/[feature-name].md
- Functional requirements → ./specs/features/[feature-name].md
- Acceptance criteria → ./specs/features/[feature-name].md
- Business constraints → ./specs/features/[feature-name].md
- Domain rules → ./specs/features/[feature-name].md
```

#### Plan Phase (HOW)
```markdown
# ⚠️ GENERATES IN: ./.specify/plans/
- Component breakdown → ./.specify/plans/[feature-name]-plan.md
- API and schema diagrams → ./.specify/plans/[feature-name]-plan.md
- Service boundaries → ./.specify/plans/[feature-name]-plan.md
- System responsibilities → ./.specify/plans/[feature-name]-plan.md
- High-level sequencing → ./.specify/plans/[feature-name]-plan.md
```

#### Tasks Phase (BREAKDOWN)
```markdown
# ⚠️ CREATES IN: ./.specify/tasks/
- Atomic tasks → ./.specify/tasks/[feature-name]-tasks.md
- Task IDs (T-XXX format) → ./.specify/tasks/[feature-name]-tasks.md
- Dependencies → ./.specify/tasks/[feature-name]-tasks.md
- Acceptance criteria → ./.specify/tasks/[feature-name]-tasks.md
```

### 3. Task Linkage Validation
```python
import re
from pathlib import Path
from typing import Dict, List, Set

class TaskLinkageValidator:
    """Validates that every Task ID has proper linkage to Plans and Specs."""

    def __init__(self, resolver: ProjectPathResolver):
        self.resolver = resolver
        self.validation_errors = []

    def validate_all_tasks(self) -> Dict[str, any]:
        """Validate task linkage across all specifications."""
        results = {
            "total_tasks": 0,
            "linked_tasks": 0,
            "orphaned_tasks": [],
            "missing_plans": [],
            "validation_errors": self.validation_errors
        }

        # Get all task files
        tasks_dir = self.resolver.get_path("specify_tasks")
        if not tasks_dir.exists():
            self.validation_errors.append("Tasks directory does not exist")
            return results

        # Extract all task IDs
        all_task_ids = set()
        task_files = list(tasks_dir.glob("*.md"))

        for task_file in task_files:
            task_ids = self._extract_task_ids(task_file)
            all_task_ids.update(task_ids)
            results["total_tasks"] += len(task_ids)

        # Validate linkage
        for task_id in all_task_ids:
            if self._is_task_linked(task_id):
                results["linked_tasks"] += 1
            else:
                results["orphaned_tasks"].append(task_id)

        # Check for missing plans
        plans_dir = self.resolver.get_path("specify_plans")
        feature_files = list(self.resolver.get_path("specs_features").glob("*.md"))

        for feature_file in feature_files:
            feature_name = feature_file.stem
            plan_file = plans_dir / f"{feature_name}-plan.md"

            if not plan_file.exists():
                results["missing_plans"].append(feature_name)

        return results

    def _extract_task_ids(self, task_file: Path) -> Set[str]:
        """Extract task IDs from a task file."""
        task_ids = set()

        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match T-XXX pattern
            pattern = r'T-\d{3}'
            matches = re.findall(pattern, content)
            task_ids.update(matches)

        except Exception as e:
            self.validation_errors.append(f"Error reading {task_file}: {e}")

        return task_ids

    def _is_task_linked(self, task_id: str) -> bool:
        """Check if a task ID is properly linked to plans and specs."""

        # Check if task is referenced in any plan
        plans_dir = self.resolver.get_path("specify_plans")
        for plan_file in plans_dir.glob("*.md"):
            try:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if task_id in content:
                        return True
            except Exception:
                continue

        # Check if task is referenced in any spec
        specs_dir = self.resolver.get_path("specs_features")
        for spec_file in specs_dir.glob("*.md"):
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if task_id in content:
                        return True
            except Exception:
                continue

        return False

    def generate_linkage_report(self) -> str:
        """Generate a detailed linkage validation report."""
        results = self.validate_all_tasks()

        report = "# Task Linkage Validation Report\n\n"
        report += f"## Summary\n"
        report += f"- Total Tasks: {results['total_tasks']}\n"
        report += f"- Linked Tasks: {results['linked_tasks']}\n"
        report += f"- Orphaned Tasks: {len(results['orphaned_tasks'])}\n"
        report += f"- Missing Plans: {len(results['missing_plans'])}\n"
        report += f"- Validation Errors: {len(results['validation_errors'])}\n\n"

        if results['orphaned_tasks']:
            report += "## Orphaned Tasks\n"
            for task_id in results['orphaned_tasks']:
                report += f"- ❌ {task_id}\n"
            report += "\n"

        if results['missing_plans']:
            report += "## Missing Plans\n"
            for feature in results['missing_plans']:
                report += f"- ❌ {feature}\n"
            report += "\n"

        if results['validation_errors']:
            report += "## Validation Errors\n"
            for error in results['validation_errors']:
                report += f"- ❌ {error}\n"
            report += "\n"

        return report

# Usage
validator = TaskLinkageValidator(resolver)
report = validator.generate_linkage_report()
print(report)
```
```

#### Tasks Phase (BREAKDOWN)
```markdown
# Creates in speckit.tasks:
- Atomic, testable work units
- Task IDs with clear descriptions
- Preconditions and expected outputs
- Links to Specify + Plan sections
```

## Architecture Decision Records (ADRs)

### ADR Template
```markdown
# ADR-001: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
Background and problem statement

## Decision
The chosen approach with rationale

## Consequences
Effects on the system, positive and negative

## Implementation
Steps to implement the decision
```

### Common ADRs for Todo App
- ADR-001: In-memory storage for Phase I
- ADR-002: SQLModel + Neon DB for Phase II
- ADR-003: Stateless chat architecture for Phase III
- ADR-004: MCP tools for AI integration

## Phase Transition Management

### Phase I → Phase II Migration
```python
# Migration considerations:
1. Task model evolution (dataclass → SQLModel)
2. CLI commands → API endpoints
3. In-memory → Database persistence
4. Single user → Multi-user authentication
5. Console UI → Web interface
```

### Phase II → Phase III Enhancement
```python
# Enhancement checklist:
1. Add conversation models to database
2. Implement MCP server for task operations
3. Create chat endpoint with agent orchestration
4. Maintain all existing API endpoints
5. Add OpenAI ChatKit to frontend
```

## Task Generation Patterns

### CRUD Feature Tasks
```markdown
T-001: Design database model
- Input: Feature specification
- Output: SQLModel class definition
- Depends: speckit.specify §2.1

T-002: Create API endpoints
- Input: Model definition
- Output: FastAPI routes
- Depends: T-001

T-003: Build UI components
- Input: API documentation
- Output: React/Next.js components
- Depends: T-002
```

### Integration Tasks
```markdown
T-004: Frontend-backend integration
- Input: Components and endpoints
- Output: Working CRUD flow
- Depends: T-002, T-003

T-005: Authentication flow
- Input: Auth requirements
- Output: JWT integration
- Depends: T-001, T-002
```

## Quality Gates

### Before Planning
- [ ] Constitution reviewed and approved
- [ ] Requirements are complete and testable
- [ ] Dependencies and constraints identified
- [ ] Success criteria defined

### Before Implementation
- [ ] Architecture approved
- [ ] Tasks are atomic and testable
- [ ] Implementation approach validated
- [ ] Risks assessed and mitigated

### Before Completion
- [ ] All acceptance criteria met
- [ ] Tests passing (unit + integration)
- [ ] Documentation updated
- [ ] ADRs created for decisions

## Common Anti-Patterns

### Avoid These
1. **"Vibe Coding"** - Writing code without specs
2. **Task Inflation** - Creating unnecessary micro-tasks
3. **Specification Drift** - Code diverging from specs
4. **Implementation Shortcut** - Skipping validation steps
5. **Architecture Bypass** - Ignoring approved patterns

### Red Flags
- Tasks without clear acceptance criteria
- Implementation without referencing task ID
- Changes without updating specs
- New features without ADRs
- Code that violates constitution

## Integration with Other Agents

### Backend-Engineer
- Provides database schemas and API contracts
- Reviews implementation plans for technical feasibility
- Validates performance and security requirements

### Frontend-UX-Designer
- Reviews UI/UX specifications
- Validates component hierarchy
- Ensures consistency with design system

### AI-Systems-Specialist
- Defines AI integration points
- Specifies MCP tool requirements
- Validates stateless architecture

### Quality-Enforcer
- Validates test coverage requirements
- Reviews quality gates and standards
- Ensures compliance with constitution

## Documentation Standards

### Specification Quality
```markdown
# Required sections:
## User Stories
- Clear "As a user..." format
- Acceptance criteria with Given/When/Then
- Edge cases considered

## Technical Requirements
- Clear constraints and assumptions
- Performance requirements
- Security considerations
```

### Task Quality
```markdown
# Each task must have:
- Unique ID (T-XXX format)
- Clear, actionable description
- Specific inputs and outputs
- Links to relevant spec sections
- Estimated complexity (optional)
```

## Tool Integration

### With Spec-Kit Plus
```bash
# Initialize project
speckit init todo-evolution

# Set up constitution
speckit constitution --template=hackathon

# Create first feature
speckit create-feature task-crud
```

### With Claude Code
```markdown
# Reference patterns:
"Implement @specs/features/task-crud.md"
"Update @speckit.plan to add AI integration"
"Create tasks for @speckit.specify §3.2"
```

## Success Metrics

### Process Metrics
- % of features with complete specs
- Time from spec to implementation
- Number of specification changes
- Test coverage achieved

### Quality Metrics
- Defect rate reduction
- Architecture adherence score
- Team velocity improvement
- Documentation completeness

## Best Practices

### Specification Writing
1. **Be Specific** - Avoid ambiguous language
2. **Testable Criteria** - Every requirement must be verifiable
3. **Consider Edge Cases** - What happens when things go wrong?
4. **Define Done** - Clear completion criteria
5. **Version Control** - Track specification changes

### Architecture Planning
1. **Document Decisions** - Create ADRs for important choices
2. **Consider Evolution** - How will this design scale?
3. **Identify Trade-offs** - Be explicit about compromises
4. **Validate Feasibility** - Confirm technical viability
5. **Plan for Migration** - How to transition from current state

### Task Breakdown
1. **Atomic Tasks** - Each task does one thing well
2. **Clear Dependencies** - Map task relationships
3. **Testable Units** - Each task produces verifiable output
4. **Reasonable Scope** - Tasks can be completed in a session
5. **Link to Specs** - Every task references requirements