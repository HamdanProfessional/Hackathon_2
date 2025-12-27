"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Wrench } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { cn } from "@/lib/utils";

export interface ToolUsageStats {
  tool_name: string;
  call_count: number;
}

export interface ToolUsageChartProps {
  data: ToolUsageStats[];
  totalToolCalls: number;
  className?: string;
}

// Color palette for bars
const BAR_COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--chart-1, 139, 92, 246))",
  "hsl(var(--chart-2, 236, 72, 153))",
  "hsl(var(--chart-3, 34, 197, 94))",
  "hsl(var(--chart-4, 251, 146, 60))",
  "hsl(var(--chart-5, 14, 165, 233))",
];

export function ToolUsageChart({
  data,
  totalToolCalls,
  className,
}: ToolUsageChartProps) {
  // Format tool name for display
  const formatToolName = (name: string) => {
    // Remove common prefixes and format
    return name
      .replace(/^(get_|create_|update_|delete_)/, "")
      .replace(/_/g, " ")
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  if (data.length === 0) {
    return (
      <Card className={cn("glass-card", className)}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Wrench className="h-4 w-4 text-primary" />
            Tool Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
            No tool usage data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("glass-card", className)}>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Wrench className="h-4 w-4 text-primary" />
          Tool Usage Frequency
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              className="stroke-muted"
              horizontal={true}
              vertical={false}
            />
            <XAxis
              type="number"
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
              axisLine={{ stroke: "hsl(var(--border))" }}
            />
            <YAxis
              type="category"
              dataKey="tool_name"
              tickFormatter={formatToolName}
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
              axisLine={{ stroke: "hsl(var(--border))" }}
              width={120}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelFormatter={(label) => formatToolName(label)}
              formatter={(value: number | undefined, name: string | undefined) => [
                value ?? 0,
                "Calls",
              ]}
            />
            <Bar dataKey="call_count" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={BAR_COLORS[index % BAR_COLORS.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        {totalToolCalls > 0 && (
          <div className="mt-4 text-center text-sm text-muted-foreground">
            Total tool calls: <span className="font-semibold text-foreground">{totalToolCalls}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
