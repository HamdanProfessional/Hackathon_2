"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { apiClient, type Task } from "@/lib/api";
import { toast } from "sonner";
import { useAuthGuard } from "@/hooks/use-auth-guard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import TaskCard from "@/components/task/task-card";
import TaskForm from "@/components/task/task-form";
import { SearchBar } from "@/components/search/search-bar";
import { TaskToolbar } from "@/components/search/task-toolbar";
import QuickAdd from "@/components/task/quick-add";
import { Plus, CheckCircle2, Circle, ListTodo, ClipboardList, Timer } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { SettingsModal } from "@/components/settings/settings-modal";
import ChatWidget from "@/components/chat/chat-widget";
import LanguageSwitcher from "@/components/language-switcher";
import { StreakHeatmap } from "@/components/analytics/streak-heatmap";
import { ProductivityDashboard } from "@/components/analytics/productivity-dashboard";
import { PomodoroTimer } from "@/components/productivity/pomodoro-timer";

type TabValue = "tasks" | "analytics" | "pomodoro";

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
  const [activeTab, setActiveTab] = useState<TabValue>("tasks");
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(() => {
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

  // Load user data on mount
  useEffect(() => {
    const loadUserData = async () => {
      const currentUser = apiClient.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
        try {
          const prefs = await apiClient.getUserPreferences();
          if (prefs?.preferences?.viewMode) {
            setViewMode(prefs.preferences.viewMode);
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

  // Listen for localStorage changes
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

  // Memoized loadTasks function
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

  const handleViewModeChange = async (newViewMode: 'grid' | 'list') => {
    setViewMode(newViewMode);
    if (typeof window !== 'undefined') {
      localStorage.setItem('viewMode', newViewMode);
    }
    try {
      const prefs = await apiClient.getUserPreferences();
      const updatedPrefs = { ...(prefs?.preferences || {}), viewMode: newViewMode };
      await apiClient.updateUserPreferences(updatedPrefs);
    } catch (error) {
      console.error("Failed to update view mode preference:", error);
    }
  };

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
      throw err;
    } finally {
      setSubmittingTask(false);
    }
  };

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

  const handleToggleComplete = async (taskId: number) => {
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
      setTasks(
        tasks.map((t) =>
          t.id === taskId ? updatedTask : t
        )
      );
    } catch (err: any) {
      setTasks(
        tasks.map((t) =>
          t.id === taskId ? { ...t, completed: originalCompleted } : t
        )
      );
      toast.error(err.response?.data?.detail || "Failed to update task");
    }
  };

  const handleDeleteTask = async (task: Task) => {
    setDeletingTaskId(task.id);
    try {
      setTasks(tasks.filter((t) => t.id !== task.id));
      await apiClient.deleteTask(task.id);
      toast.success("Task deleted successfully!");
    } catch (err: any) {
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
          <div className="flex items-center gap-3">
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
              New Task
            </Button>
            <Button variant="ghost" onClick={handleLogout} size="sm">
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
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

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabValue)} className="space-y-6">
          {/* Stats Summary Cards - Always Visible */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="glass-card">
              <CardHeader className="pb-2 px-4 pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ListTodo className="h-4 w-4 text-primary" />
                    <span className="text-sm text-muted-foreground">Total</span>
                  </div>
                  <CardTitle className="text-2xl font-bold">{totalTasks}</CardTitle>
                </div>
              </CardHeader>
            </Card>
            <Card className="glass-card">
              <CardHeader className="pb-2 px-4 pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Circle className="h-4 w-4 text-amber-500" />
                    <span className="text-sm text-muted-foreground">Active</span>
                  </div>
                  <CardTitle className="text-2xl font-bold text-amber-500">
                    {activeTasks}
                  </CardTitle>
                </div>
              </CardHeader>
            </Card>
            <Card className="glass-card">
              <CardHeader className="pb-2 px-4 pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-muted-foreground">Done</span>
                  </div>
                  <CardTitle className="text-2xl font-bold text-green-500">
                    {completedTasks}
                  </CardTitle>
                </div>
              </CardHeader>
            </Card>
          </div>

          {/* Tabs Navigation */}
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="tasks" className="flex items-center gap-2">
              <ListTodo className="h-4 w-4" />
              Tasks
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <Timer className="h-4 w-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="pomodoro" className="flex items-center gap-2">
              <Timer className="h-4 w-4" />
              Focus
            </TabsTrigger>
          </TabsList>

          {/* Tasks Tab */}
          <TabsContent value="tasks" className="space-y-6 mt-6">
            {/* Quick Add */}
            <Card className="glass-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Quick Add</CardTitle>
                <CardDescription className="text-xs">
                  "Call mom tomorrow urgent" or "Meeting every Friday"
                </CardDescription>
              </CardHeader>
              <CardContent>
                <QuickAdd onTaskCreated={loadTasks} />
              </CardContent>
            </Card>

            {/* Search and Filters */}
            <div className="space-y-4">
              <SearchBar placeholder="Search tasks..." />
              <TaskToolbar viewMode={viewMode} onViewModeChange={handleViewModeChange} />
            </div>

            {/* Tasks List */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <span>Your Tasks</span>
                <span className="text-sm font-normal text-muted-foreground">
                  ({totalTasks}{activeFiltersCount > 0 && `, ${activeFiltersCount} filter${activeFiltersCount > 1 ? "s" : ""} active`})
                </span>
              </h2>

              {loading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                </div>
              ) : tasks.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                  className="flex flex-col items-center justify-center py-12 text-center"
                >
                  <div className="bg-zinc-900/50 p-4 rounded-full mb-4 ring-1 ring-white/10">
                    <ClipboardList className="w-10 h-10 text-zinc-500" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">
                    {searchQuery || statusFilter || priorityFilter
                      ? "No tasks match your filters"
                      : "All caught up!"}
                  </h3>
                  <p className="text-sm text-muted-foreground max-w-sm mb-4">
                    {searchQuery || statusFilter || priorityFilter
                      ? "Try adjusting your filters"
                      : "Create a new task to get started"}
                  </p>
                </motion.div>
              ) : (
                <AnimatePresence>
                  <motion.div
                    layout
                    className={viewMode === 'grid'
                      ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                      : "flex flex-col gap-3"
                    }
                  >
                    {tasks.map((task) => (
                      <motion.div
                        key={task.id}
                        layout
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{ duration: 0.15 }}
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
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6 mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Streak Heatmap */}
              <Card className="glass-card lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-base">Activity Streak</CardTitle>
                  <CardDescription className="text-xs">Your task completion over the past year</CardDescription>
                </CardHeader>
                <CardContent>
                  <StreakHeatmap />
                </CardContent>
              </Card>

              {/* Productivity Dashboard */}
              <Card className="glass-card lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-base">Productivity Insights</CardTitle>
                  <CardDescription className="text-xs">30-day performance metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <ProductivityDashboard />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Pomodoro Tab */}
          <TabsContent value="pomodoro" className="mt-6">
            <Card className="glass-card max-w-md mx-auto">
              <CardHeader>
                <CardTitle className="text-center">Pomodoro Timer</CardTitle>
                <CardDescription className="text-center text-xs">
                  Focus for 25 minutes, then take a 5-minute break
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <PomodoroTimer />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
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
