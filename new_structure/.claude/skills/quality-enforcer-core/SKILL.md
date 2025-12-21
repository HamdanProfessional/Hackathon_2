---
name: quality-enforcer-core
description: Comprehensive quality assurance and testing framework for all development phases. Handles code review standards, test generation, performance analysis, integration testing, and deployment validation. Ensures all code adheres to the constitution and specifications. Manages quality gates and compliance across console, web, and AI phases.
---

# Quality Enforcer Core

## Quick Start

```python
# Initialize quality enforcement
from quality_enforcer_core import QualityEnforcer

enforcer = QualityEnforcer(
    project_path=".",
    constitution_path="speckit.constitution",
    quality_standards="production"
)

# Run full quality check
results = await enforcer.run_quality_gates([
    "code_review",
    "unit_tests",
    "integration_tests",
    "performance_analysis",
    "security_scan"
])
```

## Core Capabilities

### 1. Automated Code Review
```python
class CodeReviewEngine:
    """Reviews code against project standards."""

    def review_file(self, file_path: str) -> ReviewResult:
        issues = []

        # Check adherence to constitution
        if not self.follows_architecture(file_path):
            issues.append(ReviewIssue(
                type="architecture",
                message="Violates architecture principles",
                severity="high"
            ))

        # Check code quality metrics
        metrics = self.analyze_code_quality(file_path)
        if metrics.complexity > 10:
            issues.append(ReviewIssue(
                type="complexity",
                message=f"High complexity ({metrics.complexity})",
                severity="medium"
            ))

        return ReviewResult(
            file=file_path,
            score=self.calculate_score(issues),
            issues=issues
        )
```

### 2. Test Generation
```python
class TestGenerator:
    """Generates comprehensive test suites."""

    def generate_unit_tests(self, code: str, language: str) -> List[TestSuite]:
        """Generate unit tests from code."""
        if language == "python":
            return self.generate_python_tests(code)
        elif language == "typescript":
            return self.generate_javascript_tests(code)

        # Parse code to identify functions and classes
        ast = self.parse_code(code)
        tests = []

        for node in ast.functions:
            tests.append(self.create_test_for_function(node))

        for node in ast.classes:
            tests.append(self.create_test_for_class(node))

        return tests

    def generate_integration_tests(self, api_spec: dict) -> List[TestSuite]:
        """Generate API integration tests."""
        tests = []

        for endpoint in api_spec["endpoints"]:
            test = self.create_endpoint_test(endpoint)
            tests.append(test)

        return tests
```

### 3. Performance Analysis
```python
class PerformanceAnalyzer:
    """Analyzes application performance."""

    async def analyze_api_performance(self, endpoint: str, method: str):
        """Test API endpoint performance."""
        # Test with various loads
        loads = [1, 10, 50, 100]
        results = []

        for load in loads:
            times = []
            for _ in range(load):
                start = time.time()
                response = await self.make_request(endpoint, method)
                end = time.time()
                times.append(end - start)

            results.append({
                "load": load,
                "avg_time": sum(times) / len(times),
                "p95_time": sorted(times)[int(len(times) * 0.95)],
                "max_time": max(times)
            })

        return PerformanceReport(
            endpoint=endpoint,
            method=method,
            results=results,
            passes=self.check_performance_thresholds(results)
        )

    def analyze_database_queries(self, session):
        """Analyze database query performance."""
        slow_queries = []

        for query in session.query_log:
            if query.duration > 100:  # 100ms threshold
                slow_queries.append({
                    "query": query.sql,
                    "duration": query.duration,
                    "recommendation": self.optimize_query(query.sql)
                })

        return slow_queries
```

## Quality Gates

### Pre-Commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: code-review
        name: Code Review
        entry: quality-enforcer review
        language: system
        pass_filenames: false

      - id: unit-tests
        name: Unit Tests
        entry: pytest
        language: system
        args: [--cov, --cov-report=html]

      - id: type-check
        name: Type Check
        entry: mypy
        language: system
        files: \.py$
