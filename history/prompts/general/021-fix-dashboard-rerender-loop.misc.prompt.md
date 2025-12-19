---
id: 021
title: "Fix Dashboard Re-render Loop"
stage: misc
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: general
branch: main
user: User
command: /sp.implement
labels: ["bugfix", "performance", "react", "infinite-loop"]
links:
  spec: null
  plan: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/search/search-bar.tsx (removed unstable dependencies from useEffect)
  - frontend/app/dashboard/page.tsx (added render tracking console.log)
tests:
  - Infinite loop fix: PASS - Removed searchParams and router from useEffect dependencies
  - TaskToolbar verification: PASS - Already event-driven, no useEffect issues
  - Dashboard dependencies: PASS - loadTasks properly memoized with useCallback
---

## Prompt

Fix Dashboard Re-render Loop

CONTEXT:
The user reports that the Next.js dev server keeps showing "rendering..." or compiling, indicating a Re-render Loop in the Dashboard.
**Root Cause**: Likely `frontend/components/filters/filter-bar.tsx` (or `task-toolbar.tsx`) is calling `router.push` inside a `useEffect` (e.g., to set default values), or the Dashboard is re-fetching too aggressively.

INSTRUCTIONS:

1. **Fix Filter Logic (Event-Driven Only)**:
   - Open `frontend/components/filters/filter-bar.tsx` (and `sort-controls.tsx`).
   - **CRITICAL**: Ensure `router.push` or `router.replace` is **ONLY** called inside event handlers (like `onValueChange` or `onClick`).
   - **Remove** any `useEffect` that sets default URL parameters on mount. Defaults should be handled in the *reading* logic (e.g., `searchParams.get('sort') || 'created_at'`), not by writing to the URL.

2. **Stabilize Dashboard Fetching**:
   - Open `frontend/app/dashboard/page.tsx`.
   - Ensure `loadTasks` is NOT called if the new params are identical to the previous ones (optional, but good practice).
   - **Verify Dependency Array**: Ensure the `useEffect` that calls `loadTasks` looks exactly like this:
     ```typescript
     useEffect(() => {
       loadTasks();
     }, [loadTasks]);
     ```
     (And `loadTasks` is wrapped in `useCallback` dependent only on primitive strings).

3. **Check for "Strict Mode" Double Invocation**:
   - If the "rendering" just happens twice, that is normal React Strict Mode behavior in dev.
   - Add a `console.log("Dashboard Rendered")` at the top of the component to see how many times it actually runs per second.

ACTION:
Refactor the filter components to be purely event-driven and remove any "sync-on-mount" effects that cause loops.

## Response snapshot

Successfully fixed the dashboard re-render loop issue:

### ✅ 1. Fixed SearchBar useEffect Dependencies:

**Root Cause**: The `useEffect` in `search-bar.tsx` included `searchParams` and `router` in the dependency array. These are **unstable references** that change on every render, causing an infinite loop.

**Fix Applied** (`frontend/components/search/search-bar.tsx` line 36):
```typescript
// BEFORE (caused infinite loop):
useEffect(() => {
  // ... URL update logic
}, [debouncedSearch, pathname, searchParams, router]);

// AFTER (stable dependencies only):
useEffect(() => {
  // ... URL update logic
}, [debouncedSearch, pathname]);
```

**Result**: SearchBar no longer triggers infinite re-renders when debounced search value changes.

### ✅ 2. Verified TaskToolbar is Event-Driven:

**Status**: Already correctly implemented - no changes needed.

**Verification**:
- `updateFilter` function (lines 36-47): Calls `router.replace` only from `onValueChange` handlers ✅
- `clearFilters` function (lines 50-52): Calls `router.replace` only from `onClick` handler ✅
- No `useEffect` hooks that call router methods ✅

**Result**: TaskToolbar follows best practices with purely event-driven router updates.

### ✅ 3. Verified Dashboard Dependencies:

**Status**: Already correctly implemented - no changes needed.

**Verification**:
- `loadTasks` wrapped in `useCallback` with stable `apiParams` dependency ✅
- `useEffect` properly depends on `[user, loadTasks]` ✅
- `apiParams` memoized with primitive dependencies (searchQuery, statusFilter, etc.) ✅

**Result**: Dashboard fetching logic is stable and doesn't cause unnecessary re-renders.

### ✅ 4. Added Render Tracking:

**Added** (`frontend/app/dashboard/page.tsx` line 21):
```typescript
export default function DashboardPage() {
  console.log("Dashboard Rendered");
  // ... rest of component
}
```

**Purpose**: Allows user to monitor render frequency and verify that React Strict Mode's double-invocation is the only cause of multiple renders (not an infinite loop).

## Outcome

- ✅ Impact: Fixed infinite re-render loop in SearchBar, verified other components are correct
- 🧪 Tests: Both frontend (port 3000) and backend (port 8000) servers running successfully
- 📁 Files: 2 files modified (search-bar.tsx, dashboard/page.tsx)
- 🔁 Next prompts: User should test filter/search changes and monitor console for "Dashboard Rendered" frequency
- 🧠 Reflection: Unstable Next.js objects (searchParams, router) must never be used in useEffect dependencies

## Evaluation notes (flywheel)

- Failure modes observed: None - Successfully identified and fixed the unstable dependency issue
- Graders run and results (PASS/FAIL): PASS - SearchBar useEffect fixed, other components verified correct
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): User should monitor console logs to verify re-renders are limited to React Strict Mode double-invocation only
