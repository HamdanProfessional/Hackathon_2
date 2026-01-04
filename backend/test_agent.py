#!/usr/bin/env python
"""Test script to debug agent initialization."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("Testing Agent Initialization...")
print("=" * 80)

try:
    print("\n1. Importing AgentService...")
    from app.ai.agent import AgentService
    print("   ✓ Import successful")

    print("\n2. Creating AgentService instance...")
    agent = AgentService()
    print("   ✓ Agent initialized successfully")
    print(f"   Primary: {agent.primary_provider} ({agent.primary_model})")
    print(f"   Fallbacks: {[f['name'] for f in agent.fallback_clients]}")

except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
    sys.exit(1)

print("\n" + "=" * 80)
print("Test completed successfully!")
print("=" * 80)
