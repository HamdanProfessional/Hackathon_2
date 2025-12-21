---
name: workflow-librarian-core
description: Manages documentation, version control, translations, and local development setup. Handles git operations, documentation generation, i18n support for bilingual interfaces, and development environment configuration. Ensures proper workflow management and knowledge preservation across all phases of the Todo app evolution.
---

# Workflow Librarian Core

## Quick Start

```python
# Initialize workflow management
from workflow_librarian_core import WorkflowLibrarian

librarian = WorkflowLibrarian(
    project_name="todo-evolution",
    repo_url="https://github.com/user/todo-evolution"
)

# Set up complete workflow
await librarian.setup_workflow(
    git_config=True,
    documentation=True,
    i18n_support=True,
    development_env=True
)
```

## Core Capabilities

### 1. Git Workflow Management
```python
class GitManager:
    """Manages git operations with conventional commits."""

    async def commit_with_convention(self, message: str, changes: List[str]):
        """Create conventional commit."""
        # Parse message for type
        commit_type = self.parse_commit_type(message)

        # Format commit message
        formatted_message = f"{commit_type}: {message}"

        # Stage changes
        await self.run_git(["add"] + changes)

        # Create commit
        await self.run_git(["commit", "-m", formatted_message])

        return CommitResult(
            hash=await self.get_current_hash(),
            message=formatted_message
        )

    async def create_feature_branch(self, feature_name: str):
        """Create feature branch with convention."""
        branch_name = f"feature/{feature_name}"
        await self.run_git(["checkout", "-b", branch_name])
        return branch_name

    async def sync_with_main(self):
        """Sync current branch with main."""
        await self.run_git(["fetch", "origin"])
        await self.run_git(["merge", "origin/main"])
        return True
```

### 2. Documentation Generation
```python
class DocumentationGenerator:
    """Generates comprehensive documentation."""

    def generate_api_docs(self, fastapi_app):
        """Generate API documentation from FastAPI app."""
        return {
            "openapi": fastapi_app.openapi(),
            "postman": self.generate_postman_collection(fastapi_app),
            "readme": self.generate_readme()
        }

    def generate_phase_documentation(self, phase: int):
        """Generate documentation for specific phase."""
        docs = {
            "architecture": self.create_architecture_diagram(phase),
            "setup": self.create_setup_guide(phase),
            "usage": self.create_usage_examples(phase),
            "deployment": self.create_deployment_guide(phase)
        }

        # Write to docs directory
        for doc_type, content in docs.items():
            self.write_markdown(f"docs/phase{phase}/{doc_type}.md", content)

        return docs

    def create_migration_guide(self, from_phase: int, to_phase: int):
        """Create migration guide between phases."""
        guide = f"""
# Migration Guide: Phase {from_phase} → Phase {to_phase}

## Overview
This guide helps migrate your Todo app from Phase {from_phase} to Phase {to_phase}.

## Prerequisites
- Complete Phase {from_phase} implementation
- Backup current data
- Update dependencies

## Migration Steps
{self._generate_migration_steps(from_phase, to_phase)}

## Validation
{self._generate_validation_steps(to_phase)}

## Rollback
{self._generate_rollback_instructions(to_phase)}
        """

        return guide
```

### 3. i18n Bilingual Support (English/Urdu)
```typescript
// Phase III i18n integration
import { NextIntlClientProvider } from 'next-intl';
import { notFound } from 'next/navigation';

// Language detector middleware
export default async function LocaleMiddleware(request) {
  const pathname = request.nextUrl.pathname;

  // Check if there is any supported locale in the pathname
  const pathnameIsMissingLocale = ['/en', '/ur'].every(
    (locale) => !pathname.startsWith(`/${locale}/`)
  );

  // Redirect if there is no locale
  if (pathnameIsMissingLocale) {
    const locale = 'en'; // Default to English
    return NextResponse.redirect(
      new URL(`/${locale}${pathname}`, request.url)
    );
  }
}

// Urdu translations
const urTranslations = {
  "tasks": "ٹاسک",
  "add_task": "ٹاسک شامل کریں",
  "complete_task": "ٹاسک مکمل کریں",
  "delete_task": "ٹاسک حذف کریں",
  "chat": "بات چیت",
  "hello": "السلام علیکم",
  "how_can_help": "میں آپ کی کس مدد کر سکتا ہوں؟"
};

// RTL support for Urdu
export function UrduLayout({ children }) {
  return (
    <html lang="ur" dir="rtl">
      <body className="font-urdu">
        {children}
      </body>
    </html>
  );
}
```

