#!/usr/bin/env python3
"""Validate Conventional Commits format."""
import re
import subprocess
import sys

CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r'^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)'
    r'(\((?P<scope>[a-z0-9-]+)\))?'
    r'(?P<breaking>!)?: '
    r'(?P<description>.+)$'
)

VALID_TYPES = {
    'feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test',
    'build', 'ci', 'chore', 'revert'
}

def validate_commit_message(message: str) -> tuple[bool, str]:
    """Validate a commit message against Conventional Commits spec."""
    match = CONVENTIONAL_COMMIT_PATTERN.match(message)

    if not match:
        return False, "Invalid format. Expected: <type>(<scope>): <description>"

    groups = match.groupdict()
    description = groups['description']

    # Check description length
    if len(description) > 72:
        return False, f"Description too long ({len(description)} > 72 chars)"

    # Check description format
    if description[0].isupper():
        return False, "Description must start with lowercase"

    if description.endswith('.'):
        return False, "Description must not end with period"

    return True, "Valid commit message"

def get_last_commit_message() -> str:
    """Get the last commit message."""
    result = subprocess.run(
        ['git', 'log', '-1', '--pretty=%s'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def main():
    # Check if there's a commit message to validate
    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
    else:
        message = get_last_commit_message()
        if not message:
            print("No commit message found")
            sys.exit(1)

    is_valid, error = validate_commit_message(message)

    if is_valid:
        print(f"✓ Valid commit message: {message}")
        sys.exit(0)
    else:
        print(f"✗ Invalid commit message: {error}")
        print(f"\nMessage: {message}")
        print("\nExpected format: <type>(<scope>): <description>")
        print("\nValid types: " + ", ".join(sorted(VALID_TYPES)))
        print("\nExamples:")
        print("  feat(auth): add OAuth2 support")
        print("  fix(api): resolve null pointer exception")
        print("  feat(api)!: redesign endpoints")
        sys.exit(1)

if __name__ == "__main__":
    main()
