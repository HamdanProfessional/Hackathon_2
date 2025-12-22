import { cn } from "@/lib/utils"

interface TypingIndicatorProps {
  className?: string
  variant?: "dots" | "wave" | "pulse"
}

export function TypingIndicator({ className, variant = "dots" }: TypingIndicatorProps) {
  if (variant === "wave") {
    return (
      <div className={cn("flex gap-1 items-center", className)}>
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="w-1.5 h-6 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full animate-pulse"
            style={{
              animationDelay: `${i * 0.1}s`,
              animationDuration: '1.2s',
            }}
          />
        ))}
      </div>
    )
  }

  if (variant === "pulse") {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <div className="relative">
          <div className="w-8 h-8 rounded-full bg-blue-500/20 animate-ping" />
          <div className="absolute inset-0 w-8 h-8 rounded-full bg-blue-500/40 animate-pulse" />
        </div>
        <span className="text-sm text-slate-400 animate-pulse">AI is thinking...</span>
      </div>
    )
  }

  // Default dots variant
  return (
    <div className={cn("flex gap-1.5", className)}>
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
    </div>
  )
}

export function FullTypingIndicator({ className }: { className?: string }) {
  return (
    <div className={cn("flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-300", className)}>
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0 mt-1">
          AI
        </div>
        <div className="bg-slate-800/80 backdrop-blur-sm border border-white/10 rounded-2xl px-4 py-3 shadow-lg">
          <TypingIndicator />
        </div>
      </div>
    </div>
  )
}