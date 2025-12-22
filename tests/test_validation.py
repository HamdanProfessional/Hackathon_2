"""Validation script for Phase I Todo CRUD implementation.

Tests all functional requirements and user stories programmatically.
"""

import sys
sys.path.insert(0, 'src')

from main import Task, TaskManager


def test_all_requirements():
    """Run comprehensive validation tests."""
    print("=== PHASE I VALIDATION TESTS ===\n")

    manager = TaskManager()
    passed = 0
    total = 0

    # FR-003: Auto-assign unique IDs
    total += 1
    id1 = manager.add_task("Task 1", "Description 1")
    id2 = manager.add_task("Task 2", "Description 2")
    id3 = manager.add_task("Task 3", "Description 3")
    if id1 == 1 and id2 == 2 and id3 == 3:
        print("[PASS] FR-003: Auto-incrementing IDs work")
        passed += 1
    else:
        print(f"[FAIL] FR-003: Expected IDs 1,2,3 but got {id1},{id2},{id3}")

    # FR-008: View tasks with formatting
    total += 1
    tasks = manager.view_tasks()
    if len(tasks) == 3 and tasks[0].id == 1:
        print("[PASS] FR-008: View tasks returns correct list")
        passed += 1
    else:
        print(f"[FAIL] FR-008: Expected 3 tasks, got {len(tasks)}")

    # FR-010: Mark tasks complete
    total += 1
    result = manager.mark_complete(1)
    task1 = manager.get_task(1)
    if result and task1 and task1.completed:
        print("[PASS] FR-010: Mark complete works")
        passed += 1
    else:
        print("[FAIL] FR-010: Mark complete failed")

    # FR-011: Update task details
    total += 1
    result = manager.update_task(2, "Updated Title", None)
    task2 = manager.get_task(2)
    if result and task2 and task2.title == "Updated Title" and task2.description == "Description 2":
        print("[PASS] FR-011: Update title works (preserves description)")
        passed += 1
    else:
        print("[FAIL] FR-011: Update failed")

    # FR-012: Skip update fields
    total += 1
    result = manager.update_task(2, None, "Updated Description")
    task2 = manager.get_task(2)
    if result and task2 and task2.title == "Updated Title" and task2.description == "Updated Description":
        print("[PASS] FR-012: Update description works (preserves title)")
        passed += 1
    else:
        print("[FAIL] FR-012: Skip field failed")

    # FR-013: Delete tasks
    total += 1
    result = manager.delete_task(3)
    tasks = manager.view_tasks()
    if result and len(tasks) == 2:
        print("[PASS] FR-013: Delete task works")
        passed += 1
    else:
        print(f"[FAIL] FR-013: Expected 2 tasks after delete, got {len(tasks)}")

    # FR-014: Error for non-existent ID
    total += 1
    result = manager.delete_task(999)
    if not result:
        print("[PASS] FR-014: Returns False for non-existent ID")
        passed += 1
    else:
        print("[FAIL] FR-014: Should return False for invalid ID")

    # Test ID gaps (deleted IDs not reused)
    total += 1
    id4 = manager.add_task("Task 4", "Description 4")
    if id4 == 4:  # Should be 4, not 3 (gap from deleted task)
        print("[PASS] ID Gap Handling: Deleted IDs not reused")
        passed += 1
    else:
        print(f"[FAIL] ID Gap Handling: Expected ID 4, got {id4}")

    # Test get_task method (from code review fix)
    total += 1
    task = manager.get_task(1)
    if task and task.id == 1 and task.completed:
        print("[PASS] get_task() method works correctly")
        passed += 1
    else:
        print("[FAIL] get_task() method failed")

    # Test get_task with non-existent ID
    total += 1
    task = manager.get_task(999)
    if task is None:
        print("[PASS] get_task() returns None for invalid ID")
        passed += 1
    else:
        print("[FAIL] get_task() should return None for invalid ID")

    # Edge case: Empty list handling
    total += 1
    empty_manager = TaskManager()
    tasks = empty_manager.view_tasks()
    if len(tasks) == 0:
        print("[PASS] Edge Case: Empty list returns empty array")
        passed += 1
    else:
        print("[FAIL] Edge Case: Empty list failed")

    print(f"\n=== RESULTS: {passed}/{total} tests passed ===")

    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED - Implementation is correct!")
        return 0
    else:
        print(f"[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(test_all_requirements())
