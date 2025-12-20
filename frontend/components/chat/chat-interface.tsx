"use client";

import { useState, useEffect, useRef } from "react";
import { sendChatMessage, getConversationMessages, type ChatMessage } from "@/lib/chat-client";
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
  Waves
} from "lucide-react";
import { useSpeechRecognition, useSpeechSynthesis } from "@/hooks/use-speech";

interface ChatInterfaceProps {
  conversationId?: number;
  onConversationCreated?: (id: number) => void;
}

export default function ChatInterface({
  conversationId,
  onConversationCreated,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [voiceError, setVoiceError] = useState("");
  const [currentConversationId, setCurrentConversationId] = useState<number | undefined>(conversationId);
  const [language, setLanguage] = useState<'en-US' | 'ur-PK'>('en-US');
  const [copiedMessageId, setCopiedMessageId] = useState<number | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [voiceSpeed, setVoiceSpeed] = useState(0.9);
  const [voicePitch, setVoicePitch] = useState(1);
  const [recordingTime, setRecordingTime] = useState(0);
  const [autoPlay, setAutoPlay] = useState(false);
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

  const loadConversationHistory = async (convId: number) => {
    try {
      setLoading(true);
      const history = await getConversationMessages(convId);
      setMessages(history.map(msg => ({ role: msg.role, content: msg.content })));
    } catch (err) {
      console.error("Failed to load conversation history:", err);
      setError("Failed to load conversation history");
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

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900/95 via-slate-800/95 to-slate-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10 overflow-hidden">
      {/* Header with glassmorphism */}
      <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-blue-600/10 border-b border-white/10 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-3 h-3 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 animate-pulse"></div>
            <div className="absolute inset-0 w-3 h-3 rounded-full bg-green-400 animate-ping opacity-75"></div>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              AI Task Assistant
            </h2>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <span>Voice-Enabled</span>
              <span className="text-slate-600">•</span>
              <span>{language === 'en-US' ? 'English' : 'اردو'}</span>
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          title="Voice Settings"
        >
          <Settings className="w-5 h-5 text-slate-400" />
        </button>
      </div>

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

        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={isListening ? "Listening..." : "Type or press Space to speak..."}
            className="flex-1 px-4 py-3 bg-slate-800/50 border border-white/10 text-slate-100 placeholder:text-slate-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
            disabled={loading}
          />

          {/* Language Toggle Button */}
          <button
            type="button"
            onClick={() => setLanguage(lang => lang === 'en-US' ? 'ur-PK' : 'en-US')}
            className="px-4 py-3 bg-gradient-to-br from-slate-700 to-slate-600 hover:from-slate-600 hover:to-slate-500 border border-white/10 rounded-xl transition-all shadow-lg text-sm font-medium backdrop-blur-sm"
            title={`Switch to ${language === 'en-US' ? 'Urdu' : 'English'}`}
          >
            <span className="text-lg">{language === 'en-US' ? '🇬🇧' : '🇵🇰'}</span>
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
              className={`relative px-4 py-3 rounded-xl transition-all flex items-center justify-center min-w-[52px] shadow-lg backdrop-blur-sm ${
                isListening
                  ? 'bg-gradient-to-br from-red-600 to-red-500 hover:from-red-700 hover:to-red-600'
                  : 'bg-gradient-to-br from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600'
              }`}
              title={isListening ? 'Stop recording (Esc)' : 'Start voice input (Space)'}
              disabled={loading}
            >
              {isListening && (
                <div className="absolute inset-0 rounded-xl bg-red-400 animate-ping opacity-25"></div>
              )}
              {isListening ? (
                <MicOff className="w-5 h-5 text-white animate-pulse relative z-10" />
              ) : (
                <Mic className="w-5 h-5 text-white relative z-10" />
              )}
            </button>
          )}

          <button
            type="submit"
            disabled={!inputValue.trim() || loading}
            data-version="v4-enhanced-voice"
            aria-label="Send message"
            className="px-4 py-3 bg-gradient-to-br from-blue-600 to-blue-500 text-white rounded-xl hover:from-blue-700 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg flex items-center justify-center min-w-[52px] backdrop-blur-sm"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <ArrowRight className="w-5 h-5" />
            )}
          </button>
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
