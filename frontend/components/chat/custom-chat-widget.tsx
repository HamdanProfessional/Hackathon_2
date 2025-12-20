"use client"

import { useState, useEffect, useRef } from 'react'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowRight, Loader2, MessageSquare, Trash2 } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export function CustomChatWidget() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Version marker to verify deployment
  useEffect(() => {
    console.log('🎯 CustomChatWidget v2.0 - ARROW BUTTON VERSION - Loaded at:', new Date().toISOString())
  }, [])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Load conversation from localStorage on mount
  useEffect(() => {
    const savedConvId = localStorage.getItem('current_conversation_id')
    if (savedConvId) {
      loadConversation(savedConvId)
    }
  }, [])

  const loadConversation = async (convId: string) => {
    try {
      const conversation = await apiClient.getConversation(convId)
      setMessages(conversation.messages.filter((m: Message) =>
        m.role === 'user' || m.role === 'assistant'
      ))
      setConversationId(convId)
    } catch (err) {
      console.error('Failed to load conversation:', err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setError(null)
    setIsLoading(true)

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMsg])

    try {
      console.log('Sending message:', userMessage)
      console.log('Conversation ID:', conversationId)
      console.log('API Base URL:', process.env.NEXT_PUBLIC_API_URL)

      const response = await apiClient.sendChatMessage(userMessage, conversationId)
      console.log('Response received:', response)

      // Update conversation ID
      if (response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id)
        localStorage.setItem('current_conversation_id', response.conversation_id)
      }

      // Replace temp message and add assistant response
      setMessages(prev => [
        ...prev.filter(m => m.id !== tempUserMsg.id),
        {
          id: `user-${Date.now()}`,
          role: 'user',
          content: userMessage,
          created_at: new Date().toISOString()
        },
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.response,
          created_at: new Date().toISOString()
        }
      ])
    } catch (err: any) {
      console.error('Chat error:', err)
      console.error('Error response:', err.response)
      console.error('Error status:', err.response?.status)
      console.error('Error data:', err.response?.data)

      let errorMessage = 'Failed to send message'

      if (err.response?.status === 401) {
        errorMessage = 'Please login to use chat'
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      }

      setError(errorMessage)
      // Remove optimistic message on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id))
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startNewConversation = () => {
    setMessages([])
    setConversationId(null)
    localStorage.removeItem('current_conversation_id')
    setInput('')
    inputRef.current?.focus()
  }

  return (
    <Card className="flex flex-col h-full bg-slate-900/95 backdrop-blur-xl border-white/10 shadow-2xl">
      <CardHeader className="border-b border-white/10 pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">AI Task Assistant</h2>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={startNewConversation}
            className="text-slate-400 hover:text-white hover:bg-white/10"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0">
        <div className="h-full overflow-y-auto px-4 py-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <MessageSquare className="w-16 h-16 mb-4 opacity-50" />
              <p className="text-lg">Start chatting to manage your tasks</p>
              <p className="text-sm mt-2">Try: "Add a task to buy groceries"</p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                    : 'bg-white/5 border border-white/10 text-slate-100'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-white/5 border border-white/10 rounded-lg px-4 py-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              </div>
            </div>
          )}

          <div ref={scrollRef} />
        </div>
      </CardContent>

      <CardFooter className="border-t border-white/10 pt-4 flex-col items-stretch gap-2">
        {error && (
          <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded px-3 py-2">
            {error}
          </div>
        )}

        <div className="flex gap-2">
          <Input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me about your tasks..."
            disabled={isLoading}
            className="flex-1 bg-white/5 border-white/10 text-white placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/20"
          />
          <Button
            type="button"
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            data-version="v2-arrow"
            aria-label="Send message"
            className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ArrowRight className="w-5 h-5" />
            )}
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}
