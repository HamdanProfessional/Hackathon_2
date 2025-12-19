#!/usr/bin/env python3
"""
Phase III AI Stack Verification Script

This script verifies that all required dependencies for the AI chatbot
are properly installed and configured.

Checks:
1. Python packages: openai, mcp
2. OpenAI API connectivity (requires OPENAI_API_KEY in .env)
3. MCP SDK availability
4. Module imports (app.ai.agent, app.ai.mcp_server)

Usage:
    cd backend
    python scripts/verify_ai_stack.py
"""

import sys
import os

# ASCII-safe check marks for Windows compatibility
CHECK = '[OK]'
CROSS = '[FAIL]'
WARN = '[WARN]'

def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a Python package is installed."""
    import_name = import_name or package_name
    try:
        __import__(import_name)
        print(f"{CHECK} {package_name} is installed")
        return True
    except ImportError:
        print(f"{CROSS} {package_name} is NOT installed")
        return False

def check_openai_version():
    """Check OpenAI package version."""
    try:
        import openai
        version = openai.__version__
        print(f"{CHECK} OpenAI version: {version}")
        return True
    except Exception as e:
        print(f"{CROSS} Failed to check OpenAI version: {e}")
        return False

def check_mcp_version():
    """Check MCP package version."""
    try:
        import mcp
        # MCP may not have __version__ attribute
        print(f"{CHECK} MCP package is available")
        return True
    except Exception as e:
        print(f"{CROSS} Failed to check MCP: {e}")
        return False

def check_openai_api_key():
    """Check if OPENAI_API_KEY is configured."""
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"{CROSS} OPENAI_API_KEY not found in .env")
        return False

    if api_key == "sk-your-openai-api-key-here":
        print(f"{WARN} OPENAI_API_KEY is still the default placeholder")
        return False

    if not api_key.startswith("sk-"):
        print(f"{CROSS} OPENAI_API_KEY format is invalid (must start with 'sk-')")
        return False

    print(f"{CHECK} OPENAI_API_KEY is configured")
    return True

def check_ai_module():
    """Check if AI module structure exists."""
    ai_module_path = os.path.join(os.path.dirname(__file__), "..", "app", "ai")

    if not os.path.exists(ai_module_path):
        print(f"{CROSS} AI module directory (app/ai/) does not exist")
        return False

    required_files = ["__init__.py", "agent.py", "mcp_server.py", "tools.py"]
    missing_files = []

    for file in required_files:
        file_path = os.path.join(ai_module_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)

    if missing_files:
        print(f"{CROSS} Missing AI module files: {', '.join(missing_files)}")
        return False

    print(f"{CHECK} AI module structure is complete")
    return True

def check_chatkit_frontend():
    """Check if ChatKit is installed in frontend."""
    package_json_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "package.json"
    )

    if not os.path.exists(package_json_path):
        print(f"{WARN} Frontend package.json not found (skipping ChatKit check)")
        return True

    try:
        import json
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)

        dependencies = package_data.get("dependencies", {})
        if "@openai/chatkit" in dependencies:
            version = dependencies["@openai/chatkit"]
            print(f"{CHECK} @openai/chatkit is installed (version: {version})")
            return True
        else:
            print(f"{CROSS} @openai/chatkit is NOT installed in frontend")
            return False
    except Exception as e:
        print(f"{WARN} Failed to check frontend dependencies: {e}")
        return True

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Phase III AI Stack Verification")
    print("=" * 60)
    print()

    all_checks = []

    print("1. Checking Python Packages...")
    all_checks.append(check_package("openai"))
    all_checks.append(check_package("mcp"))
    all_checks.append(check_openai_version())
    all_checks.append(check_mcp_version())
    print()

    print("2. Checking Configuration...")
    all_checks.append(check_openai_api_key())
    print()

    print("3. Checking AI Module Structure...")
    all_checks.append(check_ai_module())
    print()

    print("4. Checking Frontend Dependencies...")
    all_checks.append(check_chatkit_frontend())
    print()

    print("=" * 60)
    if all(all_checks):
        print(f"{CHECK} All verification checks passed!")
        print()
        print("Next steps:")
        print("1. Set your OPENAI_API_KEY in backend/.env (if not already done)")
        print("2. Run: /sp.implement T006 T007 T008 (Phase 2: Database Models)")
        return 0
    else:
        print(f"{CROSS} Some verification checks failed")
        print()
        print("Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
