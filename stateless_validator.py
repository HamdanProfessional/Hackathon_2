#!/usr/bin/env python3
"""
Static analysis validator for stateless agent architecture compliance.

Detects violations of the constitutional requirement: NO in-memory conversation state.

Usage:
    python stateless_validator.py <directory>

Exit codes:
    0: No violations detected
    1: Violations detected
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Set, Dict, Any

class StatelessVisitor(ast.NodeVisitor):
    """AST visitor to detect stateless architecture violations."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: List[Dict[str, Any]] = []
        self.current_class = None
        self.current_function = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions to track class context."""
        old_class = self.current_class
        self.current_class = node.name

        # Check if this might be an agent class
        if any(keyword in node.name.lower() for keyword in ['agent', 'chat', 'assistant']):
            # Check __init__ for instance variables that might store state
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    for stmt in item.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute):
                                    var_name = target.attr
                                    # Check for state-storing patterns
                                    if any(state_keyword in var_name.lower()
                                          for state_keyword in [
                                              'cache', 'state', 'history', 'conversations',
                                              'messages', 'session', 'memory', 'context',
                                              'buffer', 'store', 'data'
                                          ]):
                                        self.violations.append({
                                            'type': 'instance_variable_state',
                                            'line': stmt.lineno,
                                            'variable': var_name,
                                            'class': node.name,
                                            'severity': 'high'
                                        })

        # Continue visiting
        self.generic_visit(node)
        self.current_class = old_class

    def visit_Assign(self, node: ast.Assign):
        """Visit assignments to detect global state."""
        # Only check for module-level assignments (outside of any function or class)
        # We determine this by checking if we're currently inside a class or function
        if self.current_class is None and self.current_function is None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Check for global variables that might store conversation state
                    # But exclude common local variable names
                    if (var_name not in ['messages', 'response', 'result', 'data'] and
                        any(keyword in var_name.lower()
                            for keyword in [
                                'conversations', 'chat_sessions',
                                'user_states', 'contexts', 'histories', 'session_cache'
                            ])):
                        self.violations.append({
                            'type': 'global_variable_state',
                            'line': node.lineno,
                            'variable': var_name,
                            'severity': 'high'
                        })

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions to track context."""
        old_function = self.current_function
        self.current_function = node.name

        # Check for @lru_cache without maxsize (unbounded cache)
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Name) and decorator.id == 'lru_cache' or
                (isinstance(decorator, ast.Call) and
                 isinstance(decorator.func, ast.Name) and
                 decorator.func.id == 'lru_cache')):

                # Check if maxsize is None or missing
                if isinstance(decorator, ast.Call):
                    maxsize = None
                    for keyword in decorator.keywords:
                        if keyword.arg == 'maxsize':
                            if isinstance(keyword.value, ast.Constant):
                                maxsize = keyword.value.value
                            elif isinstance(keyword.value, ast.NameConstant):  # Python < 3.8
                                maxsize = keyword.value.value
                    if maxsize is None:
                        self.violations.append({
                            'type': 'unbounded_cache',
                            'line': node.lineno,
                            'function': node.name,
                            'severity': 'medium'
                        })
                else:
                    # @lru_cache without parentheses means unbounded
                    self.violations.append({
                        'type': 'unbounded_cache',
                        'line': node.lineno,
                        'function': node.name,
                        'severity': 'medium'
                    })

        self.generic_visit(node)
        self.current_function = old_function

def validate_file(filepath: Path) -> List[Dict[str, Any]]:
    """Validate a single Python file for stateless architecture violations."""
    violations = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content, filename=str(filepath))

        # Visit AST
        visitor = StatelessVisitor(str(filepath))
        visitor.visit(tree)

        violations.extend(visitor.violations)

    except SyntaxError as e:
        violations.append({
            'type': 'syntax_error',
            'line': e.lineno or 0,
            'error': str(e),
            'severity': 'high'
        })
    except Exception as e:
        violations.append({
            'type': 'parse_error',
            'error': str(e),
            'severity': 'medium'
        })

    return violations

def validate_directory(directory: Path) -> Dict[str, Any]:
    """Validate all Python files in a directory."""
    all_violations = []
    files_scanned = 0
    files_with_violations = 0

    # Find all Python files
    python_files = list(directory.rglob('*.py'))

    # Skip certain directories
    skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache'}
    python_files = [f for f in python_files if not any(skip_dir in f.parts for skip_dir in skip_dirs)]

    for filepath in python_files:
        violations = validate_file(filepath)
        if violations:
            all_violations.append({
                'file': str(filepath.relative_to(directory)),
                'violations': violations
            })
            files_with_violations += 1
        files_scanned += 1

    # Count severity
    high_severity = sum(len([v for v in f['violations'] if v.get('severity') == 'high'])
                        for f in all_violations)
    medium_severity = sum(len([v for v in f['violations'] if v.get('severity') == 'medium'])
                          for f in all_violations)

    return {
        'files_scanned': files_scanned,
        'files_with_violations': files_with_violations,
        'high_severity': high_severity,
        'medium_severity': medium_severity,
        'violations_by_file': all_violations
    }

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python stateless_validator.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])

    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory")
        sys.exit(1)

    print(f"Validating stateless architecture in: {directory}")
    print()

    # Validate directory
    result = validate_directory(directory)

    # Print results
    if result['violations_by_file']:
        print("[X] Stateless architecture violations detected:\n")

        for file_result in result['violations_by_file']:
            print(f"File: {file_result['file']}")

            for violation in file_result['violations']:
                severity_marker = "[HIGH]" if violation.get('severity') == 'high' else "[MED]"
                line_info = f"Line {violation['line']}: " if 'line' in violation else ""

                if violation['type'] == 'instance_variable_state':
                    print(f"  {severity_marker} {line_info}Instance variable \"{violation['variable']}\" appears to store conversation state (class: {violation['class']})")
                elif violation['type'] == 'global_variable_state':
                    print(f"  {severity_marker} {line_info}Global variable \"{violation['variable']}\" might store conversation state")
                elif violation['type'] == 'unbounded_cache':
                    print(f"  {severity_marker} {line_info}Function \"{violation['function']}\" uses lru_cache without maxsize")
                elif violation['type'] == 'syntax_error':
                    print(f"  {severity_marker} {line_info}Syntax error: {violation['error']}")
                else:
                    print(f"  {severity_marker} {line_info}{violation['type']}")

            print()

        # Print summary
        print(f"Summary:")
        print(f"  Files scanned: {result['files_scanned']}")
        print(f"  Files with violations: {result['files_with_violations']}")
        print(f"  High severity: {result['high_severity']}")
        print(f"  Medium severity: {result['medium_severity']}")
        print()
        print("Please fix these violations to comply with stateless architecture requirements.")

        sys.exit(1)
    else:
        print("[OK] No stateless architecture violations detected")
        print(f"   Scanned {result['files_scanned']} Python files")
        sys.exit(0)

if __name__ == '__main__':
    main()