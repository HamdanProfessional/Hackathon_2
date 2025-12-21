---
name: system-integrator-core
description: Manages system integration, setup, and phase transitions. Handles monorepo setup, UV package management, API schema synchronization, phase management, and ensures seamless communication between frontend, backend, and AI components. Orchestrates the evolution from console app to full-stack to AI-powered chatbot.
---

# System Integrator Core

## Quick Start

```python
# Initialize system integration
from system_integrator_core import SystemIntegrator

integrator = SystemIntegrator(
    project_name="todo-evolution",
    phases=["console", "web", "ai"]
)

# Setup complete system
await integrator.setup_system(
    monorepo=True,
    schema_sync=True,
    phase_management=True
)
```

## Core Capabilities

### 1. Monorepo Setup and Management
```python
class MonorepoManager:
    """Manages monorepo structure and coordination."""

    def setup_monorepo(self, project_name: str):
        """Initialize monorepo structure."""
        structure = {
            "apps": {
                "console": {},      # Phase I
                "web": {},           # Phase II
                "chatbot": {}        # Phase III
            },
            "packages": {
                "shared": {
                    "types": {},       # Shared TypeScript types
                    "utils": {},       # Common utilities
                    "config": {}       # Configuration
                }
            },
            "tools": {
                "eslint-config": {},
                "prettier-config": {},
                "tsconfig": {}
            }
        }

        # Create directory structure
        self.create_directory_structure(structure)

        # Setup workspace configuration
        self.setup_workspace_config(project_name)

        # Initialize package.json files
        self.initialize_packages()

        return structure

    def setup_workspace_config(self, project_name: str):
        """Setup workspace configuration files."""
        # Root package.json
        root_config = {
            "name": project_name,
            "private": True,
            "workspaces": [
                "apps/*",
                "packages/*"
            ],
            "scripts": {
                "dev": "concurrently 'npm run dev:web' 'npm run dev:console'",
                "dev:web": "cd apps/web && npm run dev",
                "dev:console": "cd apps/console && npm run dev",
                "build": "npm run build --workspaces --if-present",
                "test": "npm run test --workspaces --if-present",
                "lint": "eslint . --ext .ts,.tsx",
                "format": "prettier --write .",
                "type-check": "npm run type-check --workspaces --if-present"
            }
        }

        self.write_json("package.json", root_config)

        # TypeScript project references
        self.setup_tsconfig()

    def setup_api_sync(self):
        """Setup API schema synchronization."""
        sync_config = {
            "frontend_backend": {
                "source": "apps/backend/models",
                "target": "packages/shared/types",
                "format": "typescript",
                "sync_on": ["build", "commit"]
            },
            "mcp_tools": {
                "source": "apps/chatbot/mcp-tools",
                "target": "packages/shared/types",
                "format": "typescript",
                "sync_on": ["build"]
            }
        }

        self.write_json(".api-sync.json", sync_config)
```

### 2. UV Package Management
```python
class UVPackageManager:
    """Manages Python packages with UV."""

    def setup_phase_1(self):
        """Setup packages for console app."""
        pyproject = {
            "project": {
                "name": "todo-console",
                "version": "0.1.0",
                "description": "Console todo application"
            },
            "dependencies": [
                "click>=8.0.0",
                "rich>=13.0.0"
            ],
            "dev-dependencies": [
                "pytest>=7.0.0",
                "ruff>=0.1.0",
                "mypy>=1.0.0"
            ]
        }

        self.write_pyproject("apps/console/pyproject.toml", pyproject)

    def setup_phase_2(self):
        """Setup packages for full-stack web."""
        # Backend dependencies
        backend_deps = {
            "project": {
                "name": "todo-backend",
                "version": "0.2.0"
            },
            "dependencies": [
                "fastapi>=0.104.0",
                "sqlmodel>=0.0.14",
                "uvicorn>=0.24.0",
                "psycopg2-binary>=2.9.0",
                "python-jose>=3.3.0",
                "python-multipart>=0.0.6"
            ]
        }

        self.write_pyproject("apps/backend/pyproject.toml", backend_deps)

        # Frontend dependencies
        frontend_deps = {
            "name": "todo-frontend",
            "version": "0.2.0",
            "dependencies": {
                "next": "^16.0.0",
                "react": "^18.0.0",
                "typescript": "^5.0.0",
                "tailwindcss": "^3.0.0",
                "better-auth": "latest"
            }
        }

        self.write_package_json("apps/web/package.json", frontend_deps)

    def create_dependency_graph(self):
        """Create dependency graph for the monorepo."""
        graph = {
            "console": [],
            "web": ["shared/types", "shared/utils"],
            "chatbot": ["web", "shared/types"],
            "shared/types": [],
            "shared/utils": ["shared/types"]
        }

        self.write_json("dependency-graph.json", graph)
```

