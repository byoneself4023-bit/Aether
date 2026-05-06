'use client';

import { Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { cleanAnalysisText } from '@/lib/utils/text';

interface AIAnalysisPanelProps {
  isAnalyzing: boolean;
  analysis: string;
}

export default function AIAnalysisPanel({ isAnalyzing, analysis }: AIAnalysisPanelProps) {
  if (!isAnalyzing && !analysis) return null;

  return (
    <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 rounded-lg bg-blue-500/20 flex items-center justify-center">
          <Bot className="w-4 h-4 text-blue-400" />
        </div>
        <h2 className="text-lg font-semibold text-white">AI 분석</h2>
      </div>
      {isAnalyzing ? (
        <div className="flex items-center gap-3 text-zinc-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">AI가 결과를 분석하고 있습니다...</span>
        </div>
      ) : (
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{cleanAnalysisText(analysis)}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
