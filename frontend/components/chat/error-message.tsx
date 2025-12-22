import { cn } from "@/lib/utils"
import { AlertCircle, RefreshCw, WifiOff, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ChatErrorProps {
  error: string
  onRetry?: () => void
  onDismiss?: () => void
  type?: "network" | "timeout" | "general"
  isRetrying?: boolean
  className?: string
}

export function ChatError({
  error,
  onRetry,
  onDismiss,
  type = "general",
  isRetrying = false,
  className
}: ChatErrorProps) {
  const getErrorIcon = () => {
    switch (type) {
      case "network":
        return <WifiOff className="w-4 h-4" />
      case "timeout":
        return <Clock className="w-4 h-4" />
      default:
        return <AlertCircle className="w-4 h-4" />
    }
  }

  const getErrorTitle = () => {
    switch (type) {
      case "network":
        return "Connection Error"
      case "timeout":
        return "Request Timeout"
      default:
        return "Error"
    }
  }

  const getErrorColor = () => {
    switch (type) {
      case "network":
        return "border-orange-200 bg-orange-50 text-orange-800"
      case "timeout":
        return "border-yellow-200 bg-yellow-50 text-yellow-800"
      default:
        return "border-red-200 bg-red-50 text-red-800"
    }
  }

  return (
    <div className={cn(
      "px-4 py-3 border rounded-lg flex items-center justify-between gap-3 animate-in fade-in slide-in-from-top-2 duration-300",
      getErrorColor(),
      className
    )}>
      <div className="flex items-center gap-3 flex-1">
        <div className="flex-shrink-0">
          {getErrorIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm">{getErrorTitle()}</p>
          <p className="text-sm opacity-90 mt-0.5">{error}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        {onRetry && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onRetry}
            disabled={isRetrying}
            className="h-8 px-3"
          >
            {isRetrying ? (
              <>
                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                Retrying...
              </>
            ) : (
              <>
                <RefreshCw className="w-3 h-3 mr-1" />
                Retry
              </>
            )}
          </Button>
        )}

        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className="h-8 w-8 p-0"
          >
            ×
          </Button>
        )}
      </div>
    </div>
  )
}

interface InlineChatErrorProps {
  error: string
  onRetry?: () => void
  isRetrying?: boolean
  className?: string
}

export function InlineChatError({ error, onRetry, isRetrying, className }: InlineChatErrorProps) {
  return (
    <div className={cn(
      "flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm animate-in fade-in duration-300",
      className
    )}>
      <AlertCircle className="w-4 h-4 flex-shrink-0" />
      <span className="flex-1">{error}</span>
      {onRetry && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onRetry}
          disabled={isRetrying}
          className="h-6 px-2 text-xs hover:bg-red-100"
        >
          {isRetrying ? (
            <RefreshCw className="w-3 h-3 animate-spin" />
          ) : (
            <>
              <RefreshCw className="w-3 h-3 mr-1" />
              Retry
            </>
          )}
        </Button>
      )}
    </div>
  )
}

// Toast-style error for less critical errors
export function ToastError({ error, onDismiss }: { error: string; onDismiss?: () => void }) {
  return (
    <div className="fixed bottom-4 right-4 z-50 px-4 py-3 bg-red-600 text-white rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-bottom-4 duration-300 max-w-sm">
      <AlertCircle className="w-5 h-5 flex-shrink-0" />
      <p className="text-sm flex-1">{error}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 hover:bg-red-700 rounded p-0.5 transition-colors"
        >
          ×
        </button>
      )}
    </div>
  )
}