### 3. API Schema Synchronization
```python
class APISchemaSync:
    """Synchronizes schemas between frontend and backend."""

    def sync_models(self):
        """Sync database models to TypeScript types."""
        # Read SQLModel definitions
        models = self.read_sqlmodels("apps/backend/app/models")

        # Generate TypeScript interfaces
        ts_types = self.generate_typescript_types(models)

        # Write to shared types package
        self.write_file(
            "packages/shared/types/src/models.ts",
            ts_types
        )

        # Generate API client types
        api_types = self.generate_api_types(models)

        self.write_file(
            "packages/shared/types/src/api.ts",
            api_types
        )

    def generate_typescript_types(self, models: dict) -> str:
        """Generate TypeScript types from SQLModel."""
        types = "// Generated types from SQLModel\n\n"

        for model_name, model_def in models.items():
            types += f"export interface {model_name} {{\n"

            for field, field_type in model_def["fields"].items():
                ts_type = self.convert_to_typescript(field_type)
                types += f"  {field}: {ts_type};\n"

            types += "}\n\n"

        return types

    def convert_to_typescript(self, field_type: dict) -> str:
        """Convert Python type to TypeScript."""
        if field_type["type"] == "str":
            return "string"
        elif field_type["type"] == "int":
            return "number"
        elif field_type["type"] == "bool":
            return "boolean"
        elif field_type["type"] == "datetime":
            return "string"  # ISO string
        elif field_type["type"] == "optional":
            inner_type = self.convert_to_typescript(field_type["inner"])
            return f"{inner_type} | null"
        else:
            return "any"

    def validate_schema_consistency(self):
        """Validate schema consistency across components."""
        backend_types = self.extract_backend_types()
        frontend_types = self.extract_frontend_types()

        inconsistencies = []

        for type_name in backend_types:
            if type_name not in frontend_types:
                inconsistencies.append(
                    f"Type {type_name} missing from frontend"
                )
            else:
                # Check field compatibility
                backend_fields = backend_types[type_name]
                frontend_fields = frontend_types[type_name]

                missing_fields = set(backend_fields) - set(frontend_fields)
                if missing_fields:
                    inconsistencies.append(
                        f"Type {type_name}: Missing fields {missing_fields} in frontend"
                    )

        return inconsistencies
```

