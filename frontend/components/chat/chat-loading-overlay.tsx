import { cn } from "@/lib/utils"
import { Loader2, Waves, Sparkles } from "lucide-react"

interface ChatLoadingOverlayProps {
  isLoading: boolean
  message?: string
  className?: string
}

export function ChatLoadingOverlay({ isLoading, message = "Loading chat interface...", className }: ChatLoadingOverlayProps) {
  if (!isLoading) return null

  return (
    <div className={cn(
      "absolute inset-0 z-50 flex flex-col items-center justify-center bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 backdrop-blur-xl rounded-2xl",
      className
    )}>
      <div className="relative mb-6">
        {/* Animated background orbs */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-32 h-32 bg-blue-500/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-0 right-0 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        </div>

        {/* Central loading icon */}
        <div className="relative bg-slate-800/80 backdrop-blur-sm border border-white/10 rounded-2xl p-8 shadow-2xl">
          <div className="relative">
            <Waves className="w-16 h-16 text-blue-400 animate-pulse" />
            <Sparkles className="absolute -top-2 -right-2 w-6 h-6 text-purple-400 animate-bounce" />
            <Sparkles className="absolute -bottom-2 -left-2 w-5 h-5 text-blue-400 animate-bounce" style={{ animationDelay: '0.5s' }} />
          </div>
        </div>
      </div>

      {/* Loading message */}
      <div className="text-center space-y-3">
        <h3 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
          {message}
        </h3>

        {/* Animated dots */}
        <div className="flex justify-center gap-2">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        </div>

        {/* Loading spinner */}
        <div className="flex items-center justify-center gap-2 text-slate-400 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Preparing your AI assistant</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-64 mt-6 h-1 bg-slate-700/50 rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"
             style={{
               width: '60%',
               animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
             }} />
      </div>
    </div>
  )
}

interface MinimalLoadingIndicatorProps {
  className?: string
  size?: "sm" | "md" | "lg"
}

export function MinimalLoadingIndicator({ className, size = "md" }: MinimalLoadingIndicatorProps) {
  const sizeClasses = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-12 h-12"
  }

  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div className={cn(
        "relative",
        sizeClasses[size]
      )}>
        {/* Outer ring */}
        <div className={cn(
          "absolute inset-0 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin",
          sizeClasses[size]
        )} />
        {/* Inner ring */}
        <div className={cn(
          "absolute inset-1 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin",
          "animation-direction-reverse"
        )}
             style={{
               animationDuration: '1.5s',
               animationDirection: 'reverse',
             }} />
        {/* Center dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className={cn(
            size === "sm" ? "w-1.5 h-1.5" : size === "md" ? "w-2 h-2" : "w-3 h-3",
            "bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-pulse"
          )} />
        </div>
      </div>
    </div>
  )
}