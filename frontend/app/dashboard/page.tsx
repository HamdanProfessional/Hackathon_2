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

  const completedCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length;

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
            <h2 className="text-xl font-semibold mb-4">Your Tasks</h2>
            <TaskList
              tasks={tasks}
              onToggleComplete={handleToggleComplete}
              onEdit={handleEdit}
              onDelete={handleDeleteClick}
            />
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
