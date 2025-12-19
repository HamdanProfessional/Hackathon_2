"use client";

import { Task } from "@/types/task";

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: number) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

export default function TaskItem({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskItemProps) {
  const formattedDate = new Date(task.created_at).toLocaleDateString();

  // Priority badge colors
  const priorityColors = {
    low: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
    medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
    high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  };

  // Parse tags
  const tagList = task.tags ? task.tags.split(",").map(t => t.trim()).filter(Boolean) : [];

  return (
    <div className="border border-border rounded-lg p-4 bg-card hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggleComplete(task.id)}
          className="mt-1 h-5 w-5 rounded border-gray-300 text-primary focus:ring-2 focus:ring-ring cursor-pointer"
        />

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <h3
              className={`text-lg font-medium ${
                task.completed
                  ? "line-through text-muted-foreground"
                  : "text-foreground"
              }`}
            >
              {task.title}
            </h3>
            {/* Priority Badge */}
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${priorityColors[task.priority]}`}>
              {task.priority.toUpperCase()}
            </span>
          </div>

          {task.description && (
            <p
              className={`mt-1 text-sm ${
                task.completed ? "text-muted-foreground/70" : "text-muted-foreground"
              }`}
            >
              {task.description}
            </p>
          )}

          {/* Tags */}
          {tagList.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {tagList.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          <p className="mt-2 text-xs text-muted-foreground">
            Created: {formattedDate}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          {onEdit && (
            <button
              onClick={() => onEdit(task)}
              className="px-3 py-1 text-sm text-primary hover:bg-primary/10 rounded transition-colors"
              aria-label="Edit task"
            >
              Edit
            </button>
          )}

          {onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              className="px-3 py-1 text-sm text-destructive hover:bg-destructive/10 rounded transition-colors"
              aria-label="Delete task"
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