```

### CI/CD Quality Gates
```yaml
# .github/workflows/quality.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Quality Enforcer
        run: |
          quality-enforcer check-all
          quality-enforcer generate-coverage
          quality-enforcer performance-test

      - name: Upload Coverage
        uses: codecov/codecov-action@v1
```

## Test Framework Setup

### Phase I (Console) Testing
```python
# tests/test_console_app.py
import pytest
from io import StringIO
import sys

def test_task_cli_add():
    """Test CLI add task functionality."""
    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    # Run CLI command
    from main import main
    main(["add", "Test task"])

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Assert output
    output = captured_output.getvalue()
    assert "Task created" in output
    assert "ID: 1" in output

def test_task_crud_operations():
    """Test complete CRUD flow."""
    tm = TaskManager()

    # Create
    task = tm.create_task("Test task")
    assert task.id is not None
    assert task.title == "Test task"

    # Read
    retrieved = tm.get_task(task.id)
    assert retrieved.id == task.id

    # Update
    tm.update_task(task.id, title="Updated task")
    assert tm.get_task(task.id).title == "Updated task"

    # Delete
    tm.delete_task(task.id)
    with pytest.raises(KeyError):
        tm.get_task(task.id)
```

### Phase II (Web) Testing
```python
# tests/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    # Create test user and get token
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_task_endpoint(auth_headers):
    """Test POST /api/tasks endpoint."""
    response = client.post(
        "/api/tasks",
        json={"title": "Test task", "description": "Test description"},
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "Test description"

def test_list_tasks_endpoint(auth_headers):
    """Test GET /api/tasks endpoint."""
    # Create a task first
    client.post(
        "/api/tasks",
        json={"title": "Test task"},
        headers=auth_headers
    )

    # List tasks
    response = client.get("/api/tasks", headers=auth_headers)

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) > 0
    assert tasks[0]["title"] == "Test task"
```

### Phase III (AI Chatbot) Testing
```python
# tests/test_ai_integration.py
import pytest
from app.ai.chat_handler import ChatHandler

async def test_conversation_flow():
    """Test complete conversation flow."""
    handler = ChatHandler()

    # First message
    response1 = await handler.handle_message(
        user_id="test_user",
        message="Add a task to buy groceries",
        conversation_id=None
    )

    assert response1["response"] is not None
    assert "task" in response1["response"].lower()
    assert len(response1["tool_calls"]) > 0

    # Second message in same conversation
    response2 = await handler.handle_message(
        user_id="test_user",
        message="What tasks do I have?",
        conversation_id=response1["conversation_id"]
    )

    assert response2["response"] is not None
    assert "buy groceries" in response2["response"].lower()

async def test_mcp_tool_execution():
    """Test MCP tool execution."""
    from app.ai.mcp_server import handle_tool_call

    # Test add_task tool
    result = await handle_tool_call("add_task", {
        "user_id": "test_user",
        "title": "Test task via MCP",
        "description": "Created by test"
    })

    assert result["success"] is True
    assert result["title"] == "Test task via MCP"
```

## Code Quality Metrics

### Complexity Analysis
```python
class ComplexityAnalyzer:
    """Analyzes code complexity."""

    def calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity

        # Count decision points
        decision_keywords = [
            "if", "elif", "else",
            "for", "while",
            "except", "finally",
            "and", "or"
        ]

        lines = code.split('\n')
        for line in lines:
            for keyword in decision_keywords:
                if keyword in line:
                    complexity += 1

        return complexity

    def analyze_maintainability_index(self, file_path: str) -> float:
        """Calculate maintainability index (0-100)."""
        with open(file_path, 'r') as f:
            code = f.read()

        # Factors affecting maintainability
        complexity = self.calculate_cyclomatic_complexity(code)
        lines_of_code = len(code.split('\n'))
        comment_ratio = self.calculate_comment_ratio(code)

        # Simple MI calculation
        mi = 171 - 5.2 * math.log(complexity) - 0.23 * complexity - 16.2 * math.log(lines_of_code)
        mi += 50 * math.sin(math.sqrt(2.4 * comment_ratio))

        return max(0, min(100, mi))
