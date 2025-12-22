#!/usr/bin/env python3
"""Check if priorities exist in the database."""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from sqlalchemy import select, text


async def check_priorities():
    """Check what priorities exist in the database."""
    print("Checking priorities in database...")

    async for db in get_db():
        try:
            # Check if priorities table exists and has data
            result = await db.execute(
                text("SELECT id, name, level FROM priorities ORDER BY level")
            )
            priorities = result.fetchall()

            if priorities:
                print("\nPriorities found:")
                for priority in priorities:
                    print(f"  ID: {priority[0]}, Name: {priority[1]}, Level: {priority[2]}")
            else:
                print("\nNo priorities found in database!")
                print("The priorities table needs to be seeded with default values.")

                # Try to insert default priorities
                print("\nAttempting to seed default priorities...")
                await db.execute(
                    text("""
                        INSERT INTO priorities (id, name, level, color) VALUES
                        (1, 'low', 1, '#22c55e'),
                        (2, 'medium', 2, '#f59e0b'),
                        (3, 'high', 3, '#ef4444')
                        ON CONFLICT (id) DO NOTHING
                    """)
                )
                await db.commit()
                print("Default priorities seeded successfully!")

                # Check again
                result = await db.execute(
                    text("SELECT id, name, level FROM priorities ORDER BY level")
                )
                priorities = result.fetchall()

                print("\nPriorities after seeding:")
                for priority in priorities:
                    print(f"  ID: {priority[0]}, Name: {priority[1]}, Level: {priority[2]}")

            return True

        except Exception as e:
            print(f"Error checking priorities: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(check_priorities())
    sys.exit(0 if success else 1)
