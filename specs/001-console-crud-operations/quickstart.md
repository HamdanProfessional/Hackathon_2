# Quickstart Guide: Console CRUD Operations

**Feature**: Console CRUD Operations - TODO List Manager
**Version**: Phase I (In-Memory)
**Date**: 2025-12-06

## Overview

This is a simple command-line todo list manager that stores tasks in memory. You can add, view, update, delete, and mark tasks as complete through a menu-driven interface.

**Important**: All data is stored in memory only and will be lost when you exit the application. This is intentional for Phase I.

---

## Prerequisites

**Python Version**: 3.13 or higher

Check your Python version:
```bash
python --version
```

Expected output: `Python 3.13.x` or higher

---

## Installation

No installation required! The application uses only Python standard library.

1. **Navigate to project directory**:
   ```bash
   cd C:\Users\User\Desktop\PIAIC_HACKATHON_1\Hackathon_2
   ```

2. **Verify file exists**:
   ```bash
   ls src/main.py
   ```

---

## Running the Application

### Windows

```bash
python src/main.py
```

### macOS / Linux

```bash
python3 src/main.py
```

### Expected Output

```
=== TODO LIST MANAGER ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Exit
Enter your choice (1-6):
```

---

## Basic Usage

### 1. Adding a Task

**Steps**:
1. Select option `1` from the menu
2. Enter task title when prompted (required)
3. Enter task description when prompted (optional - press Enter to skip)
4. See confirmation message with assigned ID

**Example Session**:
```
Enter your choice (1-6): 1
Enter task title: Buy groceries
Enter task description: Milk, eggs, bread
Task added with ID 1
```

