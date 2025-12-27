"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart as PieChartIcon } from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { cn } from "@/lib/utils";

export interface MessageRoleStats {
  role: string;
  count: number;
  percentage: number;
}

export interface MessageDistributionProps {
  data: MessageRoleStats[];
  totalMessages: number;
  className?: string;
}

// Role display names and colors
const ROLE_CONFIG: Record<
  string,
  { label: string; color: string; lightColor: string }
> = {
  user: {
    label: "User Messages",
    color: "hsl(262, 83%, 58%)",
    lightColor: "hsl(262, 83%, 58%, 0.2)",
  },
  assistant: {
    label: "AI Responses",
    color: "hsl(139, 76%, 36%)",
    lightColor: "hsl(139, 76%, 36%, 0.2)",
  },
  system: {
    label: "System",
    color: "hsl(38, 92%, 50%)",
    lightColor: "hsl(38, 92%, 50%, 0.2)",
  },
  tool: {
    label: "Tool Calls",
    color: "hsl(221, 83%, 53%)",
    lightColor: "hsl(221, 83%, 53%, 0.2)",
  },
};

const DEFAULT_COLOR = "hsl(var(--muted))";

export function MessageDistribution({
  data,
  totalMessages,
  className,
}: MessageDistributionProps) {
  // Prepare data for chart with custom colors
  const chartData = data.map((item) => ({
    ...item,
    name: ROLE_CONFIG[item.role]?.label || item.role,
    color: ROLE_CONFIG[item.role]?.color || DEFAULT_COLOR,
  }));

  if (data.length === 0) {
    return (
      <Card className={cn("glass-card", className)}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <PieChartIcon className="h-4 w-4 text-primary" />
            Message Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
            No message data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("glass-card", className)}>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <PieChartIcon className="h-4 w-4 text-primary" />
          Message Distribution by Role
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={(entry) => `${((entry.payload?.percentage || 0)).toFixed(0)}%`}
              outerRadius={90}
              innerRadius={50}
              paddingAngle={2}
              dataKey="count"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              formatter={(value: number | undefined, name: string | undefined) => [
                `${value ?? 0} messages`,
                name ?? "",
              ]}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              formatter={(value) => (
                <span className="text-xs text-muted-foreground">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
        {totalMessages > 0 && (
          <div className="mt-2 text-center text-sm text-muted-foreground">
            Total messages: <span className="font-semibold text-foreground">{totalMessages}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Legend component for displaying role breakdown
export function MessageRoleLegend({
  data,
}: {
  data: MessageRoleStats[];
}) {
  if (data.length === 0) return null;

  return (
    <div className="space-y-2 mt-4">
      {data.map((item) => {
        const config = ROLE_CONFIG[item.role];
        return (
          <div
            key={item.role}
            className="flex items-center justify-between text-sm"
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: config?.color || DEFAULT_COLOR }}
              />
              <span className="text-muted-foreground">
                {config?.label || item.role}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-medium">{item.count}</span>
              <span className="text-muted-foreground">
                {item.percentage.toFixed(1)}%
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
