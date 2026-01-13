'use client';

import { useState } from 'react';
import RealtimeAssistant from '@/components/RealtimeAssistant';

export default function ConsultationPage() {
  const [messages, setMessages] = useState<Array<{role: string; content: string}>>([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');

    // TODO: API 호출 및 응답 처리
  };

  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-6">실시간 상담</h1>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="border rounded-lg p-4 h-96 overflow-y-auto mb-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-2 p-2 rounded ${
                  msg.role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'
                } max-w-[80%]`}
              >
                {msg.content}
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="메시지를 입력하세요..."
              className="flex-1 p-3 border rounded-lg"
            />
            <button
              onClick={handleSend}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              전송
            </button>
          </div>
        </div>

        <div className="col-span-1">
          <RealtimeAssistant />
        </div>
      </div>
    </main>
  );
}
