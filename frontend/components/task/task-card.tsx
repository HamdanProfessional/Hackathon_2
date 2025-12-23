"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Calendar, Clock, Edit2, Trash2, Repeat2, ListTodo, Plus, Check, Minus } from "lucide-react";
import { Task, Subtask } from "@/types";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

interface TaskCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (task: Task) => void;
  onToggleComplete?: (taskId: number) => void;
  isCompleting?: boolean;
  viewMode?: 'grid' | 'list';
}

export default function TaskCard({
  task,
  onEdit,
  onDelete,
  onToggleComplete,
  isCompleting = false,
  viewMode = 'grid',
}: TaskCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [subtasks, setSubtasks] = useState<Subtask[]>([]);
  const [newSubtask, setNewSubtask] = useState("");
  const [showSubtasks, setShowSubtasks] = useState(false);
  const [isLoadingSubtasks, setIsLoadingSubtasks] = useState(false);

  // Load subtasks when subtasks section is shown
  useEffect(() => {
    if (showSubtasks && subtasks.length === 0) {
      loadSubtasks();
    }
  }, [showSubtasks]);

  const loadSubtasks = async () => {
    setIsLoadingSubtasks(true);
    try {
      const response = await apiClient.getSubtasks(task.id);
      setSubtasks(response);
    } catch (error) {
      console.error("Failed to load subtasks", error);
      toast.error("Failed to load subtasks");
    } finally {
      setIsLoadingSubtasks(false);
    }
  };

  const addSubtask = async () => {
    if (!newSubtask.trim()) return;
    try {
      await apiClient.createSubtask(task.id, { title: newSubtask });
      setNewSubtask("");
      loadSubtasks();
      toast.success("Subtask added");
    } catch (error) {
      console.error("Failed to add subtask", error);
      toast.error("Failed to add subtask");
    }
  };

  const toggleSubtask = async (subtaskId: number, completed: boolean) => {
    try {
      await apiClient.updateSubtask(subtaskId, completed);
      setSubtasks(subtasks.map(s => s.id === subtaskId ? { ...s, completed } : s));
    } catch (error) {
      console.error("Failed to update subtask", error);
      toast.error("Failed to update subtask");
    }
  };

  const deleteSubtask = async (subtaskId: number) => {
    try {
      await apiClient.deleteSubtask(subtaskId);
      setSubtasks(subtasks.filter(s => s.id !== subtaskId));
      toast.success("Subtask deleted");
    } catch (error) {
      console.error("Failed to delete subtask", error);
      toast.error("Failed to delete subtask");
    }
  };

  const completedSubtasksCount = subtasks.filter(s => s.completed).length;

  // Calculate task age in days
  const getTaskAge = (createdAt: string): number => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffTime = now.getTime() - created.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // Get age color class for left border
  const getAgeBorderColor = (age: number): string => {
    if (age < 3) return 'border-l-green-500'; // New - green
    if (age < 7) return 'border-l-yellow-500'; // Aging - yellow
    if (age < 14) return 'border-l-orange-500'; // Old - orange
    return 'border-l-red-500'; // Critical - red
  };

  const taskAge = getTaskAge(task.created_at);
  const ageBorderColor = getAgeBorderColor(taskAge);

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
        // Use priority colors for background tint
        task.priority === "high" && "bg-red-500/5",
        task.priority === "medium" && "bg-amber-500/5",
        task.priority === "low" && "bg-zinc-500/5",
        // Age-based left border
        viewMode === 'list' ? `border-l-4 ${ageBorderColor}` : "",
        viewMode === 'grid' ? `border-l-4 ${ageBorderColor}` : ""
      )}
    >
      <CardContent className={cn(
        viewMode === 'grid' ? "p-6" : "p-3"
      )}>
        <div className={cn(
          "flex gap-4",
          viewMode === 'list' ? "flex-row items-center w-full" : "items-start"
        )}>
          {/* Completion Checkbox */}
          <button
            onClick={() => onToggleComplete?.(task.id)}
            disabled={isCompleting}
            className={cn(
              "flex h-5 w-5 items-center justify-center rounded border-2 transition-all duration-200",
              viewMode === 'list' ? "mt-0" : "mt-1",
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
          <div className={cn(
            "min-w-0",
            viewMode === 'list' ? "flex-1 flex items-center justify-between" : "flex-1"
          )}>
            <div className={viewMode === 'list' ? "flex items-center gap-4 flex-1" : ""}>
              <div className={viewMode === 'list' ? "flex-1 min-w-0" : ""}>
                <h3
                  className={cn(
                    "font-semibold transition-all duration-200",
                    viewMode === 'grid' ? "text-lg" : "text-base",
                    task.completed
                      ? "text-zinc-500 line-through"
                      : "text-foreground"
                  )}
                >
                  {task.title}
                </h3>

                {task.description && viewMode === 'grid' && (
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
              </div>

              {/* Task Meta - shown differently based on view mode */}
              <div className={cn(
                "flex items-center gap-3 text-xs text-muted-foreground",
                viewMode === 'list' ? "flex-row" : "mt-4 flex-wrap"
              )}>
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

                {/* Recurring Indicator */}
                {task.is_recurring && task.recurrence_pattern && (
                  <div className="flex items-center gap-1 text-primary">
                    <Repeat2 className="h-3 w-3" />
                    <span className="capitalize">{task.recurrence_pattern}</span>
                  </div>
                )}

                {/* Created At - only in grid view */}
                {viewMode === 'grid' && (
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>Created {formatDate(task.created_at)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className={cn(
            "flex items-center gap-2 transition-opacity duration-200",
            viewMode === 'list' ? "opacity-100" : "opacity-0 group-hover:opacity-100"
          )}>
            {/* Subtasks Toggle Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSubtasks(!showSubtasks)}
              className={cn(
                "h-8 px-2 text-zinc-400 hover:text-foreground gap-1",
                showSubtasks && "text-primary bg-primary/10"
              )}
              aria-label={`Toggle subtasks for: ${task.title}`}
            >
              <ListTodo className="h-4 w-4" />
              {subtasks.length > 0 && (
                <span className="text-xs">{completedSubtasksCount}/{subtasks.length}</span>
              )}
            </Button>
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

      {/* Subtasks Section */}
      {showSubtasks && (
        <div className="px-6 pb-4 pt-0 border-t border-border/50 mt-2">
          {/* Subtasks Header */}
          <div className="flex items-center justify-between py-2">
            <span className="text-xs font-medium text-muted-foreground">
              Subtasks
            </span>
            {subtasks.length > 0 && (
              <span className="text-xs text-muted-foreground">
                {completedSubtasksCount}/{subtasks.length} completed
              </span>
            )}
          </div>

          {/* Loading State */}
          {isLoadingSubtasks && (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
            </div>
          )}

          {/* Subtasks List */}
          {!isLoadingSubtasks && subtasks.length > 0 && (
            <div className="space-y-1 mb-3">
              {subtasks.map((subtask) => (
                <div
                  key={subtask.id}
                  className="flex items-center gap-2 text-sm py-1 px-2 rounded hover:bg-zinc-800/50 transition-colors"
                >
                  <button
                    onClick={() => toggleSubtask(subtask.id, !subtask.completed)}
                    className={cn(
                      "flex-shrink-0 w-4 h-4 rounded border flex items-center justify-center transition-colors",
                      subtask.completed
                        ? "bg-primary border-primary"
                        : "border-zinc-600 hover:border-zinc-500"
                    )}
                  >
                    {subtask.completed && <Check className="w-3 h-3 text-primary-foreground" />}
                  </button>
                  <span
                    className={cn(
                      "flex-1 truncate",
                      subtask.completed && "line-through text-muted-foreground"
                    )}
                  >
                    {subtask.title}
                  </span>
                  <button
                    onClick={() => deleteSubtask(subtask.id)}
                    className="flex-shrink-0 text-muted-foreground hover:text-destructive transition-colors"
                    aria-label={`Delete subtask: ${subtask.title}`}
                  >
                    <Minus className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add New Subtask Input */}
          <div className="flex gap-2">
            <Input
              placeholder="Add a subtask..."
              value={newSubtask}
              onChange={(e) => setNewSubtask(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addSubtask()}
              className="h-8 text-sm bg-zinc-900/50 border-zinc-700"
              disabled={isLoadingSubtasks}
            />
            <Button
              size="sm"
              onClick={addSubtask}
              disabled={!newSubtask.trim() || isLoadingSubtasks}
              className="h-8 px-2"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Progress indicator for async operations */}
      {(isCompleting || isDeleting) && (
        <div className="absolute inset-0 bg-background/50 backdrop-blur-sm flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )}
    </Card>
  );
}