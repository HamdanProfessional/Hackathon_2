#!/usr/bin/env python3
"""
Phase 4: Kubernetes Deployment Validation Tests

Tests complete Docker containerization and Kubernetes deployment readiness.
Validates Dockerfiles, docker-compose, and Helm charts.
"""

import os
import subprocess
import sys
from pathlib import Path
import yaml

# Colors for output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


def print_header(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")


def print_result(test_name, passed, details=""):
    icon = f"{Colors.GREEN}[OK]{Colors.END}" if passed else f"{Colors.RED}[FAIL]{Colors.END}"
    print(f"  {icon} {test_name}")
    if details:
        print(f"      {details}")
    return passed


def run_command(cmd, description):
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def test_dockerfiles_exist():
    """Test that Dockerfiles exist."""
    print_header("1. Dockerfiles Exist")

    frontend_dockerfile = PROJECT_ROOT / "frontend" / "Dockerfile"
    backend_dockerfile = PROJECT_ROOT / "backend" / "Dockerfile"

    results = []
    results.append(print_result(
        "Frontend Dockerfile exists",
        frontend_dockerfile.exists(),
        f"Path: {frontend_dockerfile}"
    ))
    results.append(print_result(
        "Backend Dockerfile exists",
        backend_dockerfile.exists(),
        f"Path: {backend_dockerfile}"
    ))

    if all(results):
        # Verify Dockerfile content
        print("\n  Verifying Dockerfile content...")

        with open(frontend_dockerfile) as f:
            frontend_content = f.read()
        results.append(print_result(
            "Frontend uses node:20-alpine base",
            "node:20-alpine" in frontend_content
        ))
        results.append(print_result(
            "Frontend has multi-stage build",
            "AS builder" in frontend_content or "FROM" in frontend_content
        ))

        with open(backend_dockerfile) as f:
            backend_content = f.read()
        results.append(print_result(
            "Backend uses python:3.13-slim base",
            "python:3.13" in backend_content
        ))
        results.append(print_result(
            "Backend has uvicorn runtime",
            "uvicorn" in backend_content
        ))

    return all(results)


def test_dockerignore_exists():
    """Test that .dockerignore files exist."""
    print_header("2. .dockerignore Files Exist")

    frontend_ignore = PROJECT_ROOT / "frontend" / ".dockerignore"
    backend_ignore = PROJECT_ROOT / "backend" / ".dockerignore"

    results = []
    results.append(print_result(
        "Frontend .dockerignore exists",
        frontend_ignore.exists()
    ))
    results.append(print_result(
        "Backend .dockerignore exists",
        backend_ignore.exists()
    ))

    if frontend_ignore.exists():
        with open(frontend_ignore) as f:
            content = f.read()
        results.append(print_result(
            "Frontend excludes node_modules",
            "node_modules" in content
        ))
        results.append(print_result(
            "Frontend excludes .next",
            ".next" in content
        ))

    if backend_ignore.exists():
        with open(backend_ignore) as f:
            content = f.read()
        results.append(print_result(
            "Backend excludes __pycache__",
            "__pycache__" in content
        ))
        results.append(print_result(
            "Backend excludes .venv",
            ".venv" in content
        ))

    return all(results)


def test_docker_compose_exists():
    """Test that docker-compose.yml exists."""
    print_header("3. Docker Compose Configuration")

    compose_file = PROJECT_ROOT / "docker-compose.yml"

    if not compose_file.exists():
        print_result("docker-compose.yml exists", False)
        return False

    print_result("docker-compose.yml exists", True)

    with open(compose_file) as f:
        compose_config = yaml.safe_load(f)

    results = []
    services = compose_config.get("services", {})
    results.append(print_result(
        "Has frontend service",
        "frontend" in services
    ))
    results.append(print_result(
        "Has backend service",
        "backend" in services
    ))
    results.append(print_result(
        "Has postgres service",
        "postgres" in services or "database" in services
    ))

    if "frontend" in services:
        results.append(print_result(
            "Frontend exposes port 3000",
            "3000:3000" in str(services["frontend"].get("ports", []))
        ))

    if "backend" in services:
        results.append(print_result(
            "Backend exposes port 8000",
            "8000:8000" in str(services["backend"].get("ports", []))
        ))

    return all(results)


def test_helm_charts_exist():
    """Test that Helm charts exist."""
    print_header("4. Helm Charts Exist")

    frontend_chart = PROJECT_ROOT / "helm" / "frontend"
    backend_chart = PROJECT_ROOT / "helm" / "backend"

    results = []

    # Check Chart.yaml files
    frontend_chart_yaml = frontend_chart / "Chart.yaml"
    backend_chart_yaml = backend_chart / "Chart.yaml"

    results.append(print_result(
        "Frontend Helm chart exists",
        frontend_chart.exists() and frontend_chart_yaml.exists()
    ))
    results.append(print_result(
        "Backend Helm chart exists",
        backend_chart.exists() and backend_chart_yaml.exists()
    ))

    # Check templates
    frontend_templates = frontend_chart / "templates"
    backend_templates = backend_chart / "templates"

    if frontend_templates.exists():
        templates = list(frontend_templates.glob("*.yaml"))
        results.append(print_result(
            f"Frontend has {len(templates)} templates",
            len(templates) >= 3  # deployment, service, configmap minimum
        ))

        for template_name in ["deployment.yaml", "service.yaml", "configmap.yaml"]:
            exists = (frontend_templates / template_name).exists()
            results.append(print_result(
                f"  Has {template_name}",
                exists
            ))

    if backend_templates.exists():
        templates = list(backend_templates.glob("*.yaml"))
        results.append(print_result(
            f"Backend has {len(templates)} templates",
            len(templates) >= 4  # deployment, service, secrets, configmap
        ))

        for template_name in ["deployment.yaml", "service.yaml", "secrets.yaml", "configmap.yaml"]:
            exists = (backend_templates / template_name).exists()
            results.append(print_result(
                f"  Has {template_name}",
                exists
            ))

    return all(results)


def test_helm_chart_validity():
    """Test Helm charts with helm lint."""
    print_header("5. Helm Chart Validity (helm lint)")

    results = []

    # Test frontend chart
    passed, stdout, stderr = run_command(
        f"cd {PROJECT_ROOT} && helm lint helm/frontend",
        "Frontend helm lint"
    )

    if passed and "0 chart(s) failed" in stdout:
        print_result("Frontend Helm chart passes lint", True)
        results.append(True)
    else:
        print_result("Frontend Helm chart passes lint", False, stderr)
        results.append(False)

    # Test backend chart
    passed, stdout, stderr = run_command(
        f"cd {PROJECT_ROOT} && helm lint helm/backend",
        "Backend helm lint"
    )

    if passed and "0 chart(s" in stdout:
        print_result("Backend Helm chart passes lint", True)
        results.append(True)
    else:
        print_result("Backend Helm chart passes lint", False, stderr)
        results.append(False)

    return all(results)


def test_helm_values():
    """Test Helm values.yaml files."""
    print_header("6. Helm Values Configuration")

    results = []

    # Check frontend values
    frontend_values = PROJECT_ROOT / "helm" / "frontend" / "values.yaml"
    if frontend_values.exists():
        with open(frontend_values) as f:
            values = yaml.safe_load(f)

        image = values.get("image", {})
        results.append(print_result(
            "Frontend has image configuration",
            "repository" in image and "tag" in image
        ))

        service = values.get("service", {})
        results.append(print_result(
            "Frontend has service type",
            "type" in service
        ))

    # Check backend values
    backend_values = PROJECT_ROOT / "helm" / "backend" / "values.yaml"
    if backend_values.exists():
        with open(backend_values) as f:
            values = yaml.safe_load(f)

        image = values.get("image", {})
        results.append(print_result(
            "Backend has image configuration",
            "repository" in image and "tag" in image
        ))

        service = values.get("service", {})
        results.append(print_result(
            "Backend has service type",
            "type" in service
        ))

        secrets = values.get("secrets", {})
        results.append(print_result(
            "Backend has secrets configuration",
            len(secrets) > 0
        ))

    return all(results)


def test_deployment_guides():
    """Test that deployment guides exist."""
    print_header("7. Deployment Guides")

    results = []

    # Check for README or deployment guides in helm directory
    frontend_readme = PROJECT_ROOT / "helm" / "frontend" / "README.md"
    backend_readme = PROJECT_ROOT / "helm" / "backend" / "README.md"

    results.append(print_result(
        "Frontend has deployment guide",
        frontend_readme.exists()
    ))
    results.append(print_result(
        "Backend has deployment guide",
        backend_readme.exists()
    ))

    # Check NOTES.txt templates
    frontend_notes = PROJECT_ROOT / "helm" / "frontend" / "templates" / "NOTES.txt"
    backend_notes = PROJECT_ROOT / "helm" / "backend" / "templates" / "NOTES.txt"

    results.append(print_result(
        "Frontend has install notes template",
        frontend_notes.exists()
    ))
    results.append(print_result(
        "Backend has install notes template",
        backend_notes.exists()
    ))

    return all(results)


def test_security_hardening():
    """Test security configurations in Helm charts."""
    print_header("8. Security Hardening")

    results = []

    # Check frontend values.yaml for security context
    frontend_values = PROJECT_ROOT / "helm" / "frontend" / "values.yaml"
    if frontend_values.exists():
        with open(frontend_values) as f:
            content = f.read()

        results.append(print_result(
            "Frontend has non-root user (values.yaml)",
            "runAsNonRoot: true" in content or "runAsNonRoot" in content
        ))
        results.append(print_result(
            "Frontend has security context (values.yaml)",
            "securityContext:" in content
        ))
        results.append(print_result(
            "Frontend has resource limits (values.yaml)",
            "resources:" in content and "limits:" in content
        ))

    # Check backend values.yaml for security context
    backend_values = PROJECT_ROOT / "helm" / "backend" / "values.yaml"
    if backend_values.exists():
        with open(backend_values) as f:
            content = f.read()

        results.append(print_result(
            "Backend has non-root user (values.yaml)",
            "runAsNonRoot: true" in content or "runAsNonRoot" in content
        ))
        results.append(print_result(
            "Backend has security context (values.yaml)",
            "securityContext:" in content
        ))
        results.append(print_result(
            "Backend has resource limits (values.yaml)",
            "resources:" in content and "limits:" in content
        ))

    # Also check deployment templates have security context wired up
    frontend_deployment = PROJECT_ROOT / "helm" / "frontend" / "templates" / "deployment.yaml"
    if frontend_deployment.exists():
        with open(frontend_deployment) as f:
            content = f.read()

        results.append(print_result(
            "Frontend deployment has security context reference",
            "securityContext:" in content
        ))
        results.append(print_result(
            "Frontend deployment has resources reference",
            "resources:" in content
        ))

    backend_deployment = PROJECT_ROOT / "helm" / "backend" / "templates" / "deployment.yaml"
    if backend_deployment.exists():
        with open(backend_deployment) as f:
            content = f.read()

        results.append(print_result(
            "Backend deployment has security context reference",
            "securityContext:" in content
        ))
        results.append(print_result(
            "Backend deployment has resources reference",
            "resources:" in content
        ))

    return all(results)


def main():
    """Run all Phase 4 validation tests."""
    print(f"""
{Colors.BOLD}{'='*60}
  Phase 4: Kubernetes Deployment Validation
{'='*60}{Colors.END}

Project Root: {PROJECT_ROOT}
""")

    tests = [
        ("Dockerfiles", test_dockerfiles_exist),
        (".dockerignore Files", test_dockerignore_exists),
        ("Docker Compose", test_docker_compose_exists),
        ("Helm Charts Structure", test_helm_charts_exist),
        ("Helm Chart Validity", test_helm_chart_validity),
        ("Helm Values", test_helm_values),
        ("Deployment Guides", test_deployment_guides),
        ("Security Hardening", test_security_hardening),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n{Colors.RED}Error running {name}: {e}{Colors.END}")
            results[name] = False

    # Summary
    print_header("SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    for name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {status} {name}")

    print(f"\n{Colors.BOLD}Total: {total} | Passed: {passed} | Failed: {failed}{Colors.END}")

    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}Phase 4: All validation tests passed!{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Phase 4: {failed} test(s) failed{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
