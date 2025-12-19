"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, Clock, Edit2, Trash2 } from "lucide-react";
import { Task } from "@/types";
import { cn } from "@/lib/utils";

interface TaskCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (task: Task) => void;
  onToggleComplete?: (taskId: number) => void;
  isCompleting?: boolean;
}

export default function TaskCard({
  task,
  onEdit,
  onDelete,
  onToggleComplete,
  isCompleting = false,
}: TaskCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const priorityColors = {
    HIGH: "border-l-red-500 bg-red-500/10",
    MEDIUM: "border-l-amber-500 bg-amber-500/10",
    LOW: "border-l-zinc-500 bg-zinc-500/10",
    high: "border-l-red-500 bg-red-500/10",
    medium: "border-l-amber-500 bg-amber-500/10",
    low: "border-l-zinc-500 bg-zinc-500/10",
  };

  const priorityLabels = {
    HIGH: "High",
    MEDIUM: "Medium",
    LOW: "Low",
    high: "High",
    medium: "Medium",
    low: "Low",
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== new Date().getFullYear() ? "numeric" : undefined,
    });
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete?.(task);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card
      className={cn(
        "group relative overflow-hidden transition-all duration-200 hover:shadow-glow-primary",
        "bg-zinc-900/50 backdrop-blur-md border-zinc-800",
        task.completed && "opacity-60",
        priorityColors[task.priority]
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          {/* Completion Checkbox */}
          <button
            onClick={() => onToggleComplete?.(task.id)}
            disabled={isCompleting}
            className={cn(
              "mt-1 flex h-5 w-5 items-center justify-center rounded border-2 transition-all duration-200",
              task.completed
                ? "border-primary bg-primary text-primary-foreground"
                : "border-zinc-600 hover:border-zinc-500",
              "disabled:opacity-50"
            )}
          >
            {task.completed && (
              <svg
                className="h-3 w-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={3}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
          </button>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            <h3
              className={cn(
                "text-lg font-semibold transition-all duration-200",
                task.completed
                  ? "text-zinc-500 line-through"
                  : "text-foreground"
              )}
            >
              {task.title}
            </h3>

            {task.description && (
              <p
                className={cn(
                  "mt-2 text-sm transition-all duration-200",
                  task.completed
                    ? "text-zinc-600 line-through"
                    : "text-muted-foreground"
                )}
              >
                {task.description}
              </p>
            )}

            {/* Task Meta */}
            <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
              {/* Priority Badge */}
              <div
                className={cn(
                  "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
                  task.priority === "high" && "bg-red-500/10 text-red-500",
                  task.priority === "medium" && "bg-amber-500/10 text-amber-500",
                  task.priority === "low" && "bg-zinc-500/10 text-zinc-500"
                )}
              >
                <span
                  className={cn(
                    "h-2 w-2 rounded-full",
                    task.priority === "high" && "bg-red-500",
                    task.priority === "medium" && "bg-amber-500",
                    task.priority === "low" && "bg-zinc-500"
                  )}
                />
                {priorityLabels[task.priority]}
              </div>

              {/* Due Date */}
              {task.due_date && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(task.due_date)}</span>
                </div>
              )}

              {/* Created At */}
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>Created {formatDate(task.created_at)}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit?.(task)}
              className="h-8 w-8 p-0 text-zinc-400 hover:text-foreground"
              aria-label={`Edit task: ${task.title}`}
            >
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              disabled={isDeleting}
              className="h-8 w-8 p-0 text-zinc-400 hover:text-destructive"
              aria-label={`Delete task: ${task.title}`}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>

      {/* Progress indicator for async operations */}
      {(isCompleting || isDeleting) && (
        <div className="absolute inset-0 bg-background/50 backdrop-blur-sm flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )}
    </Card>
  );
}