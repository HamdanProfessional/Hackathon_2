#!/usr/bin/env python3
"""
Console App Specification Validator

Validates that a console app implementation meets all Phase I requirements.
"""

import sys
import subprocess
import tempfile
from pathlib import Path


class SpecValidator:
    """Validate console app against specification."""

    def __init__(self, app_path: str):
        self.app_path = Path(app_path)
        self.results = []

    def check_file_structure(self) -> bool:
        """Verify required files exist."""
        required_files = [
            "__init__.py",
            "__main__.py",
            "models.py",
            "cli.py",
            "pyproject.toml",
        ]

        for file in required_files:
            if not (self.app_path / file).exists():
                self.results.append(f"❌ Missing required file: {file}")
                return False

        self.results.append("✅ File structure OK")
        return True

    def check_model_implementation(self) -> bool:
        """Verify Task and TaskList models exist."""
        models_file = self.app_path / "models.py"
        content = models_file.read_text()

        checks = [
            ("class Task", "Task class"),
            ("class TaskList", "TaskList class"),
            ("def add", "add method"),
            ("def get_all", "get_all method"),
            ("def update", "update method"),
            ("def delete", "delete method"),
        ]

        for code, name in checks:
            if code not in content:
                self.results.append(f"❌ Missing: {name}")
                return False

        self.results.append("✅ Model implementation OK")
        return True

    def check_cli_implementation(self) -> bool:
        """Verify CLI implements required commands."""
        cli_file = self.app_path / "cli.py"
        content = cli_file.read_text()

        required_commands = [
            "cmd_add",
            "cmd_list",
            "cmd_update",
            "cmd_delete",
            "cmd_complete",
        ]

        for cmd in required_commands:
            if cmd not in content:
                self.results.append(f"❌ Missing command: {cmd}")
                return False

        self.results.append("✅ CLI commands OK")
        return True

    def check_imports(self) -> bool:
        """Verify required dependencies."""
        pyproject = self.app_path / "pyproject.toml"
        content = pyproject.read_text()

        if "rich" not in content.lower():
            self.results.append("❌ Missing 'rich' dependency")
            return False

        self.results.append("✅ Dependencies OK")
        return True

    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        print(f"Validating: {self.app_path}")
        print("-" * 50)

        all_passed = True
        all_passed &= self.check_file_structure()
        all_passed &= self.check_model_implementation()
        all_passed &= self.check_cli_implementation()
        all_passed &= self.check_imports()

        print("-" * 50)
        for result in self.results:
            print(result)

        return all_passed


def main():
    """Run validation."""
    import sys

    app_path = sys.argv[1] if len(sys.argv) > 1 else "src"

    validator = SpecValidator(app_path)
    passed = validator.run_all_checks()

    if passed:
        print("\n✅ All checks passed!")
        return 0
    else:
        print("\n❌ Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
