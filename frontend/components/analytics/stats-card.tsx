"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    period: string;
  };
  color?: "primary" | "success" | "warning" | "destructive" | "default";
  description?: string;
}

const colorVariants = {
  primary: "text-primary",
  success: "text-green-500",
  warning: "text-amber-500",
  destructive: "text-destructive",
  default: "text-muted-foreground",
};

export function StatsCard({
  title,
  value,
  icon: Icon,
  trend,
  color = "default",
  description,
}: StatsCardProps) {
  const colorClass = colorVariants[color];

  return (
    <Card className="glass-card hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Icon className={cn("h-4 w-4", colorClass)} />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
        {trend && (
          <div className="flex items-center gap-1 mt-2">
            {trend.value > 0 ? (
              <TrendingUp className="h-3 w-3 text-green-500" />
            ) : (
              <TrendingDown className="h-3 w-3 text-destructive" />
            )}
            <span
              className={cn(
                "text-xs font-medium",
                trend.value > 0 ? "text-green-500" : "text-destructive"
              )}
            >
              {trend.value > 0 ? "+" : ""}
              {trend.value}%
            </span>
            <span className="text-xs text-muted-foreground">
              vs last {trend.period}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
