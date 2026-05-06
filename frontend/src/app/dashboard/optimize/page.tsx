'use client';

import { useOptimize } from '@/hooks/useOptimize';
import OptimizeForm from '@/components/optimize/OptimizeForm';
import ResultDisplay from '@/components/optimize/ResultDisplay';

export default function OptimizePage() {
  const opt = useOptimize();

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <p className="text-zinc-400 -mt-1">종목을 선택하고 최적의 자산 배분을 찾으세요.</p>

      {opt.error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {opt.error}
        </div>
      )}

      <OptimizeForm
        selectedTickers={opt.selectedTickers}
        addTicker={opt.addTicker}
        removeTicker={opt.removeTicker}
        startDate={opt.startDate}
        setStartDate={opt.setStartDate}
        endDate={opt.endDate}
        setEndDate={opt.setEndDate}
        strategy={opt.strategy}
        setStrategy={opt.setStrategy}
        isLoading={opt.isLoading}
        onOptimize={opt.handleOptimize}
      />

      <ResultDisplay
        isLoading={opt.isLoading}
        result={opt.result}
        isAnalyzing={opt.isAnalyzing}
        analysis={opt.analysis}
      />
    </div>
  );
}