```

### Coverage Requirements
```python
class CoverageChecker:
    """Enforces test coverage requirements."""

    COVERAGE_REQUIREMENTS = {
        "production": 90,  # 90% for production
        "staging": 80,      # 80% for staging
        "development": 70   # 70% for development
    }

    def check_coverage(self, report_path: str, environment: str) -> bool:
        """Check if coverage meets requirements."""
        with open(report_path, 'r') as f:
            coverage = json.load(f)

        required = self.COVERAGE_REQUIREMENTS[environment]
        actual = coverage["totals"]["percent_covered"]

        if actual < required:
            print(f"Coverage {actual}% is below requirement {required}%")
            return False

        return True

    def generate_coverage_badge(self, coverage: float) -> str:
        """Generate coverage badge for README."""
        if coverage >= 90:
            color = "brightgreen"
        elif coverage >= 80:
            color = "yellow"
        elif coverage >= 70:
            color = "orange"
        else:
            color = "red"

        return f"![coverage](https://img.shields.io/badge/coverage-{coverage:.0f}%25-{color})"
```

## Performance Benchmarks

### API Performance
```python
API_PERFORMANCE_THRESHOLDS = {
    "avg_response_time": 200,  # ms
    "p95_response_time": 500,  # ms
    "max_response_time": 1000,  # ms
    "requests_per_second": 1000,
    "error_rate": 0.01  # 1%
}

def benchmark_api_endpoint(endpoint: str, method: str = "GET"):
    """Benchmark API endpoint performance."""
    import asyncio
    import aiohttp

    async def make_request(session, url):
        start = time.time()
        async with session.request(method, url) as response:
            await response.text()
            end = time.time()
            return end - start

    async def run_benchmark():
        times = []
        async with aiohttp.ClientSession() as session:
            # Warm up
            for _ in range(10):
                await make_request(session, endpoint)

            # Benchmark
            for _ in range(1000):
                time_taken = await make_request(session, endpoint)
                times.append(time_taken)

        stats = {
            "avg": sum(times) / len(times),
            "p95": sorted(times)[950],
            "max": max(times)
        }

        # Check against thresholds
        passed = all([
            stats["avg"] < API_PERFORMANCE_THRESHOLDS["avg_response_time"],
            stats["p95"] < API_PERFORMANCE_THRESHOLDS["p95_response_time"],
            stats["max"] < API_PERFORMANCE_THRESHOLDS["max_response_time"]
        ])

        return stats, passed
```

### Frontend Performance
```javascript
// tests/frontend/performance.test.js
import { test, expect } from '@playwright/test';