**Notes**:
- Title cannot be empty (you'll be re-prompted if you try)
- Description can be empty (just press Enter)
- ID is assigned automatically starting from 1

---

### 2. Viewing Tasks

**Steps**:
1. Select option `2` from the menu
2. See formatted list of all tasks

**Example Output**:
```
Enter your choice (1-6): 2

=== YOUR TASKS ===
[1] [ ] Buy groceries
[2] [ ] Call dentist
[3] [x] Write report

Total tasks: 3 (1 completed, 2 pending)
```

**Format Explanation**:
- `[1]` - Task ID
- `[ ]` - Pending task (not completed)
- `[x]` - Completed task
- `Title` - Task title (description not shown in list)

**Empty List**:
If no tasks exist, you'll see:
```
No tasks available.
```

---

### 3. Marking a Task Complete

**Steps**:
1. Select option `5` from the menu
2. Enter the task ID number
3. Task status changes from `[ ]` to `[x]`

**Example Session**:
```
Enter your choice (1-6): 5
Enter task ID: 1
Task 1 marked as complete!
```

**Notes**:
- You can mark a completed task complete again (no error)
- If task ID doesn't exist, you'll see "Task with ID X not found"

---

### 4. Updating a Task

**Steps**:
1. Select option `3` from the menu
2. Enter the task ID number
3. Enter new title (or press Enter to keep current)
4. Enter new description (or press Enter to keep current)

**Example Session - Update both**:
```
Enter your choice (1-6): 3
Enter task ID: 1
Leave blank to keep current value
New title (Enter to skip): Buy organic groceries
New description (Enter to skip): Organic milk, free-range eggs, whole wheat bread
Task 1 updated successfully!
```

**Example Session - Update title only**:
```
Enter your choice (1-6): 3
Enter task ID: 1
Leave blank to keep current value
New title (Enter to skip): Buy groceries URGENT
New description (Enter to skip): [just press Enter]
Task 1 updated successfully!
```

**Example Session - Update description only**:
```
Enter your choice (1-6): 3
Enter task ID: 2
Leave blank to keep current value
New title (Enter to skip): [just press Enter]
New description (Enter to skip): Appointment at 2pm tomorrow
Task 2 updated successfully!
```

**Notes**:
- Pressing Enter on a field keeps its current value (skip)
- Title cannot be empty (if you try to update to empty, error)
- Marking complete is separate (use option 5, not option 3)

---

### 5. Deleting a Task

**Steps**:
1. Select option `4` from the menu
2. Enter the task ID number
3. Task is permanently removed

**Example Session**:
```
Enter your choice (1-6): 4
Enter task ID: 3
Task 3 deleted successfully!
```

**Notes**:
- Deleted task is gone permanently
- Task ID is never reused (next new task gets next sequential ID)
- Example: Delete task 2 from [1, 2, 3] → next new task gets ID 4, not 2

---

### 6. Exiting the Application

**Steps**:
1. Select option `6` from the menu
2. Application terminates

**Example Session**:
```
Enter your choice (1-6): 6
Thank you for using TODO List Manager!
```

**Warning**: ALL DATA IS LOST when you exit. This is expected behavior for Phase I.

---

## Complete Workflow Example

```
=== TODO LIST MANAGER ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete
6. Exit
Enter your choice (1-6): 1
Enter task title: Buy groceries
Enter task description: Milk and eggs
Task added with ID 1

Enter your choice (1-6): 1
Enter task title: Call dentist
Enter task description:
Task added with ID 2

Enter your choice (1-6): 1
Enter task title: Write report
Enter task description: Q4 summary due Friday
Task added with ID 3

Enter your choice (1-6): 2

=== YOUR TASKS ===
[1] [ ] Buy groceries
[2] [ ] Call dentist
[3] [ ] Write report

Total tasks: 3 (0 completed, 3 pending)

Enter your choice (1-6): 5
Enter task ID: 1
Task 1 marked as complete!

Enter your choice (1-6): 3
Enter task ID: 3
Leave blank to keep current value
New title (Enter to skip): Write Q4 report
New description (Enter to skip): Summary and projections due Friday
Task 3 updated successfully!

Enter your choice (1-6): 2

=== YOUR TASKS ===
[1] [x] Buy groceries
[2] [ ] Call dentist
[3] [ ] Write Q4 report

Total tasks: 3 (1 completed, 2 pending)

Enter your choice (1-6): 4
Enter task ID: 2
Task 2 deleted successfully!

Enter your choice (1-6): 2

=== YOUR TASKS ===
[1] [x] Buy groceries
[3] [ ] Write Q4 report

Total tasks: 2 (1 completed, 1 pending)

Enter your choice (1-6): 6
Thank you for using TODO List Manager!
```

---

## Error Handling

### Invalid Menu Choice

**Input**: `7` or `abc` or any non-1-6 number

**Output**:
```
Invalid choice. Please enter a number between 1 and 6
```
Menu redisplays, you can try again.

---

### Non-Existent Task ID

**Example**: Trying to update task ID 999 when it doesn't exist

**Output**:
```
Task with ID 999 not found
```
Returns to menu.

---

### Empty Title When Adding

**Input**: Press Enter without typing anything for title

**Output**:
```
Title cannot be empty. Please enter a title:
```
Re-prompts until you enter a non-empty title.

---

### Invalid ID Input (Non-Number)

**Input**: Typing `abc` when asked for task ID

**Output**:
```
Invalid ID. Please enter a number
```
Re-prompts for valid integer.

---

### Empty Title When Updating

**Input**: Trying to update title to empty string

**Output**:
```
Title cannot be empty. Title not updated.
```
Task keeps its current title, returns to menu.

---

## Tips & Best Practices

### 1. Use Descriptive Titles
Good: "Buy groceries for dinner party"
Bad: "Groceries"

### 2. Use Description for Details
Title: "Call dentist"
Description: "Annual cleaning appointment, mention tooth sensitivity"

### 3. Mark Tasks Complete as You Go
Builds momentum and gives satisfaction of progress tracking

### 4. Delete Unnecessary Tasks
Keep your list focused - delete tasks that are no longer relevant

### 5. Task IDs Never Reuse
If you delete task 3, the next task you create will NOT be ID 3
This is normal behavior - IDs increment forever

### 6. Remember: Data Is Not Saved
Exit loses everything - this is Phase I limitation
Future phases will add file/database persistence

---

## Troubleshooting

### Problem: "python: command not found"
**Solution**: Try `python3` instead (macOS/Linux)

### Problem: "python is not recognized" (Windows)
**Solution**: Add Python to PATH or use full path:
```bash
C:\Python313\python.exe src/main.py
```

### Problem: Python version too old
**Check**:
```bash
python --version
```
**Solution**: Install Python 3.13+ from python.org

### Problem: Application crashes on input
**Cause**: Code error (should not happen with proper implementation)
**Solution**: Report bug, check error message for details

### Problem: Can't exit the application
**Solution**: Press Ctrl+C (force quit) if option 6 doesn't work

---

## Keyboard Shortcuts

- **Ctrl+C**: Force quit the application (emergency exit)
- **Enter**: Submit input
- **Backspace**: Correct typing mistakes before pressing Enter

---

## Limitations (Phase I)

**By Design**:
- ✘ No data persistence (data lost on exit)
- ✘ No search or filter functionality
- ✘ No task due dates or priorities
- ✘ No task categories or tags
- ✘ No undo/redo
- ✘ No bulk operations (delete all, etc.)
- ✘ Description not shown in list view
- ✘ Cannot "uncomplete" a task (one-way change)

**Future Phases**:
- Phase II: File persistence (JSON or SQLite)
- Phase III: Search, filter, sorting
- Phase IV: Due dates, priorities, categories
- Phase V: Web or GUI interface

---

## Getting Help

**For application issues**:
- Check this quickstart guide
- Review error messages carefully
- Verify Python 3.13+ is installed
- Restart the application if stuck

**For feature requests**:
- Note that Phase I is intentionally limited
- Many features planned for future phases
- Focus on core CRUD functionality for now

---

## Next Steps

After mastering basic CRUD operations:
1. Try adding 10+ tasks to test with larger lists
2. Practice the update "skip" feature (pressing Enter to keep value)
3. Verify IDs don't reuse after deletions
4. Complete a full workflow (add → view → complete → update → delete)
5. Provide feedback for Phase II planning

---

**Enjoy using TODO List Manager!**

Remember: All data is temporary in Phase I. Future phases will add persistence and advanced features.