### 4. Development Environment Setup
```python
class DevEnvironmentSetup:
    """Sets up local development environment."""

    async def setup_phase_1(self):
        """Setup for console app development."""
        # Initialize UV project
        await self.run_command("uv init todo-console")
        await self.run_command("uv add click rich")

        # Create virtual environment
        await self.run_command("uv venv")

        # Create development scripts
        self.create_dev_scripts_phase1()

        # Setup pre-commit hooks
        await self.setup_git_hooks()

    async def setup_phase_2(self):
        """Setup for full-stack development."""
        # Frontend setup
        await self.setup_nextjs()

        # Backend setup
        await self.setup_fastapi()

        # Database setup
        await self.setup_neon_db()

        # Environment configuration
        self.create_env_files()

    async def setup_phase_3(self):
        """Setup for AI chatbot development."""
        # Install AI dependencies
        await self.run_command("uv add openai agents-sdk mcp")

        # Setup MCP server
        await self.setup_mcp_server()

        # Configure OpenAI
        self.setup_openai_config()

    def create_dev_scripts_phase1(self):
        """Create development scripts for Phase I."""
        scripts = {
            "run": "uv run python main.py",
            "test": "uv run pytest",
            "lint": "uv run ruff check .",
            "format": "uv run ruff format .",
            "type-check": "uv run mypy ."
        }

        # Write to package.json equivalent for Python
        with open("pyproject.toml", "a") as f:
            f.write("\n[tool.poetry.scripts]\n")
            for name, command in scripts.items():
                f.write(f'{name} = "{command}"\n')
```

## Documentation Structure

### docs/ Directory Organization
```
docs/
├── overview.md              # Project overview
├── phases/
│   ├── phase-1-console.md    # Phase I documentation
│   ├── phase-2-web.md        # Phase II documentation
│   └── phase-3-ai.md         # Phase III documentation
├── api/
│   ├── openapi.yaml          # OpenAPI specification
│   ├── postman-collection.json # Postman collection
│   └── mcp-tools.md          # MCP tool documentation
├── architecture/
│   ├── design-decisions.md   # ADRs
│   ├── system-diagrams.md    # Architecture diagrams
│   └── evolution-path.md     # Phase evolution guide
├── i18n/
│   ├── english.md            # English localization
│   ├── urdu.md               # Urdu localization
│   └── translation-guide.md  # Translation guidelines
└── deployment/
    ├── local-setup.md        # Local development setup
    ├── production.md          # Production deployment
    └── troubleshooting.md     # Common issues
```

### Automated Documentation Updates
```python
class DocumentationUpdater:
    """Automatically updates documentation."""

    async def update_api_docs(self):
        """Update API documentation from code."""
        # Extract endpoints from FastAPI
        endpoints = self.extract_endpoints()

        # Generate OpenAPI spec
        openapi_spec = self.generate_openapi(endpoints)

        # Update documentation
        await self.write_file("docs/api/openapi.yaml", openapi_spec)

        # Generate examples
        examples = self.generate_endpoint_examples(endpoints)
        await self.write_file("docs/api/examples.md", examples)

    async def update_phase_docs(self):
        """Update phase-specific documentation."""
        for phase in [1, 2, 3]:
            # Collect phase information
            phase_info = await self.collect_phase_info(phase)

            # Generate documentation
            docs = self.generate_phase_documentation(phase, phase_info)

            # Write to docs directory
            await self.write_phase_docs(phase, docs)
```

## Git Workflow Implementation

### Branch Protection Rules
```yaml
# .github/branch-protection.yml
protection_rules:
  main:
    required_status_checks:
      strict: true
      contexts:
        - "quality-check"
        - "tests-pass"
        - "security-scan"
    required_pull_request_reviews:
      required_approving_review_count: 1
    restrictions:
      users: []
      teams: ["core-developers"]
```

### Automated Commit Validation
```python
class CommitValidator:
    """Validates commit messages."""

    CONVENTIONAL_COMMIT_PATTERN = re.compile(
        r"^(build|ci|docs|feat|fix|perf|refactor|style|test|chore)"
        r"(\(.+\))?: .{1,50}"
        r"(\n\n.{1,}.)*$",
        re.MULTILINE
    )

    def validate_commit_message(self, message: str) -> ValidationResult:
        """Validate commit against conventional commits."""
        if not self.CONVENTIONAL_COMMIT_PATTERN.match(message):
            return ValidationResult(
                valid=False,
                errors=[
                    "Commit must follow conventional commit format",
                    "Example: feat: add task creation endpoint"
                ]
            )

        return ValidationResult(valid=True)

    def get_commit_stats(self, since: str = "1 week ago"):
        """Get commit statistics."""
        # Run git command
        result = subprocess.run(
            ["git", "log", "--oneline", "--since", since],
            capture_output=True,
            text=True
        )

        commits = result.stdout.split('\n')
        stats = defaultdict(int)

        for commit in commits:
            if commit:
                commit_type = commit.split(':')[0]
                stats[commit_type] += 1

        return dict(stats)
```