test('page load performance', async ({ page }) => {
  const startTime = Date.now();

  // Navigate to page
  await page.goto('/tasks');

  // Wait for page to be fully loaded
  await page.waitForLoadState('networkidle');

  const loadTime = Date.now() - startTime;

  // Check performance thresholds
  expect(loadTime).toBeLessThan(3000); // 3 seconds

  // Check Core Web Vitals
  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        resolve({
          lcp: entries.find(e => e.name === 'largest-contentful-paint')?.startTime || 0,
          fid: entries.find(e => e.name === 'first-input-delay')?.processingStart || 0,
          cls: entries.find(e => e.name === 'cumulative-layout-shift')?.value || 0
        });
      }).observe({ entryTypes: ['largest-contentful-paint', 'first-input-delay', 'cumulative-layout-shift'] });
    });
  });

  expect(metrics.lcp).toBeLessThan(2500); // LCP < 2.5s
  expect(metrics.fid).toBeLessThan(100);   // FID < 100ms
  expect(metrics.cls).toBeLessThan(0.1);   // CLS < 0.1
});
```

## Security Testing

### Vulnerability Scanning
```python
class SecurityScanner:
    """Scans code for security vulnerabilities."""

    async def scan_dependencies(self):
        """Scan dependencies for known vulnerabilities."""
        import subprocess

        # Run safety check
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )

        vulnerabilities = json.loads(result.stdout)

        return {
            "vulnerabilities": vulnerabilities,
            "passed": len(vulnerabilities) == 0
        }

    def check_auth_flaws(self, code: str) -> List[SecurityIssue]:
        """Check for authentication flaws."""
        issues = []

        # Check for hardcoded secrets
        if re.search(r'(password|secret|key)\s*=\s*[\'"].*[\'"]', code):
            issues.append(SecurityIssue(
                type="hardcoded_secret",
                message="Hardcoded secret detected",
                severity="high"
            ))

        # Check for SQL injection vulnerabilities
        if re.search(r'f".*{.*}.*"', code) and "SELECT" in code:
            issues.append(SecurityIssue(
                type="sql_injection",
                message="Potential SQL injection with f-string",
                severity="critical"
            ))

        return issues
```

## Quality Reporting

### Dashboard Metrics
```python
class QualityDashboard:
    """Generates quality metrics dashboard."""

    def generate_report(self) -> QualityReport:
        """Generate comprehensive quality report."""
        return QualityReport(
            code_quality=self.analyze_code_quality(),
            test_coverage=self.get_coverage_metrics(),
            performance=self.get_performance_metrics(),
            security=self.get_security_metrics(),
            compliance=self.check_compliance()
        )

    def export_to_html(self, report: QualityReport) -> str:
        """Export report as HTML dashboard."""
        template = """
        <html>
            <head><title>Quality Dashboard</title></head>
            <body>
                <h1>Quality Dashboard</h1>

                <h2>Code Quality</h2>
                <div class="metric">
                    <span>Average Score:</span>
                    <span class="value">{code_quality.avg_score:.1f}</span>
                </div>

                <h2>Test Coverage</h2>
                <div class="metric">
                    <span>Line Coverage:</span>
                    <span class="value">{test_coverage.line}%</span>
                </div>

                <h2>Performance</h2>
                <div class="metric">
                    <span>API Response Time:</span>
                    <span class="value">{performance.avg_response_time}ms</span>
                </div>
            </body>
        </html>
        """

        return template.format(**report.to_dict())
```

## Integration with CI/CD

### GitHub Actions Workflow
```yaml
# .github/workflows/quality.yml
name: Quality Assurance

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        phase: [console, web, ai]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          pip install quality-enforcer

      - name: Run Quality Checks
        run: |
          quality-enforcer check --phase=${{ matrix.phase }}
          quality-enforcer test --phase=${{ matrix.phase }}
          quality-enforcer performance --phase=${{ matrix.phase }}

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          flags: ${{ matrix.phase }}

      - name: Security Scan
        run: |
          safety check
          bandit -r app/
```

## Best Practices

### Code Review Standards
1. **Review all code** - No PR without review
2. **Check compliance** - Verify against constitution
3. **Test coverage** - Minimum 80% coverage
4. **Documentation** - Code must be documented
5. **Performance** - No performance regressions

### Testing Strategy
1. **Unit tests** - Test individual components
2. **Integration tests** - Test component interactions
3. **End-to-end tests** - Test user workflows
4. **Performance tests** - Verify performance thresholds
5. **Security tests** - Check for vulnerabilities

### Quality Gates
1. **Fail fast** - Block problematic commits
2. **Automated checks** - Run automatically on PRs
3. **Metrics tracking** - Track quality over time
4. **Continuous improvement** - Address recurring issues
5. **Documentation** - Maintain quality standards