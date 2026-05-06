'use client';

import { TrendingUp } from 'lucide-react';
import type { BacktestResult } from '@/types/portfolio';
import MetricsGrid from './MetricsGrid';
import PerformanceChart from './PerformanceChart';

interface ResultsViewProps {
  result: BacktestResult | null;
}

export default function ResultsView({ result }: ResultsViewProps) {
  if (!result) {
    return (
      <div className="p-12 bg-zinc-900 border border-zinc-800 rounded-xl text-center">
        <TrendingUp className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
        <p className="text-zinc-500">백테스트 결과가 여기에 표시됩니다.</p>
        <p className="text-sm text-zinc-600 mt-1">종목을 선택하고 &quot;백테스트 실행&quot;을 클릭하세요.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <MetricsGrid result={result} />
      <PerformanceChart data={result.portfolio_values} />
    </div>
  );
}
