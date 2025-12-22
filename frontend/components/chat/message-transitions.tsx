import React from "react"
import { cn } from "@/lib/utils"
import { ChatMessage } from "@/lib/chat-client"

interface MessageTransitionProps {
  message: ChatMessage
  index: number
  isLatest?: boolean
  className?: string
  children: React.ReactNode
}

export function MessageTransition({
  message,
  index,
  isLatest = false,
  className,
  children
}: MessageTransitionProps) {
  return (
    <div
      className={cn(
        // Base animation
        "animate-in fade-in slide-in-from-bottom-2 duration-300",
        // Stagger animation for multiple messages
        isLatest ? "duration-500" : "duration-300",
        // Add subtle scale animation for new messages
        isLatest && "animate-in zoom-in-95",
        className
      )}
      style={{
        animationDelay: isLatest ? "0ms" : `${Math.min(index * 50, 200)}ms`,
        animationFillMode: "both"
      }}
    >
      {children}
    </div>
  )
}

interface SmoothScrollProps {
  containerRef: React.RefObject<HTMLDivElement>
  children: React.ReactNode
  behavior?: "smooth" | "auto"
  delay?: number
}

export function SmoothScroll({ containerRef, children, behavior = "smooth", delay = 100 }: SmoothScrollProps) {
  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.scrollTo({
          top: containerRef.current.scrollHeight,
          behavior
        })
      }
    }, delay)

    return () => clearTimeout(timer)
  }, [children, containerRef, behavior, delay])

  return <>{children}</>
}

interface FadeTransitionProps {
  show: boolean
  children: React.ReactNode
  duration?: number
  className?: string
}

export function FadeTransition({ show, children, duration = 300, className }: FadeTransitionProps) {
  return (
    <div
      className={cn(
        "transition-all",
        show
          ? "opacity-100 translate-y-0"
          : "opacity-0 translate-y-2",
        className
      )}
      style={{
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: "cubic-bezier(0.4, 0, 0.2, 1)"
      }}
    >
      {children}
    </div>
  )
}

interface SlideUpProps {
  show: boolean
  children: React.ReactNode
  distance?: number
  duration?: number
  className?: string
}

export function SlideUp({ show, children, distance = 20, duration = 300, className }: SlideUpProps) {
  return (
    <div
      className={cn(
        "transition-all",
        show
          ? "opacity-100 translate-y-0"
          : `opacity-0 translate-y-${distance}`,
        className
      )}
      style={{
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: "cubic-bezier(0.4, 0, 0.2, 1)"
      }}
    >
      {children}
    </div>
  )
}

interface ScaleInProps {
  show: boolean
  children: React.ReactNode
  scale?: number
  duration?: number
  className?: string
}

export function ScaleIn({ show, children, scale = 0.95, duration = 200, className }: ScaleInProps) {
  return (
    <div
      className={cn(
        "transition-all",
        show
          ? "opacity-100 scale-100"
          : `opacity-0 scale-${scale}`,
        className
      )}
      style={{
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: "cubic-bezier(0.4, 0, 0.2, 1)"
      }}
    >
      {children}
    </div>
  )
}

// Hook for smooth scroll with requestAnimationFrame
export function useSmoothScrollToBottom(elementRef: React.RefObject<HTMLElement>) {
  const scrollToBottom = React.useCallback((behavior: ScrollBehavior = "smooth") => {
    const element = elementRef.current
    if (!element) return

    const startTop = element.scrollTop
    const targetTop = element.scrollHeight - element.clientHeight
    const distance = targetTop - startTop
    const duration = behavior === "smooth" ? 300 : 0

    if (duration === 0) {
      element.scrollTop = targetTop
      return
    }

    let startTime: number | null = null

    function animateScroll(currentTime: number) {
      if (!startTime) startTime = currentTime
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // Easing function (ease-out-cubic)
      const easeOutCubic = 1 - Math.pow(1 - progress, 3)
      if (element) {
        element.scrollTop = startTop + distance * easeOutCubic
      }

      if (progress < 1) {
        requestAnimationFrame(animateScroll)
      }
    }

    requestAnimationFrame(animateScroll)
  }, [elementRef])

  return scrollToBottom
}