"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  getTasks,
  createTask,
  updateTask,
  toggleTaskCompletion,
  deleteTask,
  logout,
} from "@/lib/api-client";
import { isAuthenticated } from "@/lib/auth";
import TaskCreateForm from "@/components/tasks/task-create-form";
import TaskList from "@/components/tasks/task-list";
import TaskEditDialog from "@/components/tasks/task-edit-dialog";
import TaskDeleteDialog from "@/components/tasks/task-delete-dialog";
import type { Task } from "@/types/task";

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("created-desc");

  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);

  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);

  // Check authentication
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError("");
      const fetchedTasks = await getTasks();
      setTasks(fetchedTasks);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (title: string, description: string, priority: string, tags: string) => {
    try {
      const newTask = await createTask(title, description, priority as any, tags);
      setTasks([newTask, ...tasks]); // Add to beginning of list
      showSuccess("Task created successfully!");
    } catch (err) {
      throw err; // Let form handle error
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    try {
      const updatedTask = await toggleTaskCompletion(taskId);
      setTasks(tasks.map((t) => (t.id === taskId ? updatedTask : t)));
      showSuccess("Task updated!");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update task");
    }
  };

  const handleEdit = (task: Task) => {
    setTaskToEdit(task);
    setEditDialogOpen(true);
  };

  const handleSaveEdit = async (taskId: number, title: string, description: string, priority: string, tags: string) => {
    try {
      const updatedTask = await updateTask(taskId, { title, description, priority: priority as any, tags });
      setTasks(tasks.map((t) => (t.id === taskId ? updatedTask : t)));
      showSuccess("Task updated successfully!");
    } catch (err: any) {
      throw err; // Let dialog handle error display
    }
  };

  const handleDeleteClick = (taskId: number) => {
    const task = tasks.find((t) => t.id === taskId);
    if (task) {
      setTaskToDelete(task);
      setDeleteDialogOpen(true);
    }
  };

  const handleConfirmDelete = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      setTasks(tasks.filter((t) => t.id !== taskId));
      showSuccess("Task deleted successfully!");
    } catch (err: any) {
      throw err; // Let dialog handle error display
    }
  };

  const handleLogout = () => {
    logout();
  };

  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  // Filter and sort tasks
  const filteredAndSortedTasks = tasks
    .filter((task) => {
      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const titleMatch = task.title.toLowerCase().includes(query);
        const descriptionMatch = task.description.toLowerCase().includes(query);
        const tagsMatch = task.tags.toLowerCase().includes(query);
        const priorityMatch = task.priority.toLowerCase().includes(query);

        if (!titleMatch && !descriptionMatch && !tagsMatch && !priorityMatch) {
          return false;
        }
      }

      // Priority filter
      if (filterPriority !== "all" && task.priority !== filterPriority) {
        return false;
      }

      // Status filter
      if (filterStatus === "active" && task.completed) {
        return false;
      }
      if (filterStatus === "completed" && !task.completed) {
        return false;
      }

      return true;
    })
    .sort((a, b) => {
      // Sort logic
      switch (sortBy) {
        case "created-desc":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case "created-asc":
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case "title-asc":
          return a.title.localeCompare(b.title);
        case "title-desc":
          return b.title.localeCompare(a.title);
        case "priority":
          const priorityOrder = { high: 0, medium: 1, low: 2 };
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        case "status":
          return (a.completed ? 1 : 0) - (b.completed ? 1 : 0);
        default:
          return 0;
      }
    });

  const completedCount = filteredAndSortedTasks.filter((t) => t.completed).length;
  const totalCount = filteredAndSortedTasks.length;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Todo Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              {totalCount} tasks ({completedCount} completed)
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/chat"
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              AI Chat
            </Link>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm border border-border rounded-md hover:bg-accent transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200 px-4 py-3 rounded-md mb-6 border border-green-200 dark:border-green-800">
            {successMessage}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Search and Filter Bar */}
        <div className="bg-card border border-border rounded-lg p-4 mb-6 space-y-4">
          {/* Search */}
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search tasks by title, description, tags, or priority..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label="Clear search"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Filters and Sort */}
          <div className="flex flex-wrap gap-3">
            {/* Priority Filter */}
            <div className="flex-1 min-w-[140px]">
              <label htmlFor="filter-priority" className="block text-xs font-medium mb-1 text-muted-foreground">
                Priority
              </label>
              <select
                id="filter-priority"
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                className="w-full px-3 py-1.5 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="all">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            {/* Status Filter */}
            <div className="flex-1 min-w-[140px]">
              <label htmlFor="filter-status" className="block text-xs font-medium mb-1 text-muted-foreground">
                Status
              </label>
              <select
                id="filter-status"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-1.5 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="all">All Tasks</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Sort By */}
            <div className="flex-1 min-w-[140px]">
              <label htmlFor="sort-by" className="block text-xs font-medium mb-1 text-muted-foreground">
                Sort By
              </label>
              <select
                id="sort-by"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-1.5 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="created-desc">Newest First</option>
                <option value="created-asc">Oldest First</option>
                <option value="priority">Priority (High → Low)</option>
                <option value="title-asc">Title (A → Z)</option>
                <option value="title-desc">Title (Z → A)</option>
                <option value="status">Status (Active First)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Create Task Form */}
        <TaskCreateForm onSubmit={handleCreateTask} />

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading tasks...</p>
          </div>
        ) : (
          /* Task List */
          <div>
            <h2 className="text-xl font-semibold mb-4">
              Your Tasks
              {searchQuery && (
                <span className="text-sm font-normal text-muted-foreground ml-2">
                  (filtered)
                </span>
              )}
            </h2>
            {filteredAndSortedTasks.length === 0 && (searchQuery || filterPriority !== "all" || filterStatus !== "all") ? (
              <div className="text-center py-12 bg-card border border-border rounded-lg">
                <svg
                  className="w-16 h-16 mx-auto mb-4 text-muted-foreground"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <p className="text-muted-foreground">
                  No tasks found with the current filters
                </p>
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setFilterPriority("all");
                    setFilterStatus("all");
                  }}
                  className="mt-4 text-sm text-primary hover:underline"
                >
                  Clear all filters
                </button>
              </div>
            ) : (
              <TaskList
                tasks={filteredAndSortedTasks}
                onToggleComplete={handleToggleComplete}
                onEdit={handleEdit}
                onDelete={handleDeleteClick}
              />
            )}
          </div>
        )}

        {/* Edit Dialog */}
        {taskToEdit && (
          <TaskEditDialog
            task={taskToEdit}
            isOpen={editDialogOpen}
            onClose={() => setEditDialogOpen(false)}
            onSave={handleSaveEdit}
          />
        )}

        {/* Delete Confirmation Dialog */}
        <TaskDeleteDialog
          task={taskToDelete}
          isOpen={deleteDialogOpen}
          onClose={() => setDeleteDialogOpen(false)}
          onConfirm={handleConfirmDelete}
        />
      </main>
    </div>
  );
}
