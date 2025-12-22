"use client";

import { useState } from "react";
import { MessageCircle, X, Minimize2 } from "lucide-react";
import ChatInterface from "./chat-interface";

/**
 * Floating Chat Widget with Nebula 2025 Theme
 *
 * Features:
 * - Floating button in bottom-right corner
 * - Glassmorphism panel with backdrop blur
 * - Electric Violet accents (Nebula theme)
 * - Persistent conversation state
 */
export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();

  const handleToggle = () => {
    if (isOpen && !isMinimized) {
      setIsOpen(false);
    } else if (isMinimized) {
      setIsMinimized(false);
    } else {
      setIsOpen(true);
      setIsMinimized(false);
    }
  };

  const handleMinimize = () => {
    setIsMinimized(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    setIsMinimized(false);
  };

  return (
    <>
      {/* Floating Button */}
      {(!isOpen || isMinimized) && (
        <button
          onClick={handleToggle}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-violet-600 to-purple-600 text-white shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-200 flex items-center justify-center group"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
          {/* Pulse indicator */}
          <span className="absolute top-0 right-0 w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>
        </button>
      )}

      {/* Chat Panel - Nebula 2025 Glassmorphism Theme */}
      {isOpen && !isMinimized && (
        <div className="fixed bottom-6 right-6 z-50 w-96 h-[600px] rounded-2xl bg-zinc-900/90 backdrop-blur-xl border border-zinc-800 shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
          {/* Header with Nebula gradient */}
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-violet-600/20 to-purple-600/20 border-b border-zinc-800/50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center">
                <MessageCircle className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-zinc-100">AI Task Assistant</h3>
                <p className="text-xs text-zinc-400">Powered by GPT-4</p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleMinimize}
                className="p-1.5 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 transition-colors"
                aria-label="Minimize"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button
                onClick={handleClose}
                className="p-1.5 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 transition-colors"
                aria-label="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Chat Interface with Nebula Theme Overrides */}
          <div className="flex-1 overflow-hidden">
            <style jsx global>{`
              /* Nebula Theme Overrides for Chat Interface */
              .chat-widget-nebula .bg-white {
                background-color: transparent !important;
              }

              .chat-widget-nebula .bg-blue-600 {
                background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
              }

              .chat-widget-nebula .bg-gray-100 {
                background-color: rgb(39 39 42 / 0.5) !important;
                border: 1px solid rgb(63 63 70 / 0.3);
              }

              .chat-widget-nebula .text-gray-800 {
                color: rgb(228 228 231) !important;
              }

              .chat-widget-nebula .text-gray-600 {
                color: rgb(161 161 170) !important;
              }

              .chat-widget-nebula .text-gray-500 {
                color: rgb(113 113 122) !important;
              }

              .chat-widget-nebula .text-gray-700 {
                color: rgb(212 212 216) !important;
              }

              .chat-widget-nebula .text-gray-400 {
                color: rgb(113 113 122) !important;
              }

              .chat-widget-nebula .border-gray-200 {
                border-color: rgb(63 63 70 / 0.3) !important;
              }

              .chat-widget-nebula .border-gray-300 {
                border-color: rgb(63 63 70 / 0.5) !important;
              }

              .chat-widget-nebula input {
                background-color: rgb(39 39 42 / 0.5) !important;
                border-color: rgb(63 63 70 / 0.5) !important;
                color: rgb(228 228 231) !important;
              }

              .chat-widget-nebula input::placeholder {
                color: rgb(113 113 122) !important;
              }

              .chat-widget-nebula input:focus {
                ring-color: rgb(124 58 237) !important;
                border-color: rgb(124 58 237) !important;
              }

              .chat-widget-nebula button[type="submit"] {
                background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
              }

              .chat-widget-nebula button[type="submit"]:hover {
                filter: brightness(1.1);
              }

              /* Scrollbar styling */
              .chat-widget-nebula ::-webkit-scrollbar {
                width: 6px;
              }

              .chat-widget-nebula ::-webkit-scrollbar-track {
                background: rgb(39 39 42 / 0.3);
              }

              .chat-widget-nebula ::-webkit-scrollbar-thumb {
                background: rgb(124 58 237 / 0.5);
                border-radius: 3px;
              }

              .chat-widget-nebula ::-webkit-scrollbar-thumb:hover {
                background: rgb(124 58 237 / 0.8);
              }
            `}</style>

            <div className="chat-widget-nebula h-full">
              <ChatInterface
                conversationId={conversationId}
                onConversationCreated={setConversationId}
                showHeader={false}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
