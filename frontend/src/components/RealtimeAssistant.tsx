'use client';

interface Suggestion {
  type: string;
  content: string;
}

interface RealtimeAssistantProps {
  suggestions?: Suggestion[];
}

export default function RealtimeAssistant({ suggestions = [] }: RealtimeAssistantProps) {
  return (
    <div className="border rounded-lg p-4 bg-blue-50">
      <h2 className="text-lg font-semibold mb-4">실시간 어시스턴트</h2>

      <div className="space-y-3">
        {suggestions.length > 0 ? (
          suggestions.map((suggestion, idx) => (
            <div key={idx} className="bg-white p-3 rounded-lg shadow-sm">
              <span className="text-xs text-blue-600 font-medium">
                {suggestion.type}
              </span>
              <p className="text-sm mt-1">{suggestion.content}</p>
            </div>
          ))
        ) : (
          <div className="text-sm text-gray-600">
            <p className="mb-2">상담 중 실시간으로 도움을 드립니다:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>관련 정보 제안</li>
              <li>유사 사례 안내</li>
              <li>답변 템플릿 추천</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
