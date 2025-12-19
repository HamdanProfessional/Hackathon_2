---
id: task-crud-001
title: Fix Task Sorting Logic
stage: red
date: 2025-12-19
surface:
model: glm-4.6
feature: task-crud
branch: main
user: User
command: /sp.implement Fix Task Sorting Logic (Due Date & Priority)
labels: [bugfix, sorting, backend, frontend-integration]
links:
  spec: specs/features/task-crud.md
  ticket:
  adr:
  pr:
files:
  - path: backend/app/crud/task.py
    changes: Updated get_tasks_by_user function with proper field-specific sorting logic
  - path: frontend/components/search/task-toolbar.tsx
    changes: Verified frontend parameter mapping for sort options
tests:
  - name: API Sorting Test
    status: passed
    details: Tested due_date, priority, and title sorting via API calls
---

## Prompt

Fix Task Sorting Logic (Due Date & Priority)

CONTEXT:
The user reports that the Sort UI exists, but **only "Newest/Oldest" works**. Sorting by "Due Date" or "Priority" does nothing or behaves incorrectly.
**Root Cause**: The backend `get_tasks` function likely defaults to `created_at` if it doesn't recognize the `sort_by` parameter, or it fails to handle `null` values for due dates.

INSTRUCTIONS:

1. **Update Backend Logic (`backend/app/crud/task.py`)**:
   - Locate `get_tasks_by_user`.
   - **Implement Dynamic Sorting**:
     ```python
     # Example Logic
     if sort_by == "due_date":
         # Sort by date, put tasks with NO due date at the bottom (nulls_last)
         field = Task.due_date
         order = field.desc() if sort_order == "desc" else field.asc()
         query = query.order_by(order.nulls_last())

     elif sort_by == "priority":
         # If priority is a relationship, join it. If it's an ID/Enum, sort by that.
         # Assuming Priority ID or Level:
         field = Task.priority_id # or Task.priority if it's an Enum
         order = field.desc() if sort_order == "desc" else field.asc()
         query = query.order_by(order)

     else:
         # Default: Created At
         field = Task.created_at
         order = field.desc() if sort_order == "desc" else field.asc()
         query = query.order_by(order)
     ```

2. **Verify Frontend Values (`frontend/components/task/task-toolbar.tsx`)**:
   - Ensure the Sort Dropdown sends the exact strings the backend expects:
     - "Due Soon" -> `sort_by=due_date`, `sort_order=asc`
     - "Due Later" -> `sort_by=due_date`, `sort_order=desc`
     - "Priority (High)" -> `sort_by=priority`, `sort_order=desc` (Assuming High=3, Low=1)

ACTION:
Update the backend CRUD to handle specific sort fields and verify the frontend sends matching parameters.

## Response snapshot

The implementation successfully fixed the task sorting logic by:

1. **Identified the frontend parameter mapping** in `frontend/components/search/task-toolbar.tsx`:
   - `due_date-asc` → "Due Date (Earliest)"
   - `due_date-desc` → "Due Date (Latest)"
   - `priority-asc` → "Priority (Low to High)"
   - `priority-desc` → "Priority (High to Low)"
   - `title-asc` → "Title (A-Z)"
   - `title-desc` → "Title (Z-A)"

2. **Updated backend sorting logic** in `backend/app/crud/task.py`:
   - Added specific handling for `due_date` sorting with `.nulls_last()` to put tasks without due dates at the bottom
   - Added proper `priority` sorting using `priority_id` field
   - Added `title` sorting capability
   - Maintained backward compatibility with `created_at` as default

3. **Tested all sorting options** successfully via API calls:
   - Created test tasks with different priorities (1=Low, 2=Medium, 3=High)
   - Created tasks with and without due dates
   - Verified sorting works correctly for all fields

## Outcome

- ✅ Impact: Fixed critical sorting functionality that was broken for due_date and priority fields
- 🧪 Tests: All sorting options (due_date, priority, title) verified working via API tests
- 📁 Files: Modified backend/app/crud/task.py (22 lines changed)
- 🔁 Next prompts: None - sorting is now fully functional
- 🧠 Reflection: Simple but impactful fix - the original code was using getattr() which defaulted to created_at for unknown fields, causing sorting to appear broken

## Evaluation notes (flywheel)

- Failure modes observed: Tasks without due dates were not being handled properly (appearing randomly instead of at the end)
- Graders run and results (PASS/FAIL): PASS - All sorting options working as expected
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - Implementation is complete and working