"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { apiClient, type Task } from "@/lib/api";
import { toast } from "sonner";
import { useAuthGuard } from "@/hooks/use-auth-guard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import TaskCard from "@/components/task/task-card";
import TaskForm from "@/components/task/task-form";
import { SearchBar } from "@/components/search/search-bar";
import { TaskToolbar } from "@/components/search/task-toolbar";
import QuickAdd from "@/components/task/quick-add";
import { Plus, CheckCircle2, Circle, ListTodo, Download, ClipboardList, LayoutGrid, List, ChevronDown, Timer } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { SettingsModal } from "@/components/settings/settings-modal";
import ChatWidget from "@/components/chat/chat-widget";
import LanguageSwitcher from "@/components/language-switcher";
import { StreakHeatmap } from "@/components/analytics/streak-heatmap";
import { ProductivityDashboard } from "@/components/analytics/productivity-dashboard";
import { PomodoroTimer } from "@/components/productivity/pomodoro-timer";

export default function DashboardPage() {
  console.log("Dashboard Rendered");

  const router = useRouter();
  const searchParams = useSearchParams();

  // Apply authentication guard
  useAuthGuard();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [submittingTask, setSubmittingTask] = useState(false);
  const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null);
  const [showPomodoro, setShowPomodoro] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(() => {
    // Initialize from localStorage first, then sync with backend
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('viewMode');
      return (stored === 'grid' || stored === 'list') ? stored : 'grid';
    }
    return 'grid';
  });

  // Extract primitive values from searchParams to prevent infinite loops
  const searchQuery = searchParams.get("search");
  const statusFilter = searchParams.get("status");
  const priorityFilter = searchParams.get("priority");
  const sortBy = searchParams.get("sort_by") || "created_at";
  const sortOrder = searchParams.get("sort_order") || "desc";

  // Build API parameters from primitive values
  const apiParams = useMemo(() => {
    const params: Record<string, string> = {};

    if (searchQuery) params.search = searchQuery;
    if (statusFilter && statusFilter !== "all") params.status = statusFilter;
    if (priorityFilter && priorityFilter !== "all") params.priority = priorityFilter;

    params.sort_by = sortBy;
    params.sort_order = sortOrder;

    return params;
  }, [searchQuery, statusFilter, priorityFilter, sortBy, sortOrder]);

  // Load user data on mount (after auth guard has validated token)
  useEffect(() => {
    const loadUserData = async () => {
      // Get user from token
      const currentUser = apiClient.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);

        // Load user preferences including viewMode
        try {
          const prefs = await apiClient.getUserPreferences();
          if (prefs?.preferences?.viewMode) {
            setViewMode(prefs.preferences.viewMode);
            // Sync to localStorage
            if (typeof window !== 'undefined') {
              localStorage.setItem('viewMode', prefs.preferences.viewMode);
            }
          }
        } catch (error) {
          console.error("Failed to load preferences:", error);
        }
      }
    };

    loadUserData();
  }, []);

  // Listen for localStorage changes (sync across tabs/settings modal)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'viewMode' && e.newValue) {
        const newMode = e.newValue === 'grid' || e.newValue === 'list' ? e.newValue : 'grid';
        setViewMode(newMode);
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('storage', handleStorageChange);
      return () => window.removeEventListener('storage', handleStorageChange);
    }
  }, []);

  // Memoized loadTasks function to prevent infinite loops
  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedTasks = await apiClient.getTasks(apiParams);
      setTasks(fetchedTasks);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Failed to load tasks";
      setError(errorMessage);
      toast.error(errorMessage);

      // If unauthorized, the API client will handle redirect
      // No need to manually redirect here
    } finally {
      setLoading(false);
    }
  }, [apiParams]);

  // Load tasks when API parameters or user changes
  useEffect(() => {
    if (user) {
      loadTasks();
    }
  }, [user, loadTasks]);

  const handleLogout = () => {
    apiClient.logout();
    toast.info("Logged out successfully");
  };

  // Handle view mode change
  const handleViewModeChange = async (newViewMode: 'grid' | 'list') => {
    setViewMode(newViewMode);
    // Sync to localStorage immediately for responsive UI
    if (typeof window !== 'undefined') {
      localStorage.setItem('viewMode', newViewMode);
    }
    // Also update in user preferences
    try {
      const prefs = await apiClient.getUserPreferences();
      const updatedPrefs = { ...(prefs?.preferences || {}), viewMode: newViewMode };
      await apiClient.updateUserPreferences(updatedPrefs);
    } catch (error) {
      console.error("Failed to update view mode preference:", error);
    }
  };

  // Handle export to JSON
  const handleExportToJSON = () => {
    const exportData = {
      user: {
        email: user?.email,
        id: user?.id,
        created_at: user?.created_at
      },
      tasks: tasks.map(task => ({
        id: task.id,
        title: task.title,
        description: task.description,
        priority: task.priority,
        completed: task.completed,
        due_date: task.due_date,
        created_at: task.created_at,
        updated_at: task.updated_at
      })),
      exported_at: new Date().toISOString(),
      filters: {
        search: searchQuery,
        status: statusFilter,
        priority: priorityFilter,
        sort_by: sortBy,
        sort_order: sortOrder
      },
      statistics: {
        total: totalTasks,
        completed: completedTasks,
        active: activeTasks
      }
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

    const exportFileDefaultName = `tasks-${new Date().toISOString().split('T')[0]}.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.style.visibility = "hidden";
    document.body.appendChild(linkElement);
    linkElement.click();
    document.body.removeChild(linkElement);

    toast.success("Tasks exported successfully!");
  };

  // Handle task creation
  const handleCreateTask = async (data: {
    title: string;
    description?: string;
    priority: "low" | "medium" | "high";
    due_date?: string;
    is_recurring?: boolean;
    recurrence_pattern?: "daily" | "weekly" | "monthly" | "yearly";
  }) => {
    setSubmittingTask(true);
    try {
      const newTask = await apiClient.createTask(data);
      setTasks([newTask, ...tasks]);
      toast.success("Task created successfully!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to create task");
      throw err; // Re-throw to prevent form from closing
    } finally {
      setSubmittingTask(false);
    }
  };

  // Handle task editing
  const handleEditTask = async (data: {
    title: string;
    description?: string;
    priority: "low" | "medium" | "high";
    due_date?: string;
    is_recurring?: boolean;
    recurrence_pattern?: "daily" | "weekly" | "monthly" | "yearly";
  }) => {
    if (!editingTask) return;

    setSubmittingTask(true);
    try {
      const updatedTask = await apiClient.updateTask(editingTask.id, data);
      setTasks(tasks.map((t) => (t.id === editingTask.id ? updatedTask : t)));
      toast.success("Task updated successfully!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to update task");
      throw err;
    } finally {
      setSubmittingTask(false);
    }
  };

  // Handle task completion toggle with optimistic UI
  const handleToggleComplete = async (taskId: number) => {
    // Optimistic update
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    const originalCompleted = task.completed;
    setTasks(
      tasks.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      )
    );

    try {
      const updatedTask = await apiClient.toggleTaskCompletion(taskId);
      // Ensure the API response matches our optimistic update
      setTasks(
        tasks.map((t) =>
          t.id === taskId ? updatedTask : t
        )
      );
    } catch (err: any) {
      // Revert on error
      setTasks(
        tasks.map((t) =>
          t.id === taskId ? { ...t, completed: originalCompleted } : t
        )
      );
      toast.error(err.response?.data?.detail || "Failed to update task");
    }
  };

  // Handle task deletion with confirmation
  const handleDeleteTask = async (task: Task) => {
    setDeletingTaskId(task.id);
    try {
      // Optimistic update
      setTasks(tasks.filter((t) => t.id !== task.id));
      await apiClient.deleteTask(task.id);
      toast.success("Task deleted successfully!");
    } catch (err: any) {
      // Revert on error
      setTasks((prev) => [...prev, task]);
      toast.error(err.response?.data?.detail || "Failed to delete task");
    } finally {
      setDeletingTaskId(null);
    }
  };

  // Get task statistics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.completed).length;
  const activeTasks = totalTasks - completedTasks;

  // Get active filters count for display
  const activeFiltersCount = [
    searchQuery,
    statusFilter === "all" ? null : statusFilter,
    priorityFilter === "all" ? null : priorityFilter,
  ].filter(Boolean).length;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold gradient-text">Dashboard</h1>
            <div className="flex items-center gap-2 mt-1">
              <svg className="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <p className="text-sm text-muted-foreground">
                {user?.email || "Loading..."}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <LanguageSwitcher />
            <SettingsModal />
            <Button
              onClick={() => {
                setEditingTask(null);
                setIsFormOpen(true);
              }}
              className="gradient-bg"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create New Task
            </Button>
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error State */}
        {error && (
          <Card className="mb-6 border-destructive/50">
            <CardContent className="pt-6">
              <p className="text-destructive">{error}</p>
              <Button onClick={loadTasks} className="mt-4" variant="outline">
                Try Again
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {loading && !error && (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading your tasks...</p>
          </div>
        )}

        {/* Tasks List */}
        {!loading && !error && (
          <div className="space-y-8">
            {/* Quick Add Bar */}
            <Card className="glass-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Quick Add Task</CardTitle>
                <CardDescription className="text-xs">
                  Use natural language: "Call mom tomorrow urgent" or "Meeting every Friday"
                </CardDescription>
              </CardHeader>
              <CardContent>
                <QuickAdd onTaskCreated={loadTasks} />
              </CardContent>
            </Card>

            {/* Search and Filter Controls */}
            <div className="space-y-4">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex-1 max-w-md">
                  <SearchBar placeholder="Search tasks by title or description..." />
                </div>
              </div>
              <TaskToolbar viewMode={viewMode} onViewModeChange={handleViewModeChange} />
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="glass-card">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <ListTodo className="h-5 w-5 text-primary" />
                    <CardTitle className="text-2xl font-bold">{totalTasks}</CardTitle>
                  </div>
                  <CardDescription>Total Tasks</CardDescription>
                </CardHeader>
              </Card>
              <Card className="glass-card">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Circle className="h-5 w-5 text-amber-500" />
                    <CardTitle className="text-2xl font-bold text-amber-500">
                      {activeTasks}
                    </CardTitle>
                  </div>
                  <CardDescription>Active Tasks</CardDescription>
                </CardHeader>
              </Card>
              <Card className="glass-card">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    <CardTitle className="text-2xl font-bold text-green-500">
                      {completedTasks}
                    </CardTitle>
                  </div>
                  <CardDescription>Completed</CardDescription>
                </CardHeader>
              </Card>
            </div>

            {/* Streak Heatmap */}
            <StreakHeatmap />

            {/* Productivity Analytics Dashboard */}
            <ProductivityDashboard />

            {/* Pomodoro Timer Section */}
            <Card className="glass-card">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Timer className="h-5 w-5 text-primary" />
                    <CardTitle>Pomodoro Timer</CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowPomodoro(!showPomodoro)}
                    className="flex items-center gap-2"
                  >
                    {showPomodoro ? 'Hide' : 'Show'}
                    <ChevronDown className={`h-4 w-4 transition-transform ${showPomodoro ? 'rotate-180' : ''}`} />
                  </Button>
                </div>
              </CardHeader>
              {showPomodoro && (
                <CardContent>
                  <div className="flex justify-center">
                    <PomodoroTimer />
                  </div>
                </CardContent>
              )}
            </Card>

            {/* Tasks List */}
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <span>Your Tasks</span>
                <span className="text-sm font-normal text-muted-foreground">
                  ({totalTasks} total{activeFiltersCount > 0 && `, ${activeFiltersCount} filter${activeFiltersCount > 1 ? "s" : ""} active`})
                </span>
              </h2>

              {/* Empty State */}
              {tasks.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5 }}
                  className="flex flex-col items-center justify-center py-12 text-center"
                >
                  <div className="bg-zinc-900/50 p-6 rounded-full mb-4 ring-1 ring-white/10">
                    <ClipboardList className="w-12 h-12 text-zinc-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {searchQuery ||
                     statusFilter ||
                     priorityFilter
                      ? "No tasks match your filters"
                      : "All caught up!"}
                  </h3>
                  <p className="text-zinc-400 max-w-sm mb-6">
                    {searchQuery ||
                     statusFilter ||
                     priorityFilter
                      ? "Try adjusting your filters or create a new task"
                      : "You have no pending tasks. Enjoy your free time or add a new task to get started."}
                  </p>
                  <Button
                    onClick={() => {
                      setEditingTask(null);
                      setIsFormOpen(true);
                    }}
                    className="gradient-bg"
                  >
                      <Plus className="w-4 h-4 mr-2" />
                      {searchQuery ||
                       statusFilter ||
                       priorityFilter
                        ? "Create a New Task"
                        : "Create Your First Task"}
                    </Button>
                </motion.div>
              ) : (
                <AnimatePresence>
                  <motion.div
                    layout
                    className={viewMode === 'grid'
                      ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
                      : "flex flex-col gap-3"
                    }
                  >
                    {tasks.map((task) => (
                      <motion.div
                        key={task.id}
                        layout
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{
                          duration: 0.2,
                        }}
                      >
                        <TaskCard
                          task={task}
                          viewMode={viewMode}
                          isCompleting={deletingTaskId === task.id}
                          onEdit={(task) => {
                            setEditingTask(task);
                            setIsFormOpen(true);
                          }}
                          onDelete={(task) => {
                            // Use AlertDialog for confirmation
                            setDeletingTaskId(task.id);
                            handleDeleteTask(task);
                          }}
                          onToggleComplete={handleToggleComplete}
                        />
                      </motion.div>
                    ))}
                  </motion.div>
                </AnimatePresence>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Task Form Modal */}
      <TaskForm
        task={editingTask}
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={editingTask ? handleEditTask : handleCreateTask}
        isSubmitting={submittingTask}
      />

      {/* Floating AI Chat Widget */}
      <ChatWidget />
    </div>
  );
}