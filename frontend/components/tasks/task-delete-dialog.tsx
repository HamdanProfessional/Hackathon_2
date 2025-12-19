"use client";

import { useState } from "react";
import { Task } from "@/types/task";

interface TaskDeleteDialogProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (taskId: number) => Promise<void>;
}

export default function TaskDeleteDialog({
  task,
  isOpen,
  onClose,
  onConfirm,
}: TaskDeleteDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleConfirm = async () => {
    if (!task) return;

    setError("");
    setLoading(true);

    try {
      await onConfirm(task.id);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete task");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setError("");
    onClose();
  };

  if (!isOpen || !task) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-card border border-border rounded-lg p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-semibold mb-4 text-destructive">Delete Task</h2>

        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-4 text-sm">
            {error}
          </div>
        )}

        <p className="text-muted-foreground mb-2">
          Are you sure you want to delete this task? This action cannot be undone.
        </p>

        <div className="bg-muted/50 border border-border rounded-md p-3 mb-6">
          <p className="font-medium text-foreground">{task.title}</p>
          {task.description && (
            <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
          )}
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleCancel}
            disabled={loading}
            className="flex-1 px-4 py-2 border border-border rounded-md hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={loading}
            className="flex-1 bg-destructive text-destructive-foreground py-2 rounded-md hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
