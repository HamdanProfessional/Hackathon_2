import { cn } from "@/lib/utils"
import { Loader2, Brain, Sparkles } from "lucide-react"

interface ProgressIndicatorProps {
  progress: number
  message?: string
  showPercentage?: boolean
  className?: string
  variant?: "linear" | "circular"
  size?: "sm" | "md" | "lg"
}

export function ProgressIndicator({
  progress,
  message,
  showPercentage = true,
  className,
  variant = "linear",
  size = "md"
}: ProgressIndicatorProps) {
  const sizeClasses = {
    sm: "h-1",
    md: "h-2",
    lg: "h-3"
  }

  if (variant === "circular") {
    const radius = size === "sm" ? 16 : size === "md" ? 24 : 32
    const strokeWidth = size === "sm" ? 3 : size === "md" ? 4 : 5
    const normalizedRadius = radius - strokeWidth * 2
    const circumference = normalizedRadius * 2 * Math.PI
    const strokeDashoffset = circumference - (progress / 100) * circumference

    return (
      <div className={cn("flex flex-col items-center gap-2", className)}>
        <div className="relative">
          <svg
            height={radius * 2}
            width={radius * 2}
            className="transform -rotate-90"
          >
            {/* Background circle */}
            <circle
              stroke="rgba(255, 255, 255, 0.1)"
              fill="transparent"
              strokeWidth={strokeWidth}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            {/* Progress circle */}
            <circle
              stroke="url(#gradient)"
              fill="transparent"
              strokeWidth={strokeWidth}
              strokeDasharray={circumference + ' ' + circumference}
              style={{ strokeDashoffset }}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              className="transition-all duration-300 ease-out"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3B82F6" />
                <stop offset="100%" stopColor="#9333EA" />
              </linearGradient>
            </defs>
          </svg>
          {showPercentage && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-medium text-slate-300">
                {Math.round(progress)}%
              </span>
            </div>
          )}
        </div>
        {message && (
          <p className="text-xs text-slate-400 text-center max-w-32">{message}</p>
        )}
      </div>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      {message && (
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm text-slate-400">{message}</p>
          {showPercentage && (
            <span className="text-xs text-slate-500">{Math.round(progress)}%</span>
          )}
        </div>
      )}
      <div className={cn(
        "w-full bg-slate-700/50 rounded-full overflow-hidden",
        sizeClasses[size]
      )}>
        <div
          className={cn(
            "h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-300 ease-out",
            "relative overflow-hidden"
          )}
          style={{ width: `${progress}%` }}
        >
          {/* Animated shimmer effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 animate-pulse"
               style={{
                 width: '200%',
                 animation: 'shimmer 2s infinite',
               }} />
        </div>
      </div>
    </div>
  )
}

interface ChatProcessingIndicatorProps {
  isProcessing: boolean
  stage?: "thinking" | "generating" | "finalizing"
  progress?: number
  className?: string
}

export function ChatProcessingIndicator({
  isProcessing,
  stage = "thinking",
  progress = 0,
  className
}: ChatProcessingIndicatorProps) {
  if (!isProcessing) return null

  const getStageMessage = () => {
    switch (stage) {
      case "thinking":
        return "AI is thinking..."
      case "generating":
        return "Generating response..."
      case "finalizing":
        return "Finalizing answer..."
      default:
        return "Processing..."
    }
  }

  const getStageIcon = () => {
    switch (stage) {
      case "thinking":
        return <Brain className="w-4 h-4 text-blue-400 animate-pulse" />
      case "generating":
        return <Sparkles className="w-4 h-4 text-purple-400 animate-bounce" />
      case "finalizing":
        return <Loader2 className="w-4 h-4 text-green-400 animate-spin" />
      default:
        return <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
    }
  }

  return (
    <div className={cn(
      "flex items-center gap-3 px-4 py-3 bg-slate-800/50 border border-white/10 rounded-lg",
      className
    )}>
      {getStageIcon()}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-300">{getStageMessage()}</p>
        {progress > 0 && (
          <ProgressIndicator
            progress={progress}
            variant="linear"
            size="sm"
            className="mt-2"
          />
        )}
      </div>
    </div>
  )
}

// Add shimmer animation to global styles
export const shimmerKeyframes = `
  @keyframes shimmer {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }
`