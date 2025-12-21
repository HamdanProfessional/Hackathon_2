"use client";

import { useEffect, useState } from 'react';

export default function ChatDebug() {
  const [debugInfo, setDebugInfo] = useState<any>({});

  useEffect(() => {
    // Collect debug information
    const info = {
      userAgent: navigator.userAgent,
      localStorage: {
        token: !!localStorage.getItem('todo_access_token'),
        keys: Object.keys(localStorage)
      },
      window: {
        speechRecognition: !!(window.SpeechRecognition || window.webkitSpeechRecognition),
        speechSynthesis: !!window.speechSynthesis,
      },
      env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
        NODE_ENV: process.env.NODE_ENV,
      },
      time: new Date().toISOString()
    };
    setDebugInfo(info);
  }, []);

  return (
    <div className="p-4 bg-slate-900 text-slate-100 font-mono text-xs">
      <h3 className="text-lg font-bold mb-4 text-blue-400">Chat Debug Information</h3>
      <pre className="whitespace-pre-wrap">{JSON.stringify(debugInfo, null, 2)}</pre>

      <div className="mt-4 space-y-2">
        <button
          onClick={() => {
            console.log('Debug info:', debugInfo);
            alert('Debug info logged to console');
          }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
        >
          Log to Console
        </button>

        <button
          onClick={() => {
            localStorage.clear();
            window.location.reload();
          }}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded ml-2"
        >
          Clear Storage & Reload
        </button>
      </div>
    </div>
  );
}