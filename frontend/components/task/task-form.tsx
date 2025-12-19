"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar, CalendarDays, X } from "lucide-react";
import { Task } from "@/types";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorMessage } from "@/components/ui/error-message";

interface TaskFormProps {
  task?: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description?: string;
    priority: "low" | "medium" | "high";
    due_date?: string;
  }) => Promise<void>;
  isSubmitting?: boolean;
}

const defaultFormData = {
  title: "",
  description: "",
  priority: "medium" as "low" | "medium" | "high",
  due_date: "",
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
  }>(defaultFormData);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Populate form when editing
  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || "",
        priority: (task.priority as "low" | "medium" | "high") || "medium",
        due_date: task.due_date || "",
      });
    } else {
      setFormData(defaultFormData);
    }
    setErrors({});
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
    };

    await onSubmit(submitData);
    onClose();
  };

  const handleInputChange = (
    field: keyof typeof formData,
    value: string
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