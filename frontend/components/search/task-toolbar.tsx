"use client";

import { Search, Filter, ArrowUpDown, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useSearchParams, useRouter, usePathname } from "next/navigation";

interface TaskToolbarProps {
  className?: string;
}

export function TaskToolbar({ className }: TaskToolbarProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Get current filter values
  const currentStatus = searchParams.get("status") || "all";
  const currentPriority = searchParams.get("priority") || "all";
  const currentSortBy = searchParams.get("sort_by") || "created_at";
  const currentSortOrder = searchParams.get("sort_order") || "desc";

  // Check if any filters are active
  const hasActiveFilters = searchParams.get("search") ||
                         currentStatus !== "all" ||
                         currentPriority !== "all";

  // Update URL with new filter value
  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());

    if (value && value !== "all") {
      params.set(key, value);
    } else {
      params.delete(key);
    }

    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl);
  };

  // Clear all filters
  const clearFilters = () => {
    router.replace(pathname);
  };

  return (
    <div className={cn("flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-2", className)}>
      {/* Search bar will be handled separately */}

      <div className="flex flex-1 gap-2">
        {/* Status Filter */}
        <Select value={currentStatus} onValueChange={(value) => updateFilter("status", value)}>
          <SelectTrigger className="w-full sm:w-[140px] bg-zinc-900/50 border-zinc-800 text-white">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>

        {/* Priority Filter */}
        <Select value={currentPriority} onValueChange={(value) => updateFilter("priority", value)}>
          <SelectTrigger className="w-full sm:w-[140px] bg-zinc-900/50 border-zinc-800 text-white">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">All Priority</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>

        {/* Sort By */}
        <Select value={`${currentSortBy}-${currentSortOrder}`} onValueChange={(value) => {
          const [sortBy, sortOrder] = value.split("-");
          updateFilter("sort_by", sortBy);
          updateFilter("sort_order", sortOrder);
        }}>
          <SelectTrigger className="w-full sm:w-[140px] bg-zinc-900/50 border-zinc-800 text-white">
            <ArrowUpDown className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Sort" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="created_at-desc">Newest First</SelectItem>
            <SelectItem value="created_at-asc">Oldest First</SelectItem>
            <SelectItem value="due_date-asc">Due Date (Earliest)</SelectItem>
            <SelectItem value="due_date-desc">Due Date (Latest)</SelectItem>
            <SelectItem value="priority-asc">Priority (Low to High)</SelectItem>
            <SelectItem value="priority-desc">Priority (High to Low)</SelectItem>
            <SelectItem value="title-asc">Title (A-Z)</SelectItem>
            <SelectItem value="title-desc">Title (Z-A)</SelectItem>
          </SelectContent>
        </Select>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <Button
            variant="outline"
            size="sm"
            onClick={clearFilters}
            className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white"
          >
            <X className="mr-2 h-4 w-4" />
            Clear
          </Button>
        )}
      </div>
    </div>
  );
}