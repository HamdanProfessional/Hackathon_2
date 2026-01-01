#!/usr/bin/env python3
"""Validate conversation history management patterns."""
import ast
import sys
from pathlib import Path
from typing import List, Dict, Any


class StatelessValidator(ast.NodeVisitor):
    """Validate stateless architecture patterns."""

    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        """Check for stateful patterns in classes."""
        # Check for instance variables that might store conversation state
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        name = target.id.lower()
                        # Check for suspicious variable names
                        state_keywords = [
                            'conversation', 'message', 'chat', 'context',
                            'cache', 'state', 'history', 'session', 'memory'
                        ]
                        if any(keyword in name for keyword in state_keywords):
                            self.violations.append({
                                'type': 'instance_state',
                                'line': node.lineno,
                                'var_name': name,
                                'message': f'Possible stateful variable: {name}'
                            })

        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        """Check for global state."""
        for name in node.names:
            if any(keyword in name.lower() for keyword in
                   ['conversation', 'message', 'cache', 'state']):
                self.violations.append({
                    'type': 'global_state',
                    'line': node.lineno,
                    'var_name': name,
                    'message': f'Global state variable: {name}'
                })

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Check function patterns."""
        # Look for database session parameters
        params = [arg.arg for arg in node.args.args]
        if 'db' not in params and 'session' not in params:
            # Check if function might need database access
            if any(node.name.lower().startswith(prefix) for prefix in
                   ['get_', 'fetch_', 'load_', 'create_', 'update_', 'delete_']):
                self.warnings.append({
                    'type': 'missing_db_param',
                    'line': node.lineno,
                    'func_name': node.name,
                    'message': f'Function {node.name} might need database session'
                })

        self.generic_visit(node)


def validate_file(file_path: Path) -> Dict[str, Any]:
    """Validate a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code, filename=str(file_path))
    except Exception as e:
        return {'error': str(e)}

    validator = StatelessValidator()
    validator.visit(tree)

    return {
        'file': str(file_path),
        'violations': validator.violations,
        'warnings': validator.warnings
    }


def validate_directory(directory: Path) -> List[Dict[str, Any]]:
    """Validate all Python files in directory."""
    results = []

    for py_file in directory.rglob("*.py"):
        # Skip test files and __pycache__
        if 'test' in py_file.name or '__pycache__' in str(py_file):
            continue

        result = validate_file(py_file)
        if 'error' not in result:
            if result['violations'] or result['warnings']:
                results.append(result)

    return results


def print_results(results: List[Dict[str, Any]]):
    """Print validation results."""
    if not results:
        print("✓ No stateful patterns detected!")
        return

    print("\nValidation Results:")
    print("=" * 60)

    for result in results:
        print(f"\n📁 {result['file']}")

        if result['violations']:
            print("  ❌ VIOLATIONS:")
            for v in result['violations']:
                print(f"     Line {v['line']}: {v['message']}")
                print(f"     Type: {v['type']}")

        if result['warnings']:
            print("  ⚠️  WARNINGS:")
            for w in result['warnings']:
                print(f"     Line {w['line']}: {w['message']}")

    total_violations = sum(len(r['violations']) for r in results)
    total_warnings = sum(len(r['warnings']) for r in results)

    print("\n" + "=" * 60)
    print(f"Total: {total_violations} violations, {total_warnings} warnings")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_conversation.py <file_or_directory>")
        sys.exit(1)

    path = Path(sys.argv[1])

    if path.is_file():
        result = validate_file(path)
        if 'error' in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print_results([result] if result.get('violations') or result.get('warnings') else [])
    elif path.is_dir():
        results = validate_directory(path)
        print_results(results)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)
