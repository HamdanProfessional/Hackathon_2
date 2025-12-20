import ChatInterface from '@/components/chat/chat-interface'

export default function ChatPage() {
  // UPDATED VERSION - Dec 20, 2025 - Voice & Bilingual Support
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Background effects */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent to-transparent pointer-events-none" />

      <div className="relative container mx-auto h-screen p-4 flex flex-col">
        <header className="mb-6 text-center">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-2">
            AI Task Assistant
          </h1>
          <p className="text-slate-400">
            Chat naturally to manage your tasks - Now with Voice Commands & Bilingual Support! 🎤
          </p>
        </header>

        <div className="flex-1 min-h-0">
          <ChatInterface />
        </div>
      </div>
    </div>
  )
}
