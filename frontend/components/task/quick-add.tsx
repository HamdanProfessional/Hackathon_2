"use client";

import { useState, FormEvent } from "react";
import { Zap } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";

interface QuickAddProps {
  onTaskCreated?: () => void;
  placeholder?: string;
}

/**
 * QuickAdd component for creating tasks using natural language.
 *
 * Supports parsing of:
 * - Priority: urgent, important, high priority, low priority
 * - Due dates: today, tomorrow, Monday, next Friday, in 3 days, in 2 weeks
 * - Recurrence: daily, weekly, monthly, yearly, every [day]
 *
 * Examples:
 * - "Call mom tomorrow urgent" -> High priority, due tomorrow
 * - "Submit report by Friday important" -> High priority, due Friday
 * - "Weekly team meeting every Monday" -> Recurring weekly task
 */
export function QuickAdd({
  onTaskCreated,
  placeholder = "Quick add: 'Call mom tomorrow urgent' or 'Meeting every Friday'"
}: QuickAddProps) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    try {
      await apiClient.axiosInstance.post('/api/tasks/quick-add', { text: text.trim() });
      setText("");
      toast.success("Task created successfully!");
      onTaskCreated?.();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || "Failed to create task";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 w-full">
      <input
        type="text"
        placeholder={placeholder}
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={loading}
        className="flex-1 px-4 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all placeholder:text-muted-foreground/70"
        maxLength={500}
      />
      <button
        type="submit"
        disabled={loading || !text.trim()}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 font-medium whitespace-nowrap"
      >
        <Zap className="h-4 w-4" />
        {loading ? "Adding..." : "Add"}
      </button>
    </form>
  );
}

export default QuickAdd;
