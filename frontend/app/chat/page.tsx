"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated, logout } from "@/lib/auth";
import ChatInterface from "@/components/chat/chat-interface";
import { getConversations, type Conversation } from "@/lib/chat-client";
import Link from "next/link";

export default function ChatPage() {
  const router = useRouter();
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    } else {
      loadConversations();
    }
  }, [router]);

  const loadConversations = async () => {
    try {
      setLoadingConversations(true);
      const data = await getConversations();
      setConversations(data);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setLoadingConversations(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const handleConversationCreated = (id: number) => {
    setConversationId(id);
    loadConversations(); // Reload conversation list
  };

  const handleNewConversation = () => {
    setConversationId(undefined);
  };

  const handleSelectConversation = (id: number) => {
    setConversationId(id);
    setSidebarOpen(false); // Close sidebar on mobile after selection
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div className="flex items-center gap-4 sm:gap-8">
              <h1 className="text-lg sm:text-2xl font-bold text-gray-900">
                Todo AI
              </h1>
              <div className="flex gap-2 sm:gap-4">
                <Link
                  href="/dashboard"
                  className="text-sm sm:text-base text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  href="/chat"
                  className="text-sm sm:text-base text-blue-600 font-semibold border-b-2 border-blue-600"
                >
                  Chat
                </Link>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 lg:py-8">
        <div className="flex gap-4 lg:gap-6 h-[calc(100vh-8rem)] relative">
          {/* Mobile Sidebar Toggle Button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden fixed bottom-4 left-4 z-50 px-4 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <span className="text-sm font-medium">Chats</span>
          </button>

          {/* Mobile Backdrop */}
          {sidebarOpen && (
            <div
              className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Conversation Sidebar */}
          <div className={`w-80 flex-shrink-0 fixed lg:relative inset-y-0 left-0 z-40 transform transition-transform duration-300 ease-in-out lg:transform-none ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
          }`}>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-screen lg:h-full flex flex-col">
              {/* Sidebar Header */}
              <div className="px-4 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Conversations</h3>
                <button
                  onClick={handleNewConversation}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New Chat
                </button>
              </div>

              {/* Conversation List */}
              <div className="flex-1 overflow-y-auto">
                {loadingConversations ? (
                  <div className="p-4 text-center text-gray-500">Loading...</div>
                ) : conversations.length === 0 ? (
                  <div className="p-4 text-center text-gray-500 text-sm">
                    No conversations yet. Start a new chat!
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {conversations.map((conv) => (
                      <button
                        key={conv.id}
                        onClick={() => handleSelectConversation(conv.id)}
                        className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                          conversationId === conv.id ? "bg-blue-50 border-l-4 border-l-blue-600" : ""
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                          </svg>
                          <span className="text-sm font-medium text-gray-900">
                            Chat #{conv.id}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500">
                          {new Date(conv.updated_at).toLocaleString()}
                        </p>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Help Tips */}
              <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
                <h4 className="text-xs font-semibold text-gray-700 mb-2">💡 Try saying:</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• "Add buy milk"</li>
                  <li>• "Show my tasks"</li>
                  <li>• "Mark task 5 as done"</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="flex-1 min-w-0">
            <ChatInterface
              conversationId={conversationId}
              onConversationCreated={handleConversationCreated}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
