"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { cn } from "@/lib/utils";

interface HeatmapData {
  date: string;
  count: number;
}

export function StreakHeatmap() {
  const [data, setData] = useState<HeatmapData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use apiClient to fetch heatmap data
      const heatmapData = await apiClient.axiosInstance.get('/api/analytics/streak-heatmap?days=365').then(r => r.data);

      setData(heatmapData);
    } catch (error: any) {
      console.error("Failed to load heatmap data:", error);
      setError(error.response?.data?.detail || error.message || "Unable to load activity data");
    } finally {
      setLoading(false);
    }
  };

  // Generate 52 weeks (7 days each) grid
  const weeks = [];
  const today = new Date();
  for (let i = 51; i >= 0; i--) {
    const week = [];
    for (let j = 0; j < 7; j++) {
      const date = new Date(today);
      date.setDate(date.getDate() - (i * 7 + (6 - j)));
      const dateStr = date.toISOString().split('T')[0];
      const dayData = data.find(d => d.date === dateStr);
      week.push({
        date: dateStr,
        count: dayData?.count || 0,
        dayOfWeek: j
      });
    }
    weeks.push(week);
  }

  const getColor = (count: number) => {
    if (count === 0) return 'bg-gray-100 dark:bg-gray-800';
    if (count <= 2) return 'bg-green-200 dark:bg-green-900';
    if (count <= 4) return 'bg-green-400 dark:bg-green-700';
    if (count <= 6) return 'bg-green-600 dark:bg-green-500';
    return 'bg-green-800 dark:bg-green-300';
  };

  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // Get month labels for every ~4 weeks
  const monthLabels = [];
  for (let i = 0; i < 52; i += 4) {
    if (weeks[i] && weeks[i][6]) {
      const date = new Date(weeks[i][6].date);
      monthLabels.push({ index: i, name: months[date.getMonth()] });
    }
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg border border-border bg-card">
        <h3 className="text-sm font-medium mb-4">Task Completion Streak</h3>
        <p className="text-sm text-muted-foreground">{error}</p>
        <button
          onClick={loadData}
          className="mt-2 text-xs text-primary hover:underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 rounded-lg border border-border bg-card">
      <h3 className="text-sm font-medium mb-4">Task Completion Streak</h3>
      {loading ? (
        <div className="animate-pulse h-32 bg-muted rounded"></div>
      ) : (
        <div className="overflow-x-auto">
          <div className="flex gap-1 min-w-fit">
            {/* Day labels */}
            <div className="flex flex-col gap-1 text-xs text-muted-foreground pr-2">
              {days.map((day, i) => (
                <div key={day} className="h-3 flex items-center" style={{ height: '12px' }}>
                  {i % 2 === 0 ? day : ''}
                </div>
              ))}
            </div>

            {/* Heatmap grid */}
            <div className="flex gap-1">
              {weeks.map((week, weekIndex) => (
                <div key={weekIndex} className="flex flex-col gap-1">
                  {week.map((day) => (
                    <div
                      key={day.date}
                      title={`${day.date}: ${day.count} task${day.count !== 1 ? 's' : ''} completed`}
                      className={cn(
                        "w-3 h-3 rounded-sm cursor-pointer transition-colors",
                        getColor(day.count)
                      )}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-between mt-3 text-xs text-muted-foreground">
            <span>Less</span>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-sm bg-gray-100 dark:bg-gray-800"></div>
              <div className="w-3 h-3 rounded-sm bg-green-200 dark:bg-green-900"></div>
              <div className="w-3 h-3 rounded-sm bg-green-400 dark:bg-green-700"></div>
              <div className="w-3 h-3 rounded-sm bg-green-600 dark:bg-green-500"></div>
              <div className="w-3 h-3 rounded-sm bg-green-800 dark:bg-green-300"></div>
            </div>
            <span>More</span>
          </div>
        </div>
      )}
    </div>
  );
}
