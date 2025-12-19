import { CheckSquare, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"

interface EmptyStateProps {
  onCreateTask?: () => void
  message?: string
}

export function EmptyState({ onCreateTask, message }: EmptyStateProps) {
  const defaultMessage = "You don't have any tasks yet. Create your first task to get started!"

  return (
    <div className="flex flex-col items-center justify-center py-16 px-6">
      <div className="w-24 h-24 rounded-full bg-muted flex items-center justify-center mb-6">
        <CheckSquare className="h-12 w-12 text-muted-foreground" />
      </div>

      <h3 className="text-xl font-semibold text-foreground mb-2">
        No tasks yet
      </h3>

      <p className="text-muted-foreground text-center max-w-sm mb-8">
        {message || defaultMessage}
      </p>

      {onCreateTask && (
        <Button onClick={onCreateTask} className="gradient-bg">
          <Plus className="h-4 w-4 mr-2" />
          Create your first task
        </Button>
      )}
    </div>
  )
}