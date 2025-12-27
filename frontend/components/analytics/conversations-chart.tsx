"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { cn } from "@/lib/utils";

export interface TimelineDataPoint {
  date: string;
  count: number;
}

export interface ConversationsChartProps {
  data: TimelineDataPoint[];
  period: "daily" | "weekly" | "monthly";
  className?: string;
}

export function ConversationsChart({
  data,
  period,
  className,
}: ConversationsChartProps) {
  // Format date based on period
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    switch (period) {
      case "daily":
        return date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        });
      case "weekly":
        return dateStr; // Already formatted as "2025-W03"
      case "monthly":
        return date.toLocaleDateString("en-US", { month: "short" });
      default:
        return dateStr;
    }
  };

  // Calculate average line
  const avgCount =
    data.length > 0
      ? Math.round(data.reduce((sum, d) => sum + d.count, 0) / data.length)
      : 0;

  if (data.length === 0) {
    return (
      <Card className={cn("glass-card", className)}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-primary" />
            Conversations Over Time
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
            No conversation data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("glass-card", className)}>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-primary" />
          Conversations Timeline ({period})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart
            data={data}
            margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              className="stroke-muted"
              vertical={false}
            />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
              axisLine={{ stroke: "hsl(var(--border))" }}
            />
            <YAxis
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
              axisLine={{ stroke: "hsl(var(--border))" }}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelFormatter={(label) => formatDate(label)}
              formatter={(value: number | undefined) => [value ?? 0, "Conversations"]}
            />
            {avgCount > 0 && (
              <ReferenceLine
                y={avgCount}
                stroke="hsl(var(--muted-foreground))"
                strokeDasharray="3 3"
                label={{
                  value: `Avg: ${avgCount}`,
                  position: "insideTopRight",
                  fill: "hsl(var(--muted-foreground))",
                  fontSize: 12,
                }}
              />
            )}
            <Line
              type="monotone"
              dataKey="count"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={{ fill: "hsl(var(--primary))", r: 4 }}
              activeDot={{ r: 6, fill: "hsl(var(--primary))" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
