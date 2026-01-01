#!/usr/bin/env python3
"""Validate stateless agent architecture compliance."""
import ast
import sys
from pathlib import Path
from typing import List, Dict, Any, Set


class StatelessComplianceValidator(ast.NodeVisitor):
    """Validate stateless architecture compliance."""

    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.classes: Dict[str, List[str]] = {}

    def visit_ClassDef(self, node: ast.ClassDef):
        """Check for stateful patterns in classes."""
        class_name = node.name
        self.classes[class_name] = []

        # Check for instance variables
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        self.classes[class_name].append(target.id)

                        # Check for stateful patterns
                        state_keywords = [
                            'conversation', 'message', 'chat', 'context',
                            'cache', 'state', 'history', 'session', 'memory'
                        ]
                        if any(keyword in var_name for keyword in state_keywords):
                            self.violations.append({
                                'type': 'stateful_instance_var',
                                'severity': 'critical',
                                'class': class_name,
                                'line': node.lineno,
                                'var_name': target.id,
                                'message': f'Class {class_name} has stateful instance variable: {target.id}'
                            })

        # Check methods for database parameters
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                params = [arg.arg for arg in item.args.args]
                if 'db' not in params and 'session' not in params:
                    # Methods that likely need DB but don't have it
                    if any(item.name.lower().startswith(prefix) for prefix in
                           ['get_', 'fetch_', 'load_', 'create_', 'update_', 'delete_', 'process_']):
                        self.warnings.append({
                            'type': 'missing_db_param',
                            'severity': 'warning',
                            'class': class_name,
                            'line': item.lineno,
                            'func_name': item.name,
                            'message': f'Method {class_name}.{item.name}() may need database session parameter'
                        })

        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        """Check for global state variables."""
        for name in node.names:
            if any(keyword in name.lower() for keyword in
                   ['conversation', 'message', 'cache', 'state', 'history']):
                self.violations.append({
                    'type': 'global_state',
                    'severity': 'critical',
                    'line': node.lineno,
                    'var_name': name,
                    'message': f'Global state variable detected: {name}'
                })

    def visit_Import(self, node: ast.Import):
        """Check for suspicious imports."""
        for alias in node.names:
            if alias.name == 'functools' and 'lru_cache' in str(alias):
                self.warnings.append({
                    'type': 'lru_cache_import',
                    'severity': 'warning',
                    'line': node.lineno,
                    'message': 'lru_cache imported - ensure no unbounded caching of user data'
                })

    def visit_Call(self, node: ast.Call):
        """Check for dangerous patterns."""
        # Check for unbounded lru_cache
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'lru_cache':
                # Check if maxsize is specified
                if not node.keywords or not any(k.arg == 'maxsize' for k in node.keywords):
                    self.violations.append({
                        'type': 'unbounded_cache',
                        'severity': 'critical',
                        'line': node.lineno,
                        'message': '@lru_cache without maxsize parameter creates unbounded cache'
                    })

        self.generic_visit(node)


def validate_file(file_path: Path) -> Dict[str, Any]:
    """Validate a single Python file for stateless compliance."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code, filename=str(file_path))
    except SyntaxError as e:
        return {'error': f'Syntax error: {e}'}
    except Exception as e:
        return {'error': str(e)}

    validator = StatelessComplianceValidator()
    validator.visit(tree)

    return {
        'file': str(file_path),
        'violations': validator.violations,
        'warnings': validator.warnings,
        'classes': validator.classes
    }


def validate_directory(directory: Path) -> List[Dict[str, Any]]:
    """Validate all Python files in directory."""
    results = []

    for py_file in directory.rglob("*.py"):
        # Skip test files and common directories
        if any(skip in str(py_file) for skip in ['test', '__pycache__', '.venv', 'node_modules']):
            continue

        result = validate_file(py_file)
        if 'error' not in result:
            if result['violations'] or result['warnings']:
                results.append(result)

    return results


def print_report(results: List[Dict[str, Any]], verbose: bool = False):
    """Print validation report."""
    if not results:
        print("\n✓ No stateful architecture violations detected!")
        print("✓ Code follows stateless patterns correctly.")
        return True

    total_violations = sum(len(r['violations']) for r in results)
    total_warnings = sum(len(r['warnings']) for r in results)

    print(f"\n{'='*60}")
    print("Stateless Architecture Validation Report")
    print(f"{'='*60}")
    print(f"Files checked: {len(results) + len([r for r in results if not r['violations']])}")
    print(f"Critical violations: {total_violations}")
    print(f"Warnings: {total_warnings}")
    print(f"{'='*60}\n")

    for result in results:
        file_path = result['file']
        violations = result['violations']
        warnings = result['warnings']

        # Relative path for readability
        try:
            rel_path = Path(file_path).relative_to(Path.cwd())
        except:
            rel_path = file_path

        print(f"\n📁 {rel_path}")

        if violations:
            print("  ❌ CRITICAL VIOLATIONS:")
            for v in violations:
                print(f"     Line {v['line']}: {v['message']}")
                print(f"     Type: {v['type']} | Severity: {v['severity']}")
                if 'var_name' in v:
                    print(f"     Variable: {v['var_name']}")
                if 'class' in v:
                    print(f"     Class: {v['class']}")

        if warnings:
            print("  ⚠️  WARNINGS:")
            for w in warnings:
                print(f"     Line {w['line']}: {w['message']}")
                if verbose and 'func_name' in w:
                    print(f"     Function: {w['func_name']}")

    print(f"\n{'='*60}")

    if total_violations > 0:
        print("\n❌ FAILED: Stateless architecture violations found!")
        print("\nRemediation steps:")
        print("1. Remove instance variables that store conversation/message state")
        print("2. Pass database session as parameter to all data-access functions")
        print("3. Use database queries instead of in-memory caches")
        print("4. Specify maxsize for @lru_cache or remove it")
        return False
    else:
        print("\n✓ PASSED: No critical violations (warnings only)")
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Validate stateless agent architecture')
    parser.add_argument('path', help='File or directory to validate')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"Error: {path} does not exist")
        sys.exit(1)

    if path.is_file():
        result = validate_file(path)
        if 'error' in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        success = print_report([result] if result.get('violations') or result.get('warnings') else [])
    else:
        results = validate_directory(path)
        success = print_report(results, verbose=args.verbose)

    sys.exit(0 if success else 1)