### 4. Phase Management
```python
class PhaseManager:
    """Manages phase transitions and evolution."""

    def __init__(self):
        self.current_phase = 1
        self.phases = {
            1: {
                "name": "Console",
                "features": ["basic_crud", "cli_ui"],
                "tech_stack": ["python", "click", "rich"]
            },
            2: {
                "name": "Web",
                "features": ["web_ui", "auth", "database", "api"],
                "tech_stack": ["nextjs", "fastapi", "sqlmodel", "neon"]
            },
            3: {
                "name": "AI Chatbot",
                "features": ["ai_interface", "mcp_tools", "conversation", "stateless"],
                "tech_stack": ["chatkit", "openai-sdk", "mcp", "agents"]
            }
        }

    async def transition_to_phase(self, target_phase: int):
        """Transition to specified phase."""
        if target_phase <= self.current_phase:
            raise ValueError(f"Cannot transition backwards from phase {self.current_phase}")

        # Run migration
        migration_result = await self.migrate_to_phase(target_phase)

        if migration_result.success:
            self.current_phase = target_phase
            await self.update_phase_config(target_phase)
            return migration_result
        else:
            raise Exception(f"Migration to phase {target_phase} failed")

    async def migrate_to_phase(self, phase: int):
        """Perform phase migration."""
        if phase == 2:
            return await self.migrate_to_web()
        elif phase == 3:
            return await self.migrate_to_ai()
        else:
            raise ValueError(f"Unknown phase: {phase}")

    async def migrate_to_web(self):
        """Migrate from console to web."""
        # 1. Create web structure
        self.create_web_structure()

        # 2. Migrate data models
        await self.migrate_models_to_sqlmodel()

        # 3. Create API endpoints
        await self.create_api_from_cli()

        # 4. Setup authentication
        await self.setup_authentication()

        return MigrationResult(
            success=True,
            message="Successfully migrated to Phase II"
        )

    async def migrate_to_ai(self):
        """Migrate from web to AI chatbot."""
        # 1. Add AI components
        await self.add_ai_components()

        # 2. Create MCP server
        await self.create_mcp_server()

        # 3. Setup conversation management
        await self.setup_conversation_db()

        # 4. Integrate ChatKit
        await self.integrate_chatkit()

        return MigrationResult(
            success=True,
            message="Successfully migrated to Phase III"
        )
```

### 5. Development Environment Coordination
```python
class DevCoordinator:
    """Coordinates development environments."""

    def setup_development_docker(self):
        """Setup Docker Compose for development."""
        docker_compose = {
            "version": "3.8",
            "services": {
                "postgres": {
                    "image": "postgres:15",
                    "environment": {
                        "POSTGRES_USER": "todo",
                        "POSTGRES_PASSWORD": "password",
                        "POSTGRES_DB": "todo"
                    },
                    "ports": ["5432:5432"],
                    "volumes": ["postgres_data:/var/lib/postgresql/data"]
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": ["6379:6379"]
                },
                "backend": {
                    "build": "./apps/backend",
                    "ports": ["8000:8000"],
                    "environment": {
                        "DATABASE_URL": "postgresql://todo:password@postgres:5432/todo"
                    },
                    "depends_on": ["postgres", "redis"],
                    "volumes": ["./apps/backend:/app"]
                },
                "frontend": {
                    "build": "./apps/web",
                    "ports": ["3000:3000"],
                    "environment": {
                        "NEXT_PUBLIC_API_URL": "http://localhost:8000"
                    },
                    "depends_on": ["backend"],
                    "volumes": ["./apps/web:/app"]
                }
            },
            "volumes": {
                "postgres_data": None
            }
        }

        self.write_yaml("docker-compose.dev.yml", docker_compose)

    def create_launch_scripts(self):
        """Create launch scripts for each phase."""
        # Phase I script
        self.create_script(
            "run-phase1.sh",
            """#!/bin/bash
cd apps/console
uv run python main.py "$@"
"""
        )

        # Phase II script
        self.create_script(
            "run-phase2.sh",
            """#!/bin/bash
# Start backend
cd apps/backend && uv run uvicorn main:app --reload &
BACKEND_PID=$!

# Start frontend
cd apps/web && npm run dev &
FRONTEND_PID=$!

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
"""
        )

        # Phase III script
        self.create_script(
            "run-phase3.sh",
            """#!/bin/bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Wait for services
sleep 10

# Start MCP server
cd apps/chatbot && uv run python mcp_server.py &
MCP_PID=$!

# Start backend with AI
cd apps/backend && uv run uvicorn main:app --reload &
BACKEND_PID=$!

# Start frontend with chat
cd apps/web && npm run dev &
FRONTEND_PID=$!

wait $MCP_PID $BACKEND_PID $FRONTEND_PID
"""
        )
```

