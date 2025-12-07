# In-Memory TODO CLI Constitution

<!--
  Sync Impact Report - Version 1.0.0
  =====================================
  Version Change: [new project] → 1.0.0

  Modified Principles:
  - I. Spec-Driven Development (new)
  - II. Single-File Simplicity (new)
  - III. In-Memory Only (new)
  - IV. Clean Python Standards (new)
  - V. Continuous Loop Interface (new)

  Added Sections:
  - Technology Stack
  - Development Workflow
  - Governance

  Templates Status:
  ✅ plan-template.md - reviewed, aligned with Constitution Check requirement
  ✅ spec-template.md - reviewed, aligned with functional requirements mandate
  ✅ tasks-template.md - reviewed, aligned with testable task principle

  Follow-up TODOs: None
-->

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)
**No code without spec.** Every feature MUST begin with a complete specification in `/specs/<feature>/spec.md`. Implementation may only start after the spec is written and user-approved. This ensures:
- Clear requirements before coding
- Testable acceptance criteria
- Alignment between user intent and implementation

**Rationale:** Prevents scope creep, rework, and misaligned implementations. Spec serves as contract between user and system.

### II. Single-File Simplicity
For Phase I, ALL application logic MUST reside in `src/main.py`. No additional modules, packages, or file splits are permitted.

**Exceptions:** Test files in `tests/` directory are permitted when testing is explicitly requested.

**Rationale:** Phase I is a learning foundation. Single-file constraint forces developers to understand the full system without navigating complexity. Future phases will introduce modular architecture.

### III. In-Memory Only
Phase I MUST use in-memory storage only (Python `list`, `dict`, or similar data structures). Persistence mechanisms are STRICTLY FORBIDDEN:
- NO SQL databases (PostgreSQL, MySQL, SQLite, etc.)
- NO file-based storage (JSON, CSV, pickle, etc.)
- NO external data services (Redis, cloud storage, etc.)

Data loss on application restart is EXPECTED and ACCEPTABLE for Phase I.

**Rationale:** Eliminates I/O complexity, file handling, serialization concerns. Focus is on core logic and user interaction patterns. Persistence will be introduced in future phases.

### IV. Clean Python Standards
All code MUST adhere to professional Python practices:
- **Type Hints:** All function signatures MUST include type annotations for parameters and return values
- **Docstrings:** All functions, classes, and modules MUST have clear docstrings explaining purpose, parameters, and return values
- **Error Handling:** Use proper exception handling with meaningful error messages
- **Naming:** Follow PEP 8 conventions (snake_case for functions/variables, PascalCase for classes)
- **Standard Library Only:** No external dependencies except Python 3.13+ standard library

**Rationale:** Establishes professional coding habits early. Type hints improve IDE support and catch bugs. Clean code is maintainable code.

### V. Continuous Loop Interface
The application MUST run in a continuous `while` loop until the user explicitly selects an 'Exit' or 'Quit' option. The application MUST:
- Display a menu of available operations
- Accept user input for operation selection
- Execute the selected operation
- Return to the menu (not terminate) after each operation
- Only exit when user chooses the exit option

**Rationale:** Console applications should not require re-launching for each operation. Continuous loop provides better user experience and matches standard CLI tool behavior.

### VI. Test-First When Requested
When testing is explicitly requested in the feature specification:
- Tests MUST be written FIRST in `tests/` directory
- Tests MUST FAIL before implementation begins
- Follow Red-Green-Refactor cycle: Write failing test → Implement to pass → Refactor if needed
- Use Python's `unittest` or `pytest` framework

When testing is NOT requested, tests are OPTIONAL.

**Rationale:** Test-first ensures testable design and prevents implementation bias. However, Phase I focuses on learning fundamentals, so tests are not mandatory unless specified.

## Technology Stack

**Language:** Python 3.13 or higher
**Environment:** Console (CLI) - no GUI, no web interface
**Database:** NONE - In-memory only (list/dict)
**Libraries:** Python standard library only
**Testing:** unittest or pytest (when requested)
**Version Control:** Git (standard branching and commits)

**Constraints:**
- Single file implementation (`src/main.py`)
- No external package dependencies (no pip installs beyond Python itself)
- Must run on Windows, macOS, and Linux without modification

## Development Workflow

### 1. Feature Specification
- User provides feature description
- Agent creates `/specs/<feature>/spec.md` with user scenarios and acceptance criteria
- User reviews and approves specification
- NO code written until spec approved

### 2. Planning (Optional for Complex Features)
- Agent creates `/specs/<feature>/plan.md` for architectural decisions
- Identifies edge cases and error handling requirements
- User reviews and approves plan

### 3. Implementation
- Read spec.md thoroughly before writing any code
- Implement in `src/main.py` following all constitution principles
- Test manually by running the application
- Verify all acceptance criteria from spec.md are met

### 4. Testing (When Requested)
- Write tests in `tests/` directory BEFORE implementation
- Verify tests FAIL initially
- Implement feature to make tests PASS
- Refactor if needed while keeping tests green

### 5. Documentation
- Keep code self-documenting with clear docstrings
- Update README.md with usage instructions if needed
- Create Prompt History Records (PHR) for significant interactions

## Governance

**Constitution Authority:** This constitution supersedes all other practices and preferences. When conflict arises between convenience and constitution, constitution wins.

**Amendment Process:**
1. Proposed changes MUST be documented with rationale
2. User approval required for all amendments
3. Version MUST increment following semantic versioning:
   - MAJOR: Backward incompatible principle changes (e.g., removing a principle)
   - MINOR: New principle added or significant expansion
   - PATCH: Clarifications, wording improvements, typo fixes

**Compliance:**
- All PRs and code reviews MUST verify constitution compliance
- Agent MUST refuse to implement features that violate constitution principles
- Complexity violations (e.g., multiple files in Phase I) MUST be explicitly justified in `plan.md` Complexity Tracking section and approved by user

**Phase Evolution:**
- This constitution governs Phase I only
- Future phases (Phase II: File Persistence, Phase III: Advanced Features) will amend this constitution
- Each phase transition requires explicit constitutional update

**Conflict Resolution:**
- When spec.md conflicts with constitution: Constitution wins, spec must be updated
- When implementation convenience conflicts with constitution: Constitution wins
- When user explicitly requests violation: User must approve constitutional amendment first

**Version**: 1.0.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-06
