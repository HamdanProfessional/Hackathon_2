"use client";

import { useState, useEffect, useRef } from "react";
import { sendChatMessage, getConversationMessages, type ChatMessage } from "@/lib/chat-client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import VoiceInputButton from "@/components/ui/voice-input-button";
import { ArrowRight, Loader2, Mic, MicOff, Volume2, VolumeX } from "lucide-react";
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    console.log('🎯 ChatInterface v3.0 - VOICE + BILINGUAL - Loaded at:', new Date().toISOString());
  }, []);

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

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800">AI Task Assistant</h2>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="text-sm text-gray-600">Online</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-2">
              <svg
                className="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-500 text-sm max-w-md mx-auto">
              Ask me to add tasks, like "Add buy groceries to my list" or "Remind me to call mom tomorrow"
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className="flex flex-col gap-2 max-w-[70%]">
              <div
                className={`rounded-lg px-4 py-2 ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {msg.role === "user" ? (
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <div className="text-sm prose prose-sm max-w-none prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0 prose-code:bg-gray-200 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-gray-800 prose-pre:text-gray-100">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>

              {/* Text-to-Speech Button for AI Messages */}
              {msg.role === "assistant" && isSynthesisSupported && (
                <button
                  type="button"
                  onClick={() => {
                    if (isSpeaking) {
                      cancelSpeech();
                    } else {
                      speak(msg.content, language);
                    }
                  }}
                  className="self-start flex items-center gap-1 px-2 py-1 text-xs text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
                  title={isSpeaking ? 'Stop speaking' : 'Read aloud'}
                >
                  {isSpeaking ? (
                    <>
                      <VolumeX className="w-3 h-3 animate-pulse" />
                      <span>Stop</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-3 h-3" />
                      <span>Listen</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
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

      {/* Input Area */}
      <div className="px-6 py-4 border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message or click mic to speak..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          {/* Language Toggle Button */}
          <button
            type="button"
            onClick={() => setLanguage(lang => lang === 'en-US' ? 'ur-PK' : 'en-US')}
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
            title={`Current: ${language === 'en-US' ? 'English' : 'Urdu'}`}
          >
            {language === 'en-US' ? '🇬🇧 EN' : '🇵🇰 UR'}
          </button>

          {/* Microphone Button for Voice Input */}
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
              className={`px-4 py-2 rounded-lg transition-colors flex items-center justify-center min-w-[44px] ${
                isListening
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-purple-600 hover:bg-purple-700 text-white'
              }`}
              title={isListening ? 'Stop recording' : 'Start voice input'}
              disabled={loading}
            >
              {isListening ? (
                <MicOff className="w-5 h-5 animate-pulse" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </button>
          )}

          <button
            type="submit"
            disabled={!inputValue.trim() || loading}
            data-version="v3-voice-bilingual"
            aria-label="Send message"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center min-w-[44px]"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <ArrowRight className="w-5 h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
