"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar, CalendarDays, X, Repeat2, Sparkles } from "lucide-react";
import { Task } from "@/types";
import type { RecurrencePattern } from "@/types";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorMessage } from "@/components/ui/error-message";
import { toast } from "sonner";

interface TaskFormProps {
  task?: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description?: string;
    priority: "low" | "medium" | "high";
    due_date?: string;
    is_recurring?: boolean;
    recurrence_pattern?: RecurrencePattern;
  }) => Promise<void>;
  isSubmitting?: boolean;
}

const defaultFormData = {
  title: "",
  description: "",
  priority: "medium" as "low" | "medium" | "high",
  due_date: "",
  is_recurring: false,
  recurrence_pattern: undefined as RecurrencePattern | undefined,
};

export default function TaskForm({
  task,
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
}: TaskFormProps) {
  const [formData, setFormData] = useState<{
    title: string;
    description: string;
    priority: "low" | "medium" | "high";
    due_date: string;
    is_recurring: boolean;
    recurrence_pattern: RecurrencePattern | undefined;
  }>(defaultFormData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [subtasks, setSubtasks] = useState<Array<{title: string, description: string | null}>>([]);
  const [loadingBreakdown, setLoadingBreakdown] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || "",
        priority: (task.priority as "low" | "medium" | "high") || "medium",
        due_date: task.due_date || "",
        is_recurring: task.is_recurring || false,
        recurrence_pattern: task.recurrence_pattern,
      });
    } else {
      setFormData(defaultFormData);
    }
    setErrors({});
    setSubtasks([]); // Reset subtasks when dialog opens/closes
  }, [task, isOpen]);

  // Keyboard shortcut handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !isSubmitting) {
        e.preventDefault();
        const form = document.querySelector("form");
        if (form) {
          const submitEvent = new Event("submit", { cancelable: true });
          form.dispatchEvent(submitEvent);
        }
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, isSubmitting]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});

    // Convert date format if needed
    const submitData = {
      ...formData,
      description: formData.description || "",
      due_date: formData.due_date || undefined,
      is_recurring: formData.is_recurring,
      recurrence_pattern: formData.is_recurring ? formData.recurrence_pattern : undefined,
    };

    await onSubmit(submitData);
    onClose();
  };

  const handleInputChange = (
    field: keyof typeof formData,
    value: string | boolean
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

  const getTodayString = () => {
    return new Date().toISOString().split('T')[0];
  };

  // Get API base URL from environment or use default
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleAIBreakdown = async () => {
    if (!formData.title || formData.title.length < 10) {
      toast.error("Enter a more detailed task title (at least 10 characters) for AI breakdown");
      return;
    }

    setLoadingBreakdown(true);
    try {
      // Get token from localStorage
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("You must be logged in to use AI breakdown");
        setLoadingBreakdown(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/tasks/breakdown`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ task_title: formData.title })
      });

      if (response.ok) {
        const tasks = await response.json();
        setSubtasks(tasks);
        toast.success(`AI created ${tasks.length} subtasks!`);
      } else {
        const errorData = await response.json().catch(() => ({}));
        toast.error(errorData.detail || "Failed to generate breakdown");
      }
    } catch (error) {
      toast.error("Error generating breakdown. Please try again.");
    } finally {
      setLoadingBreakdown(false);
    }
  };

  const handleCreateAllSubtasks = async () => {
    // Create all subtasks as individual tasks
    for (const subtask of subtasks) {
      await onSubmit({
        ...formData,
        title: subtask.title,
        description: subtask.description || formData.description
      });
    }
    setSubtasks([]);
    toast.success(`Created ${subtasks.length} subtasks!`);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] bg-zinc-900 border-zinc-800">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-foreground">
            {task ? "Edit Task" : "Create New Task"}
          </DialogTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="absolute right-4 top-4 h-8 w-8 p-0 text-zinc-400 hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </Button>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-sm font-medium text-foreground">
              Title
              <span className="text-destructive ml-1">*</span>
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleInputChange("title", e.target.value)}
              placeholder="Enter task title"
              className={cn(
                "bg-zinc-800 border-zinc-700 focus:border-primary",
                errors.title && "border-destructive"
              )}
              maxLength={500}
              disabled={isSubmitting}
            />
            <ErrorMessage message={errors.title} />
          </div>

          {/* AI Breakdown Button - Only show for new tasks when title is long enough */}
          {!task && formData.title.length >= 30 && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAIBreakdown}
              disabled={loadingBreakdown || isSubmitting}
              className="w-full border-purple-500/50 hover:bg-purple-500/10 hover:border-purple-500 text-purple-400"
            >
              {loadingBreakdown ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-400 mr-2" />
                  AI is thinking...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  AI Breakdown: Generate Subtasks
                </>
              )}
            </Button>
          )}

          {/* AI-Generated Subtasks */}
          {subtasks.length > 0 && (
            <div className="space-y-3 p-4 rounded-lg border border-purple-500/30 bg-purple-500/5">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-medium text-purple-400">
                  AI-Generated Subtasks
                </Label>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setSubtasks([])}
                  className="h-6 text-xs text-muted-foreground hover:text-foreground"
                >
                  Clear
                </Button>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {subtasks.map((subtask, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-lg border border-zinc-700 bg-zinc-800/50"
                  >
                    <div className="font-medium text-sm text-foreground">
                      <span className="text-purple-400 mr-2">{index + 1}.</span>
                      {subtask.title}
                    </div>
                    {subtask.description && (
                      <div className="text-xs text-muted-foreground mt-1 ml-5">
                        {subtask.description}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              <Button
                type="button"
                variant="default"
                size="sm"
                onClick={handleCreateAllSubtasks}
                disabled={isSubmitting}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                Create All {subtasks.length} Subtasks
              </Button>
            </div>
          )}

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium text-foreground">
              Description
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange("description", e.target.value)}
              placeholder="Add a description (optional)"
              className="bg-zinc-800 border-zinc-700 focus:border-primary resize-none"
              rows={4}
              maxLength={2000}
              disabled={isSubmitting}
            />
            <p className="text-xs text-muted-foreground">
              {formData.description.length}/2000 characters
            </p>
          </div>

          {/* Priority */}
          <div className="space-y-2">
            <Label htmlFor="priority" className="text-sm font-medium text-foreground">
              Priority
            </Label>
            <Select
              value={formData.priority}
              onValueChange={(value: "LOW" | "MEDIUM" | "HIGH") =>
                handleInputChange("priority", value)
              }
              disabled={isSubmitting}
            >
              <SelectTrigger className="bg-zinc-800 border-zinc-700 focus:border-primary">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-zinc-800 border-zinc-700">
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Due Date */}
          <div className="space-y-2">
            <Label htmlFor="due_date" className="text-sm font-medium text-foreground">
              Due Date
            </Label>
            <div className="relative">
              <Input
                id="due_date"
                type="date"
                value={formData.due_date}
                onChange={(e) => handleInputChange("due_date", e.target.value)}
                min={getTodayString()}
                className="bg-zinc-800 border-zinc-700 focus:border-primary pl-10"
                disabled={isSubmitting}
              />
              <CalendarDays className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500 pointer-events-none" />
            </div>
          </div>

          {/* Recurring Task */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <Repeat2 className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="is_recurring" className="text-sm font-medium text-foreground">
                    Make this a recurring task
                  </Label>
                </div>
                <p className="text-xs text-muted-foreground ml-6">
                  Tasks will repeat automatically based on the selected pattern
                </p>
              </div>
              <Switch
                id="is_recurring"
                checked={formData.is_recurring}
                onCheckedChange={(checked) => handleInputChange("is_recurring", checked)}
                disabled={isSubmitting}
              />
            </div>

            {formData.is_recurring && (
              <div className="space-y-2 ml-6">
                <Label htmlFor="recurrence_pattern" className="text-sm font-medium text-foreground">
                  Recurrence Pattern
                </Label>
                <Select
                  value={formData.recurrence_pattern}
                  onValueChange={(value: RecurrencePattern) =>
                    handleInputChange("recurrence_pattern", value)
                  }
                  disabled={isSubmitting}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700 focus:border-primary">
                    <SelectValue placeholder="Select frequency" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-800 border-zinc-700">
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                    <SelectItem value="yearly">Yearly</SelectItem>
                  </SelectContent>
                </Select>
                {errors.recurrence_pattern && (
                  <p className="text-xs text-destructive">{errors.recurrence_pattern}</p>
                )}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 border-zinc-700 hover:bg-zinc-800"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 gradient-bg"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <LoadingSpinner size="sm" />
                  {task ? "Updating..." : "Creating..."}
                </span>
              ) : (
                task ? "Update Task" : "Create Task"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}