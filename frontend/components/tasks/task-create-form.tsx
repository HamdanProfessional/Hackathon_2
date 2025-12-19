"use client";

import { useState, FormEvent } from "react";
import VoiceInputButton from "@/components/ui/voice-input-button";
import type { TaskPriority } from "@/types/task";

interface TaskCreateFormProps {
  onSubmit: (title: string, description: string, priority: TaskPriority, tags: string) => Promise<void>;
}

export default function TaskCreateForm({ onSubmit }: TaskCreateFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [tags, setTags] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [voiceError, setVoiceError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setLoading(true);

    try {
      await onSubmit(title.trim(), description.trim(), priority, tags.trim());
      // Clear form on success
      setTitle("");
      setDescription("");
      setPriority("medium");
      setTags("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create task");
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceTitle = (transcript: string) => {
    setTitle(transcript);
    setVoiceError("");
  };

  const handleVoiceDescription = (transcript: string) => {
    setDescription(transcript);
    setVoiceError("");
  };

  const handleVoiceError = (error: string) => {
    setVoiceError(error);
    setTimeout(() => setVoiceError(""), 5000);
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Create New Task</h2>

      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-4 text-sm">
          {error}
        </div>
      )}

      {voiceError && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200 px-4 py-3 rounded-md mb-4 text-sm border border-yellow-200 dark:border-yellow-800">
          {voiceError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium mb-2">
            Title <span className="text-destructive">*</span>
          </label>
          <div className="flex gap-2">
            <input
              id="title"
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="flex-1 px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Enter task title or click mic to speak"
              disabled={loading}
              maxLength={500}
            />
            <VoiceInputButton
              onResult={handleVoiceTitle}
              onError={handleVoiceError}
              language="en-US"
            />
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-2">
            Description (optional)
          </label>
          <div className="flex gap-2">
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="flex-1 px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring min-h-[100px]"
              placeholder="Enter task description or click mic to speak"
              disabled={loading}
              maxLength={10000}
            />
            <VoiceInputButton
              onResult={handleVoiceDescription}
              onError={handleVoiceError}
              language="en-US"
            />
          </div>
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium mb-2">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
            className="w-full px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            disabled={loading}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="tags" className="block text-sm font-medium mb-2">
            Tags (optional, comma-separated)
          </label>
          <input
            id="tags"
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="w-full px-3 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="e.g., work, urgent, personal"
            disabled={loading}
            maxLength={500}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary text-primary-foreground py-2 rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Creating..." : "Create Task"}
        </button>
      </form>
    </div>
  );
}
