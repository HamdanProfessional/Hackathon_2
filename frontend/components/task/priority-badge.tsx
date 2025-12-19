"use client";

import { cn } from "@/lib/utils";
import { AlertTriangle, CheckCircle, Circle } from "lucide-react";

interface PriorityBadgeProps {
  priority: "LOW" | "MEDIUM" | "HIGH";
  className?: string;
  variant?: "default" | "compact" | "large";
}

const priorityConfig = {
  HIGH: {
    label: "High",
    color: "red",
    bgColor: "bg-red-500/10",
    textColor: "text-red-500",
    borderColor: "border-red-500/20",
    icon: AlertTriangle,
  },
  MEDIUM: {
    label: "Medium",
    color: "amber",
    bgColor: "bg-amber-500/10",
    textColor: "text-amber-500",
    borderColor: "border-amber-500/20",
    icon: Circle,
  },
  LOW: {
    label: "Low",
    color: "zinc",
    bgColor: "bg-zinc-500/10",
    textColor: "text-zinc-500",
    borderColor: "border-zinc-500/20",
    icon: CheckCircle,
  },
};

export default function PriorityBadge({
  priority,
  className,
  variant = "default",
}: PriorityBadgeProps) {
  const config = priorityConfig[priority];
  const Icon = config.icon;

  const sizes = {
    compact: "px-2 py-1 text-xs gap-1",
    default: "px-3 py-1.5 text-sm gap-1.5",
    large: "px-4 py-2 text-base gap-2",
  };

  const iconSizes = {
    compact: "h-3 w-3",
    default: "h-3.5 w-3.5",
    large: "h-4 w-4",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border font-medium transition-all duration-200",
        config.bgColor,
        config.textColor,
        config.borderColor,
        sizes[variant],
        "hover:opacity-80",
        className
      )}
    >
      <Icon className={cn(iconSizes[variant], "shrink-0")} />
      <span className="capitalize">{config.label}</span>
    </div>
  );
}