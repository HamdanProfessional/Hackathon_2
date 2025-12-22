import { useState, useCallback, useRef, useEffect } from "react"

interface LoadingState {
  isLoading: boolean
  stage: "idle" | "sending" | "thinking" | "generating" | "finalizing" | "error" | "retry"
  message?: string
  error?: string
  progress?: number
  retryCount?: number
}

interface UseChatLoadingOptions {
  maxRetries?: number
  retryDelay?: number
  timeout?: number
}

export function useChatLoading(options: UseChatLoadingOptions = {}) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    timeout = 30000
  } = options

  const [state, setState] = useState<LoadingState>({
    isLoading: false,
    stage: "idle"
  })

  const timeoutRef = useRef<NodeJS.Timeout>()
  const retryCountRef = useRef(0)

  const setLoading = useCallback((loading: boolean, stage: LoadingState["stage"] = "idle", message?: string) => {
    setState(prev => ({
      ...prev,
      isLoading: loading,
      stage,
      message,
      error: undefined
    }))

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Set new timeout if loading
    if (loading && timeout > 0) {
      timeoutRef.current = setTimeout(() => {
        setError("Request timed out. Please try again.")
      }, timeout)
    }
  }, [timeout])

  const setError = useCallback((error: string, shouldRetry: boolean = false) => {
    setState(prev => ({
      ...prev,
      isLoading: false,
      stage: "error",
      error,
      retryCount: retryCountRef.current
    }))

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
  }, [])

  const simulateProgress = useCallback(() => {
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 15
      if (progress >= 90) {
        progress = 90
        clearInterval(interval)
      }
      setState(prev => ({ ...prev, progress }))
    }, 200)

    return () => clearInterval(interval)
  }, [])

  const startSending = useCallback(() => {
    retryCountRef.current = 0
    setLoading(true, "sending", "Sending your message...")
    setState(prev => ({ ...prev, progress: 10 }))
  }, [setLoading])

  const startThinking = useCallback(() => {
    setLoading(true, "thinking", "AI is thinking...")
    setState(prev => ({ ...prev, progress: 30 }))
    return simulateProgress()
  }, [setLoading, simulateProgress])

  const startGenerating = useCallback(() => {
    setLoading(true, "generating", "Generating response...")
    setState(prev => ({ ...prev, progress: 60 }))
    return simulateProgress()
  }, [setLoading, simulateProgress])

  const startFinalizing = useCallback(() => {
    setLoading(true, "finalizing", "Finalizing response...")
    setState(prev => ({ ...prev, progress: 90 }))
  }, [setLoading])

  const setComplete = useCallback(() => {
    setState(prev => ({ ...prev, progress: 100 }))
    setTimeout(() => {
      setLoading(false, "idle")
      setState(prev => ({ ...prev, progress: undefined }))
    }, 300)
  }, [setLoading])

  const retry = useCallback(async (retryFn: () => Promise<void>) => {
    if (retryCountRef.current >= maxRetries) {
      setError("Maximum retry attempts reached. Please refresh the page.", false)
      return
    }

    retryCountRef.current++
    setState(prev => ({
      ...prev,
      stage: "retry",
      isLoading: true,
      message: `Retrying... (${retryCountRef.current}/${maxRetries})`
    }))

    await new Promise(resolve => setTimeout(resolve, retryDelay))

    try {
      await retryFn()
      retryCountRef.current = 0
    } catch (error) {
      setError(error instanceof Error ? error.message : "Retry failed", true)
    }
  }, [maxRetries, retryDelay, setError])

  const reset = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    retryCountRef.current = 0
    setState({
      isLoading: false,
      stage: "idle"
    })
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return {
    ...state,
    setLoading,
    setError,
    startSending,
    startThinking,
    startGenerating,
    startFinalizing,
    setComplete,
    retry,
    reset,
    canRetry: retryCountRef.current < maxRetries,
    retryCount: retryCountRef.current
  }
}

// Hook for managing conversation loading states
export function useConversationLoading() {
  const [isLoading, setIsLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState("")
  const [progress, setProgress] = useState(0)

  const loadConversation = useCallback(async (
    loadFn: () => Promise<void>,
    message: string = "Loading conversation..."
  ) => {
    setIsLoading(true)
    setLoadingMessage(message)
    setProgress(0)

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const next = prev + Math.random() * 20
          return next >= 90 ? 90 : next
        })
      }, 200)

      await loadFn()

      clearInterval(progressInterval)
      setProgress(100)

      setTimeout(() => {
        setIsLoading(false)
        setProgress(0)
      }, 300)
    } catch (error) {
      setIsLoading(false)
      setProgress(0)
      throw error
    }
  }, [])

  return {
    isLoading,
    loadingMessage,
    progress,
    loadConversation
  }
}