"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Clock, Target, Award, Zap } from "lucide-react";
import { apiClient } from "@/lib/api";

interface AnalyticsData {
  period_days: number;
  total_completed: number;
  completion_rate: number;
  priority_breakdown: Record<string, number>;
  daily_completion: Array<{date: string, count: number}>;
}

interface FocusHoursData {
  period_days: number;
  completed_tasks: number;
  focus_minutes: number;
  focus_hours: number;
}

export function ProductivityDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [focusData, setFocusData] = useState<FocusHoursData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use apiClient to fetch analytics
      const [analyticsJson, focusJson] = await Promise.all([
        apiClient.axiosInstance.get('/api/analytics/productivity?days=30').then(r => r.data),
        apiClient.axiosInstance.get('/api/analytics/focus-hours?days=30').then(r => r.data)
      ]);

      setAnalytics(analyticsJson);
      setFocusData(focusJson);
    } catch (err: any) {
      console.error("Failed to load analytics:", err);
      setError(err.response?.data?.detail || err.message || "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="glass-card">
            <CardContent className="pt-6">
              <div className="animate-pulse h-20 bg-muted/50 rounded-lg" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="glass-card border-destructive/50">
        <CardContent className="pt-6">
          <p className="text-destructive">Failed to load analytics: {error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!analytics || !focusData) return null;

  // Calculate derived metrics
  const dailyAverage = (analytics.total_completed / analytics.period_days).toFixed(1);
  const priorityLabels: Record<string, string> = {
    "1": "Low",
    "2": "Medium",
    "3": "High",
    "none": "Unset"
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Completed */}
        <Card className="glass-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              Completed (30d)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.total_completed}</div>
            <p className="text-xs text-muted-foreground mt-1">tasks finished</p>
          </CardContent>
        </Card>

        {/* Success Rate */}
        <Card className="glass-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Award className="h-4 w-4 text-amber-500" />
              Success Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.completion_rate}%</div>
            <p className="text-xs text-muted-foreground mt-1">task completion</p>
          </CardContent>
        </Card>

        {/* Daily Average */}
        <Card className="glass-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              Daily Average
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dailyAverage}</div>
            <p className="text-xs text-muted-foreground mt-1">tasks per day</p>
          </CardContent>
        </Card>

        {/* Focus Time */}
        <Card className="glass-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Clock className="h-4 w-4 text-blue-500" />
              Focus Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{focusData.focus_hours}h</div>
            <p className="text-xs text-muted-foreground mt-1">
              {focusData.focus_minutes} minutes focused
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Completion Chart */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" />
              Daily Completion (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics.daily_completion.length > 0 ? (
              <div className="flex items-end gap-1 h-32 w-full">
                {analytics.daily_completion.slice(-30).map((day, i) => {
                  const maxCount = Math.max(...analytics.daily_completion.map(d => d.count), 1);
                  const height = (day.count / maxCount) * 100;
                  return (
                    <div
                      key={i}
                      className="flex-1 bg-primary/60 hover:bg-primary rounded-t transition-colors relative group min-w-[8px]"
                      style={{ height: `${height}%`, minHeight: height > 0 ? '4px' : '2px' }}
                      title={`${day.date}: ${day.count} tasks`}
                    >
                      <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity bg-popover px-1.5 py-0.5 rounded shadow-md whitespace-nowrap">
                        {day.count}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
                No completion data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Priority Breakdown */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              Priority Breakdown (30d)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {Object.keys(analytics.priority_breakdown).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(analytics.priority_breakdown)
                  .sort((a, b) => parseInt(b[0]) - parseInt(a[0]))
                  .map(([priority, count]) => {
                    const maxCount = Math.max(...Object.values(analytics.priority_breakdown));
                    const width = (count / maxCount) * 100;
                    const colors: Record<string, string> = {
                      "3": "bg-red-500",
                      "2": "bg-amber-500",
                      "1": "bg-green-500",
                      "none": "bg-gray-400"
                    };
                    return (
                      <div key={priority} className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium">
                            {priorityLabels[priority] || priority}
                          </span>
                          <span className="text-muted-foreground">{count} tasks</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${colors[priority] || 'bg-primary'} rounded-full transition-all duration-500`}
                            style={{ width: `${width}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
                No priority data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
