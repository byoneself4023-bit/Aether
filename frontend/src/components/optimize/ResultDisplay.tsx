'use client';

import { PieChart } from 'lucide-react';
import type { OptimizationResult } from '@/types/portfolio';
import MetricsCards from './MetricsCards';
import AllocationChart from './AllocationChart';
import AIAnalysisPanel from './AIAnalysisPanel';

interface ResultDisplayProps {
  isLoading: boolean;
  result: OptimizationResult | null;
  isAnalyzing: boolean;
  analysis: string;
}

export default function ResultDisplay({ isLoading, result, isAnalyzing, analysis }: ResultDisplayProps) {
  if (isLoading) return null;

  if (!result) {
    return (
      <div className="p-12 bg-zinc-900 border border-zinc-800 rounded-xl text-center">
        <PieChart className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
        <p className="text-zinc-500">최적화 결과가 여기에 표시됩니다.</p>
        <p className="text-sm text-zinc-600 mt-1">2개 이상의 종목을 선택하고 &quot;최적화 실행&quot;을 클릭하세요.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {result.warnings && result.warnings.length > 0 && (
        <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400 text-sm space-y-1">
          {result.warnings.map((w, i) => <p key={i}>{w}</p>)}
        </div>
      )}
      <MetricsCards {...result.metrics} />
      <AllocationChart weights={result.weights} />
      <AIAnalysisPanel isAnalyzing={isAnalyzing} analysis={analysis} />
      {result.failed_tickers && result.failed_tickers.length > 0 && (
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400">
            데이터 수집 실패: <span className="text-red-400">{result.failed_tickers.join(', ')}</span>
          </p>
        </div>
      )}
    </div>
  );
}
