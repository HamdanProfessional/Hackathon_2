"use client";

import { useState, useEffect, useRef } from "react";
import { sendChatMessage, getConversationMessages, getConversations, type ChatMessage } from "@/lib/chat-client";
import { apiClient } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  ArrowRight,
  Loader2,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Copy,
  Check,
  Settings,
  Clock,
  Waves,
  History,
  Plus,
  MessageSquare,
  X,
  Trash2
} from "lucide-react";
import { useSpeechRecognition, useSpeechSynthesis } from "@/hooks/use-speech";

interface ChatInterfaceProps {
  conversationId?: string;
  onConversationCreated?: (id: string) => void;
  showHeader?: boolean; // New prop to control header visibility
  showHistory?: boolean; // External control of history sidebar
  onShowHistoryChange?: (show: boolean) => void; // Callback when history toggle changes
}

export default function ChatInterface({
  conversationId,
  onConversationCreated,
  showHeader = true, // Default to true for backwards compatibility
  showHistory: externalShowHistory,
  onShowHistoryChange,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [voiceError, setVoiceError] = useState("");
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(conversationId);
  const [language, setLanguage] = useState<'en-US' | 'ur-PK'>('en-US');
  const [copiedMessageId, setCopiedMessageId] = useState<number | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [voiceSpeed, setVoiceSpeed] = useState(0.9);
  const [voicePitch, setVoicePitch] = useState(1);
  const [recordingTime, setRecordingTime] = useState(0);
  const [autoPlay, setAutoPlay] = useState(false);
  const [internalShowHistory, setInternalShowHistory] = useState(false);

  // Use external history state if provided, otherwise use internal state
  const showHistory = externalShowHistory !== undefined ? externalShowHistory : internalShowHistory;

  // Wrapper to handle both internal and external state changes
  const handleSetShowHistory = (newValue: boolean) => {
    if (onShowHistoryChange) {
      onShowHistoryChange(newValue);
    } else {
      setInternalShowHistory(newValue);
    }
  };
  const [conversations, setConversations] = useState<Array<{
    id: string;
    created_at: string;
    updated_at: string;
    preview?: string;
  }>>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Speech hooks
  const {
    transcript,
    isListening,
    isSupported: isRecognitionSupported,
    startListening,
    stopListening,
    resetTranscript,
    error: speechError
  } = useSpeechRecognition();

  const {
    speak,
    cancel: cancelSpeech,
    isSpeaking,
    isSupported: isSynthesisSupported
  } = useSpeechSynthesis();

  // Version marker
  useEffect(() => {
    console.log('🎯 ChatInterface v4.0 - ENHANCED VOICE + DESIGN - Loaded at:', new Date().toISOString());
  }, []);

  // Recording timer
  useEffect(() => {
    if (isListening) {
      setRecordingTime(0);
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
      setRecordingTime(0);
    }
    return () => {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    };
  }, [isListening]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Spacebar to toggle recording (when not typing in input)
      if (e.code === 'Space' && e.target === document.body && !loading) {
        e.preventDefault();
        if (isListening) {
          stopListening();
        } else {
          startListening(language);
        }
      }
      // Escape to stop recording or speaking
      if (e.code === 'Escape') {
        if (isListening) {
          stopListening();
        }
        if (isSpeaking) {
          cancelSpeech();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isListening, isSpeaking, loading, language, startListening, stopListening, cancelSpeech]);

  // Auto-play new AI responses
  useEffect(() => {
    if (autoPlay && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant' && !isSpeaking) {
        speak(lastMessage.content, language, voiceSpeed, voicePitch);
      }
    }
  }, [messages, autoPlay, language, voiceSpeed, voicePitch]);

  // Handle speech recognition transcript
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript);
      resetTranscript();
    }
  }, [transcript, resetTranscript]);

  // Handle speech recognition errors
  useEffect(() => {
    if (speechError) {
      setVoiceError(speechError);
      setTimeout(() => setVoiceError(""), 5000);
    }
  }, [speechError]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load conversation history when conversationId changes
  useEffect(() => {
    if (conversationId && conversationId !== currentConversationId) {
      loadConversationHistory(conversationId);
      setCurrentConversationId(conversationId);
    } else if (!conversationId) {
      // New conversation - clear messages
      setMessages([]);
      setCurrentConversationId(undefined);
    }
  }, [conversationId]);

  const loadConversationHistory = async (convId: string) => {
    try {
      setLoading(true);
      console.log('📖 Loading conversation history for ID:', convId);
      const history = await getConversationMessages(convId);
      console.log('✅ History loaded:', history.length, 'messages');
      setMessages(history.map(msg => ({ role: msg.role, content: msg.content })));
    } catch (err: any) {
      console.error("❌ Failed to load conversation history:", err);

      // If conversation not found (404), reset the chat state
      if (err.response?.status === 404) {
        console.warn('🗑️ Conversation not found in database, resetting chat');
        setCurrentConversationId(undefined);
        setMessages([]);
        setError("Conversation not found. Starting fresh.");
        setTimeout(() => setError(""), 3000);
      } else {
        setError("Failed to load conversation history");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || loading) {
      return;
    }

    const userMessage = inputValue.trim();
    setInputValue("");
    setError("");
    setLoading(true);

    // Optimistically add user message to UI
    const userMsg: ChatMessage = {
      role: "user",
      content: userMessage,
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      console.log('📤 Sending message:', userMessage);
      console.log('📋 Conversation ID:', currentConversationId);

      // Send message to backend
      const response = await sendChatMessage(userMessage, currentConversationId);
      console.log('✅ Response received:', response);

      // Update conversation ID if this was the first message
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
        onConversationCreated?.(response.conversation_id);
        // Reload conversations list after a short delay to ensure DB commit
        setTimeout(() => {
          console.log('🔄 Reloading conversations list after new conversation created');
          loadConversationsList();
        }, 500);
      }

      // Add assistant response to messages
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: response.response,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('❌ Chat error:', err);
      console.error('❌ Error response:', err.response);
      console.error('❌ Error status:', err.response?.status);
      console.error('❌ Error data:', err.response?.data);

      let errorMessage = "Failed to send message";
      if (err.response?.status === 401) {
        errorMessage = "Please login to use chat";
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      // Remove optimistically added user message on error
      setMessages((prev) => prev.slice(0, -1));
      // Restore input value so user can retry
      setInputValue(userMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = (transcript: string) => {
    setInputValue(transcript);
    setVoiceError("");
  };

  const handleVoiceError = (error: string) => {
    setVoiceError(error);
    setTimeout(() => setVoiceError(""), 5000);
  };

  const copyToClipboard = async (text: string, messageId: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };

  // Delete conversation handler
  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering switchConversation
    try {
      console.log('🗑️ Deleting conversation:', convId);
      await apiClient.deleteConversation(convId);

      // Remove from local state
      setConversations(prev => prev.filter(c => c.id !== convId));

      // If deleted conversation was current, start new conversation
      if (currentConversationId === convId) {
        startNewConversation();
      }

      console.log('✅ Conversation deleted');
    } catch (err: any) {
      console.error('❌ Failed to delete conversation:', err);
      console.error('Error details:', err.response?.data);
    }
  };

  // Define conversation management functions before useEffects
  const loadConversationsList = async () => {
    try {
      console.log('📜 Loading conversations list...');
      const convs = await getConversations();
      console.log('✅ Conversations loaded:', convs.length);

      // Load first message for each conversation as preview
      const convsWithPreviews = await Promise.all(
        convs.map(async (conv) => {
          try {
            const msgs = await getConversationMessages(conv.id);
            const firstUserMsg = msgs.find(m => m.role === 'user');
            return {
              ...conv,
              preview: firstUserMsg?.content.substring(0, 50) || 'New conversation'
            };
          } catch {
            return { ...conv, preview: 'New conversation' };
          }
        })
      );
      setConversations(convsWithPreviews);
    } catch (err: any) {
      console.error('❌ Failed to load conversations:', err);
      console.error('Error details:', err.response?.data);
    }
  };

  // Load conversations on mount with delay for authentication
  useEffect(() => {
    console.log('🚀 Chat interface mounted, waiting for authentication...');

    // Wait for authentication to complete before fetching
    const initializeChat = async () => {
      // Add delay to allow authentication to complete
      await new Promise(resolve => setTimeout(resolve, 500));

      console.log('⏱️ Delay completed, checking authentication...');

      // Check if user is authenticated
      const token = localStorage.getItem('todo_access_token');
      if (!token) {
        console.log('❌ No authentication token found, skipping conversation load');
        return;
      }

      console.log('✅ Token found, loading conversations from database...');

      // Load the conversations list from database
      try {
        console.log('📜 Loading conversations list...');
        const convs = await getConversations();
        console.log('✅ Conversations loaded:', convs.length);

        // Load previews for conversations
        const convsWithPreviews = await Promise.all(
          convs.map(async (conv) => {
            try {
              const msgs = await getConversationMessages(conv.id);
              const firstUserMsg = msgs.find(m => m.role === 'user');
              return {
                ...conv,
                preview: firstUserMsg?.content.substring(0, 50) || 'New conversation'
              };
            } catch {
              return { ...conv, preview: 'New conversation' };
            }
          })
        );
        setConversations(convsWithPreviews);

        // If there are conversations and no current conversation is set, load the most recent one
        if (convsWithPreviews.length > 0 && !currentConversationId) {
          const mostRecent = convsWithPreviews[0]; // Conversations are ordered by updated_at DESC
          console.log('📖 Loading most recent conversation:', mostRecent.id);
          setCurrentConversationId(mostRecent.id);
          await loadConversationHistory(mostRecent.id);
        }
      } catch (err: any) {
        console.error('❌ Failed to initialize chat:', err);
        // Don't show error to user on initial load, just log it
      } finally {
        // Ensure loading is always set to false after initialization
        setLoading(false);
      }
    };

    // Set a timeout to ensure the interface doesn't stay in loading state forever
    const timeoutId = setTimeout(() => {
      setLoading(false);
      console.log('⏰ Initialization timeout reached');
    }, 5000);

    initializeChat();

    // Cleanup timeout on unmount
    return () => clearTimeout(timeoutId);
  }, []);


  const switchConversation = async (convId: string) => {
    setCurrentConversationId(convId);
    await loadConversationHistory(convId);
    handleSetShowHistory(false);
    onConversationCreated?.(convId);
  };

  const startNewConversation = () => {
    setMessages([]);
    setCurrentConversationId(undefined);
    handleSetShowHistory(false);
  };

  // If component is still in initial loading state, show a minimal loader
  if (loading && messages.length === 0 && !error) {
    return (
      <div className="relative flex flex-col h-full bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 overflow-hidden">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-slate-400">Loading chat interface...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex flex-col h-full bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 overflow-hidden">
      {/* Enhanced Header with improved design - only show if showHeader is true */}
      {showHeader && (
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-violet-600/20 to-purple-600/20 border-b border-zinc-800/50 backdrop-blur-sm relative overflow-hidden">
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-violet-600/5 to-purple-600/5 animate-pulse"></div>

        <div className="flex items-center gap-3 relative z-10">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-600/25 relative">
            <Waves className="w-4 h-4 text-white" />
            {/* Animated glow effect */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-600 to-purple-600 animate-ping opacity-20"></div>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
              AI Task Assistant
              {/* Status indicator */}
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
            </h3>
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <span className="flex items-center gap-1">
                <span className={`h-2 w-2 rounded-full ${isSpeaking ? 'bg-purple-500 animate-pulse' : 'bg-zinc-600'}`}></span>
                {isSpeaking ? 'Speaking' : 'Powered by Gemini AI'}
              </span>
              <span className="text-zinc-600">•</span>
              <span className="px-1.5 py-0.5 bg-zinc-700/50 rounded-xs text-zinc-300">
                {language === 'en-US' ? 'EN' : 'UR'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 relative z-10">
          <button
            onClick={() => handleSetShowHistory(!showHistory)}
            className={`p-2 hover:bg-white/10 rounded-lg transition-all duration-200 group relative ${showHistory ? 'bg-white/10 text-white' : 'text-zinc-400'}`}
            title="Conversation History"
          >
            <History className="w-4 h-4 group-hover:scale-110 transition-transform" />
            {conversations.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-violet-600 text-white text-xs rounded-full flex items-center justify-center font-semibold shadow-lg">
                {conversations.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 hover:bg-white/10 rounded-lg transition-all duration-200 group ${showSettings ? 'bg-white/10 text-white' : 'text-zinc-400'}`}
            title="Voice Settings"
          >
            <Settings className="w-4 h-4 group-hover:scale-110 transition-transform" />
          </button>
          <button
            className="p-2 hover:bg-white/10 rounded-lg transition-all duration-200 group text-zinc-400"
            title="Minimize"
          >
            <svg className="w-4 h-4 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
          </button>
          <button
            className="p-2 hover:bg-red-500/20 rounded-lg transition-all duration-200 group text-zinc-400 hover:text-red-400"
            title="Close Chat"
          >
            <X className="w-4 h-4 group-hover:scale-110 transition-transform" />
          </button>
        </div>
      </div>
      )}

      {/* Conversation History Sidebar */}
      {showHistory && (
        <div className="absolute top-0 left-0 w-80 h-full bg-slate-900/98 backdrop-blur-xl border-r border-white/10 z-10 flex flex-col">
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
            <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-blue-400" />
              Conversations
              {conversations.length > 0 && (
                <span className="text-xs text-slate-400">({conversations.length})</span>
              )}
            </h3>
            <div className="flex items-center gap-1">
              <button
                onClick={() => {
                  console.log('🔄 Manual refresh of conversations list');
                  loadConversationsList();
                }}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
                title="Refresh conversations"
              >
                <History className="w-4 h-4 text-slate-400" />
              </button>
              <button
                onClick={() => handleSetShowHistory(false)}
                className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-slate-400" />
              </button>
            </div>
          </div>

          <div className="p-3">
            <button
              onClick={startNewConversation}
              className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg"
            >
              <Plus className="w-4 h-4" />
              New Conversation
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-2">
            {conversations.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-sm">
                <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                No conversations yet
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`w-full px-3 py-3 rounded-lg text-left transition-all group relative ${
                    currentConversationId === conv.id
                      ? 'bg-blue-600/20 border border-blue-500/30'
                      : 'bg-slate-800/50 hover:bg-slate-700/50 border border-white/5'
                  }`}
                >
                  <button
                    onClick={() => switchConversation(conv.id)}
                    className="w-full text-left pr-8"
                  >
                    <p className="text-sm text-slate-200 font-medium line-clamp-2 mb-1">
                      {conv.preview}
                    </p>
                    <p className="text-xs text-slate-500">
                      {new Date(conv.updated_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </button>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    className="absolute top-2 right-2 p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-200"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Voice Settings Panel */}
      {showSettings && (
        <div className="px-6 py-4 bg-slate-800/50 border-b border-white/10 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-300">Auto-play responses</span>
            <button
              onClick={() => setAutoPlay(!autoPlay)}
              className={`relative w-12 h-6 rounded-full transition-colors ${
                autoPlay ? 'bg-blue-600' : 'bg-slate-600'
              }`}
            >
              <div
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                  autoPlay ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
          <div>
            <label className="text-sm text-slate-300 block mb-1">
              Voice Speed: {voiceSpeed.toFixed(1)}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={voiceSpeed}
              onChange={(e) => setVoiceSpeed(parseFloat(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>
          <div>
            <label className="text-sm text-slate-300 block mb-1">
              Voice Pitch: {voicePitch.toFixed(1)}
            </label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={voicePitch}
              onChange={(e) => setVoicePitch(parseFloat(e.target.value))}
              className="w-full accent-purple-500"
            />
          </div>
          <div className="text-xs text-slate-400 pt-2 border-t border-white/10">
            <p>⌨️ Shortcuts: <span className="text-slate-300">Space</span> to record, <span className="text-slate-300">Esc</span> to stop</p>
          </div>
        </div>
      )}

      {/* Messages Area with enhanced scrollbar */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 custom-scrollbar">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="relative mb-6">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-3xl"></div>
              <Waves className="w-20 h-20 text-blue-400 relative animate-pulse" />
            </div>
            <h3 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-3">
              Start a Voice-Enabled Conversation
            </h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto mb-4">
              Try saying: <span className="text-blue-400">"Add buy groceries to my list"</span>
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              <span className="px-3 py-1 bg-blue-600/20 border border-blue-500/30 rounded-full text-xs text-blue-300">
                🎤 Voice Input
              </span>
              <span className="px-3 py-1 bg-purple-600/20 border border-purple-500/30 rounded-full text-xs text-purple-300">
                🗣️ Bilingual (EN/UR)
              </span>
              <span className="px-3 py-1 bg-green-600/20 border border-green-500/30 rounded-full text-xs text-green-300">
                🔊 Text-to-Speech
              </span>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} group`}
          >
            <div className="flex flex-col gap-2 max-w-[75%]">
              <div className="flex items-start gap-2">
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0 mt-1">
                    AI
                  </div>
                )}
                <div className="flex-1">
                  <div
                    className={`rounded-2xl px-4 py-3 shadow-lg ${
                      msg.role === "user"
                        ? "bg-gradient-to-br from-blue-600 to-blue-500 text-white"
                        : "bg-slate-800/80 backdrop-blur-sm border border-white/10 text-slate-100"
                    }`}
                  >
                    {msg.role === "user" ? (
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <div className="text-sm prose prose-sm prose-invert max-w-none prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0 prose-code:bg-slate-700 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-pre:bg-slate-900/50 prose-pre:border prose-pre:border-white/10">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>

                  {/* Message actions bar */}
                  <div className="flex items-center gap-2 mt-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-xs text-slate-500">
                      {formatTimestamp(new Date())}
                    </span>

                    {/* Copy button */}
                    <button
                      onClick={() => copyToClipboard(msg.content, idx)}
                      className="p-1 hover:bg-slate-700/50 rounded transition-colors"
                      title="Copy message"
                    >
                      {copiedMessageId === idx ? (
                        <Check className="w-3 h-3 text-green-400" />
                      ) : (
                        <Copy className="w-3 h-3 text-slate-400" />
                      )}
                    </button>

                    {/* Text-to-Speech Button for AI Messages */}
                    {msg.role === "assistant" && isSynthesisSupported && (
                      <button
                        type="button"
                        onClick={() => {
                          if (isSpeaking) {
                            cancelSpeech();
                          } else {
                            speak(msg.content, language, voiceSpeed, voicePitch);
                          }
                        }}
                        className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-slate-700/50 rounded transition-colors"
                        title={isSpeaking ? 'Stop speaking' : 'Read aloud'}
                      >
                        {isSpeaking ? (
                          <>
                            <VolumeX className="w-3 h-3 text-red-400 animate-pulse" />
                            <span className="text-red-400">Stop</span>
                          </>
                        ) : (
                          <>
                            <Volume2 className="w-3 h-3 text-blue-400" />
                            <span className="text-blue-400">Listen</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0 mt-1">
                    U
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
                AI
              </div>
              <div className="bg-slate-800/80 backdrop-blur-sm border border-white/10 rounded-2xl px-4 py-3 shadow-lg">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recording indicator with transcript preview */}
        {isListening && transcript && (
          <div className="flex justify-end">
            <div className="max-w-[75%] bg-blue-600/20 border border-blue-500/30 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-blue-300">Recording preview...</span>
              </div>
              <p className="text-sm text-slate-200 italic">{transcript}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-6 py-2 bg-red-50 border-t border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Voice Error Message */}
      {voiceError && (
        <div className="px-6 py-2 bg-yellow-50 border-t border-yellow-200">
          <p className="text-sm text-yellow-600">{voiceError}</p>
        </div>
      )}

      {/* Input Area with glassmorphism */}
      <div className="px-6 py-4 bg-gradient-to-r from-slate-900/50 via-slate-800/50 to-slate-900/50 border-t border-white/10 backdrop-blur-sm">
        {/* Recording Timer Bar */}
        {isListening && (
          <div className="mb-3 flex items-center gap-3 px-4 py-2 bg-red-600/10 border border-red-500/30 rounded-lg">
            <div className="flex items-center gap-2 flex-1">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-red-400 font-medium">Recording...</span>
              <div className="flex gap-0.5 ml-2">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-red-400 rounded-full animate-pulse"
                    style={{
                      height: `${Math.random() * 16 + 8}px`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  />
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2 text-red-400">
              <Clock className="w-4 h-4" />
              <span className="text-sm font-mono">{formatTime(recordingTime)}</span>
            </div>
          </div>
        )}

        <form onSubmit={handleSendMessage} className="flex flex-col gap-2">
          {/* Main input row */}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={isListening ? "Listening..." : "Type or speak..."}
              className="flex-1 px-3 py-2.5 bg-slate-800/50 border border-white/10 text-slate-100 placeholder:text-slate-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all text-sm"
              disabled={loading}
            />

            <button
              type="submit"
              disabled={!inputValue.trim() || loading}
              data-version="v4-enhanced-voice"
              aria-label="Send message"
              className="px-3 py-2.5 bg-gradient-to-br from-blue-600 to-blue-500 text-white rounded-xl hover:from-blue-700 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg flex items-center justify-center min-w-[44px] backdrop-blur-sm"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <ArrowRight className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Voice controls row - stacked for narrow views */}
          <div className="flex gap-2">
            {/* Language Toggle Button */}
            <button
              type="button"
              onClick={() => setLanguage(lang => lang === 'en-US' ? 'ur-PK' : 'en-US')}
              className="flex-1 px-3 py-2 bg-gradient-to-br from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-white/10 rounded-lg transition-all shadow-lg text-xs font-medium backdrop-blur-sm flex items-center justify-center gap-1.5"
              title={`Switch to ${language === 'en-US' ? 'Urdu' : 'English'}`}
            >
              <span className="text-base">{language === 'en-US' ? '🇬🇧' : '🇵🇰'}</span>
              <span className="text-slate-300">{language === 'en-US' ? 'EN' : 'UR'}</span>
            </button>

            {/* Microphone Button with Recording Animation */}
            {isRecognitionSupported && (
              <button
                type="button"
                onClick={() => {
                  if (isListening) {
                    stopListening();
                  } else {
                    startListening(language);
                  }
                }}
                className={`flex-1 relative px-3 py-2 rounded-lg transition-all flex items-center justify-center gap-1.5 shadow-lg backdrop-blur-sm ${
                  isListening
                    ? 'bg-gradient-to-br from-red-600 to-red-500 hover:from-red-700 hover:to-red-600'
                    : 'bg-gradient-to-br from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600'
                }`}
                title={isListening ? 'Stop recording (Esc)' : 'Start voice input (Space)'}
                disabled={loading}
              >
                {isListening && (
                  <div className="absolute inset-0 rounded-lg bg-red-400 animate-ping opacity-25"></div>
                )}
                {isListening ? (
                  <>
                    <MicOff className="w-4 h-4 text-white animate-pulse relative z-10" />
                    <span className="text-xs text-white relative z-10">Stop</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-4 h-4 text-white relative z-10" />
                    <span className="text-xs text-white relative z-10">Voice</span>
                  </>
                )}
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Custom scrollbar styles */}
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.3);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(to bottom, rgb(59, 130, 246), rgb(147, 51, 234));
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(to bottom, rgb(37, 99, 235), rgb(126, 34, 206));
        }
      `}</style>
    </div>
  );
}