## Translation Management

### Message Extraction
```python
class MessageExtractor:
    """Extracts messages for translation."""

    def extract_messages(self, source_dir: str) -> TranslationKeys:
        """Extract all translatable messages."""
        messages = {}

        # Extract from Python files
        for py_file in glob(f"{source_dir}/**/*.py"):
            messages.update(self.extract_from_python(py_file))

        # Extract from TypeScript files
        for ts_file in glob(f"{source_dir}/**/*.{ts,tsx}"):
            messages.update(self.extract_from_typescript(ts_file))

        return messages

    def extract_from_python(self, file_path: str) -> dict:
        """Extract messages from Python files."""
        messages = {}
        with open(file_path, 'r') as f:
            content = f.read()

        # Find translatable strings
        matches = re.findall(r'_\(["\']([^"\']+)["\']', content)
        for match in matches:
            key = match.lower().replace(' ', '_')
            messages[key] = match

        return messages
```

### Translation Files
```json
// locales/en.json
{
  "tasks": {
    "add_task": "Add Task",
    "complete_task": "Complete Task",
    "delete_task": "Delete Task",
    "edit_task": "Edit Task"
  },
  "messages": {
    "welcome": "Welcome to Todo App!",
    "task_created": "Task created successfully",
    "task_completed": "Task marked as complete",
    "task_deleted": "Task deleted successfully"
  },
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "confirm": "Confirm",
    "loading": "Loading...",
    "error": "Error"
  }
}

// locales/ur.json
{
  "tasks": {
    "add_task": "ٹاسک شامل کریں",
    "complete_task": "ٹاسک مکمل کریں",
    "delete_task": "ٹاسک حذف کریں",
    "edit_task": "ٹاسک ترمیم کریں"
  },
  "messages": {
    "welcome": "ٹوڈو ایپ میں خوش آمدید!",
    "task_created": "ٹاسک کامیابی سے بنایا گیا",
    "task_completed": "ٹاسک مکمل کے طور پر نشان زد",
    "task_deleted": "ٹاسک کامیابی سے حذف ہو گیا"
  },
  "common": {
    "save": "محفوظ کریں",
    "cancel": "منسوخ کریں",
    "confirm": "تصدیق کریں",
    "loading": "لوڈ ہو رہا ہے...",
    "error": "خرابی"
  }
}
```

## Environment Configuration

### .env Templates
```bash
# .env.template - Copy to .env.local
# Phase I (Console)
LOG_LEVEL=INFO

# Phase II (Web)
DATABASE_URL=postgresql://user:pass@localhost:5432/todo
SECRET_KEY=your-secret-key-here
NEXTAUTH_SECRET=your-nextauth-secret

# Phase III (AI)
OPENAI_API_KEY=your-openai-api-key
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key

# Common
NODE_ENV=development
DEBUG=true
```

### Development Scripts
```python
# scripts/dev_setup.py
import os
import subprocess

def create_env_files():
    """Create environment files for each phase."""
    phases = ["phase1", "phase2", "phase3"]

    for phase in phases:
        env_file = f".env.{phase}"
        if not os.path.exists(env_file):
            subprocess.run(["cp", ".env.template", env_file])
            print(f"Created {env_file}")

def setup_pre_commit():
    """Setup pre-commit hooks."""
    subprocess.run(["pip", "install", "pre-commit"])
    subprocess.run(["pre-commit", "install"])

if __name__ == "__main__":
    create_env_files()
    setup_pre_commit()
```

## Integration with Other Agents

### With Spec-Architect
- Documents architecture decisions
- Maintains ADRs
- Tracks specification changes

### With Quality-Enforcer
- Validates commit messages
- Enforces documentation standards
- Checks i18n compliance

### With System-Integrator
- Provides setup instructions
- Documents integration patterns
- Manages environment configurations

## Best Practices

### Documentation
1. **Keep it current** - Auto-update when code changes
2. **Be comprehensive** - Cover all aspects
3. **Use examples** - Show, don't just tell
4. **Version control** - Track documentation changes
5. **Multiple formats** - Support various output formats

### Git Workflow
1. **Conventional commits** - Standardize commit messages
2. **Feature branches** - Isolate development
3. **Pull requests** - Code review process
4. **Automated checks** - Ensure quality
5. **Semantic versioning** - Clear versioning

### Translation
1. **Maintain consistency** - Same meaning across languages
2. **Cultural context** - Consider cultural nuances
3. **RTL support** - Proper layout for right-to-left
4. **Fallbacks** - Default language support
5. **Community review** - Native speaker validation