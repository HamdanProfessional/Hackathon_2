/**
 * Task-related TypeScript type definitions
 */

export type TaskPriority = "low" | "medium" | "high";

export type RecurrencePattern = "daily" | "weekly" | "monthly" | "yearly";

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string;
  completed: boolean;
  priority: TaskPriority;
  tags: string;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  tags?: string;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  tags?: string;
  is_recurring?: boolean;
  recurrence_pattern?: RecurrencePattern;
}
