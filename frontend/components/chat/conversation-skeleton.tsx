import { cn } from "@/lib/utils"
import { MessageSquare } from "lucide-react"

interface ConversationSkeletonProps {
  className?: string
  count?: number
}

export function ConversationSkeleton({ className, count = 3 }: ConversationSkeletonProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {[...Array(count)].map((_, i) => (
        <div
          key={i}
          className="px-3 py-3 rounded-lg bg-slate-800/50 border border-white/5 animate-pulse"
          style={{ animationDelay: `${i * 0.1}s` }}
        >
          <div className="space-y-2">
            {/* Preview text skeleton */}
            <div className="h-4 bg-slate-600/40 rounded w-3/4 animate-pulse" />
            <div className="h-3 bg-slate-600/30 rounded w-1/2 animate-pulse" />

            {/* Timestamp skeleton */}
            <div className="flex items-center gap-2 pt-1">
              <div className="h-2 w-16 bg-slate-600/20 rounded animate-pulse" />
              <div className="h-2 w-2 bg-slate-600/20 rounded-full animate-pulse" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function ConversationListSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Header skeleton */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-slate-400 animate-pulse" />
          <div className="h-5 w-24 bg-slate-600/40 rounded animate-pulse" />
        </div>
        <div className="flex gap-1">
          <div className="h-8 w-8 bg-slate-600/30 rounded-lg animate-pulse" />
          <div className="h-8 w-8 bg-slate-600/30 rounded-lg animate-pulse" />
        </div>
      </div>

      {/* New conversation button skeleton */}
      <div className="p-3">
        <div className="w-full h-12 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-lg animate-pulse" />
      </div>

      {/* Conversation list skeleton */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        <ConversationSkeleton count={5} />
      </div>
    </div>
  )
}