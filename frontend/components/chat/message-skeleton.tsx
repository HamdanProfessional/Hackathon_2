import { cn } from "@/lib/utils"

interface MessageSkeletonProps {
  type: "user" | "assistant"
  className?: string
}

export function MessageSkeleton({ type, className }: MessageSkeletonProps) {
  return (
    <div className={cn(
      "flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300",
      type === "user" ? "justify-end" : "justify-start",
      className
    )}>
      {type === "assistant" && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0 mt-1">
          AI
        </div>
      )}

      <div className={cn(
        "flex flex-col gap-2 max-w-[75%]",
        type === "user" && "items-end"
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3 shadow-lg",
          type === "user"
            ? "bg-gradient-to-br from-blue-600 to-blue-500"
            : "bg-slate-800/80 backdrop-blur-sm border border-white/10"
        )}>
          <div className="space-y-2">
            {/* Title line skeleton */}
            <div className={cn(
              "h-4 rounded animate-pulse",
              type === "user" ? "bg-blue-400/30 w-20" : "bg-slate-600/50 w-16"
            )} />

            {/* Content lines skeleton */}
            <div className="space-y-1.5">
              <div className={cn(
                "h-3 rounded-full animate-pulse",
                type === "user" ? "bg-blue-400/20 w-full" : "bg-slate-600/30 w-full"
              )} />
              <div className={cn(
                "h-3 rounded-full animate-pulse",
                type === "user" ? "bg-blue-400/20 w-4/5" : "bg-slate-600/30 w-4/5"
              )} />
              <div className={cn(
                "h-3 rounded-full animate-pulse",
                type === "user" ? "bg-blue-400/20 w-3/5" : "bg-slate-600/30 w-2/3"
              )} />
            </div>
          </div>
        </div>

        {/* Metadata skeleton */}
        <div className="flex items-center gap-2 px-2 opacity-60">
          <div className="h-3 w-12 bg-slate-600/30 rounded animate-pulse" />
          <div className="h-3 w-3 bg-slate-600/30 rounded-full animate-pulse" />
        </div>
      </div>

      {type === "user" && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0 mt-1">
          U
        </div>
      )}
    </div>
  )
}