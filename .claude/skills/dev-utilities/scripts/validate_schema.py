#!/usr/bin/env python3
"""Validate and synchronize API schemas between backend and frontend."""
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

TYPE_MAPPING = {
    'int': 'number',
    'str': 'string',
    'bool': 'boolean',
    'float': 'number',
    'datetime': 'string',
    'UUID': 'string',
}

def extract_pydantic_fields(file_path: Path) -> Dict[str, str]:
    """Extract fields from Pydantic model."""
    content = file_path.read_text()

    # Find class definition
    class_match = re.search(r'class (\w+)\([^)]*BaseModel[^)]*\):', content)
    if not class_match:
        return {}

    class_name = class_match.group(1)

    # Parse with AST
    tree = ast.parse(content)

    fields = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            field_name = node.target.id

            # Get type annotation
            if node.annotation:
                type_str = ast.unparse(node.annotation)
                fields[field_name] = convert_python_type(type_str)

    return fields

def extract_typescript_fields(file_path: Path) -> Dict[str, str]:
    """Extract fields from TypeScript interface."""
    content = file_path.read_text()

    # Find interface definition
    interface_match = re.search(r'interface (\w+) \{', content)
    if not interface_match:
        return {}

    class_name = interface_match.group(1)

    # Extract properties
    properties_match = re.search(r'interface \w+ \{(.*?)\}', content, re.DOTALL)
    if not properties_match:
        return {}

    properties_str = properties_match.group(1)
    fields = {}

    for line in properties_str.split('\n'):
        prop_match = re.match(r'\s*(\w+)\s*:\s*([^,;]+)', line)
        if prop_match:
            prop_name, prop_type = prop_match.groups()
            fields[prop_name] = prop_type.strip()

    return fields

def convert_python_type(python_type: str) -> str:
    """Convert Python type to TypeScript type."""
    # Handle Optional
    if python_type.startswith('Optional['):
        inner = python_type[9:-1]  # Remove Optional[ and ]
        inner_converted = convert_python_type(inner)
        return f"{inner_converted} | null"

    # Handle List
    if python_type.startswith('List['):
        inner = python_type[5:-1]  # Remove List[ and ]
        inner_converted = convert_python_type(inner)
        return f"{inner_converted}[]"

    # Handle Dict
    if python_type.startswith('Dict['):
        parts = python_type[5:-1].split(', ')  # Remove Dict[ and ]
        key_converted = convert_python_type(parts[0])
        value_converted = convert_python_type(parts[1])
        return f"Record<{key_converted}, {value_converted}>"

    # Direct mapping
    return TYPE_MAPPING.get(python_type, python_type)

def validate_sync(backend_file: Path, frontend_file: Path) -> Dict[str, Any]:
    """Validate backend and frontend schemas match."""
    backend_fields = extract_pydantic_fields(backend_file)
    frontend_fields = extract_typescript_fields(frontend_file)

    mismatches = []
    missing_in_frontend = set(backend_fields.keys()) - set(frontend_fields.keys())
    missing_in_backend = set(frontend_fields.keys()) - set(backend_fields.keys())

    if missing_in_frontend:
        mismatches.append(f"Missing in frontend: {', '.join(missing_in_frontend)}")

    if missing_in_backend:
        mismatches.append(f"Missing in backend: {', '.join(missing_in_backend)}")

    # Check type mismatches for common fields
    for field in backend_fields:
        if field in frontend_fields:
            backend_type = backend_fields[field].replace(' | null', '')
            frontend_type = frontend_fields[field].replace(' | null', '')

            if backend_type != frontend_type:
                mismatches.append(
                    f"Type mismatch for '{field}': "
                    f"backend={backend_fields[field]}, frontend={frontend_fields[field]}"
                )

    return {
        'valid': len(mismatches) == 0,
        'mismatches': mismatches
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validate_schema.py <backend_file> <frontend_file>")
        sys.exit(1)

    backend_file = Path(sys.argv[1])
    frontend_file = Path(sys.argv[2])

    result = validate_sync(backend_file, frontend_file)

    if result['valid']:
        print("✓ Schemas are synchronized")
    else:
        print("✗ Schema mismatches found:")
        for mismatch in result['mismatches']:
            print(f"  - {mismatch}")
        sys.exit(1)