### 6. Integration Testing
```python
class IntegrationTestSuite:
    """Tests system integration between components."""

    async def test_frontend_backend_integration(self):
        """Test frontend-backend communication."""
        # Start backend
        backend = await self.start_backend()

        # Start frontend
        frontend = await self.start_frontend()

        # Test API calls
        test_results = await self.run_integration_tests()

        # Shutdown services
        await self.shutdown_backend(backend)
        await self.shutdown_frontend(frontend)

        return test_results

    async def test_mcp_integration(self):
        """Test MCP server integration."""
        # Start MCP server
        mcp_server = await self.start_mcp_server()

        # Test tool calls
        results = []
        for tool in ["add_task", "list_tasks", "complete_task"]:
            result = await self.test_mcp_tool(tool)
            results.append(result)

        # Shutdown server
        await self.shutdown_mcp_server(mcp_server)

        return results

    async def test_database_consistency(self):
        """Test data consistency across components."""
        # Create test data
        test_data = await self.create_test_data()

        # Verify in all components
        checks = []
        checks.append(await self.verify_in_database(test_data))
        checks.append(await self.verify_in_api(test_data))
        checks.append(await self.verify_in_frontend(test_data))

        return all(checks)
```

## Configuration Management

### Shared Configuration
```typescript
// packages/shared/config/index.ts
export const config = {
  development: {
    apiUrl: "http://localhost:8000",
    mcpUrl: "http://localhost:8001",
    databaseUrl: "postgresql://localhost:5432/todo"
  },
  production: {
    apiUrl: "https://api.todoapp.com",
    mcpUrl: "https://mcp.todoapp.com",
    databaseUrl: process.env.DATABASE_URL
  }
};

export const phaseConfig = {
  1: {
    name: "Console",
    features: ["cli", "in-memory"]
  },
  2: {
    name: "Web",
    features: ["api", "database", "auth"]
  },
  3: {
    name: "AI Chatbot",
    features: ["chat", "mcp", "ai"]
  }
};
```

### Environment Variables
```python
# apps/backend/.env.example
DATABASE_URL=postgresql://todo:password@localhost:5432/todo
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key

# apps/web/.env.example
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000

# apps/chatbot/.env.example
MCP_PORT=8001
AGENT_MODEL=gpt-4
MAX_CONVERSATION_LENGTH=50
```

## Migration Scripts

### Automated Migration
```python
# scripts/migrate_phase.py
import asyncio
import sys
from pathlib import Path

async def main():
    phase = int(sys.argv[1]) if len(sys.argv) > 1 else None

    if not phase:
        print("Usage: python migrate_phase.py <phase_number>")
        sys.exit(1)

    integrator = SystemIntegrator("todo-evolution")

    try:
        result = await integrator.transition_to_phase(phase)
        print(f"✅ Migration to Phase {phase} successful")
        print(f"📝 {result.message}")

        # Post-migration validation
        await validate_migration(phase)

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

async def validate_migration(phase):
    """Validate migration was successful."""
    print("\n🔍 Validating migration...")

    if phase >= 2:
        # Test web features
        await test_web_features()

    if phase >= 3:
        # Test AI features
        await test_ai_features()

    print("✅ Validation complete")

if __name__ == "__main__":
    asyncio.run(main())
```

## Integration with Other Agents

### With Spec-Architect
- Updates configuration for new phases
- Manages architecture evolution
- Tracks system changes

### With Backend-Engineer
- Coordinates API endpoints
- Manages database schemas
- Ensures model consistency

### With Frontend-UX-Designer
- Syncs type definitions
- Manages component sharing
- Coordinates UI evolution

### With AI-Systems-Specialist
- Sets up MCP server integration
- Manages tool registration
- Coordinates AI features

## Best Practices

### System Architecture
1. **Loose coupling** - Components communicate via APIs
2. **Strong contracts** - Clear type definitions
3. **Version management** - Semantic versioning
4. **Backward compatibility** - Support older clients
5. **Migration paths** - Clear upgrade paths

### Development Workflow
1. **Feature flags** - Toggle features between phases
2. **Gradual rollout** - Phase-based deployment
3. **Consistent naming** - Standardize conventions
4. **Documentation** - Keep configs documented
5. **Testing** - Integration tests at boundaries

### Configuration Management
1. **Environment separation** - Dev/staging/prod configs
2. **Secrets management** - Secure credential storage
3. **Type safety** - Validate configurations
4. **Default values** - Reasonable defaults
5. **Validation** - Validate on startup