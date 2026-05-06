'use client';

import { useBacktest } from '@/hooks/useBacktest';
import BacktestForm from '@/components/backtest/BacktestForm';
import ResultsView from '@/components/backtest/ResultsView';

export default function BacktestPage() {
  const bt = useBacktest();

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <p className="text-zinc-400 -mt-1">과거 데이터로 포트폴리오 전략을 검증하세요.</p>

      {bt.error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {bt.error}
        </div>
      )}

      <BacktestForm
        selectedTickers={bt.selectedTickers}
        addTicker={bt.addTicker}
        removeTicker={bt.removeTicker}
        strategy={bt.strategy}
        setStrategy={bt.setStrategy}
        startDate={bt.startDate}
        setStartDate={bt.setStartDate}
        endDate={bt.endDate}
        setEndDate={bt.setEndDate}
        rebalanceEvery={bt.rebalanceEvery}
        setRebalanceEvery={bt.setRebalanceEvery}
        isLoading={bt.isLoading}
        onRun={bt.handleBacktest}
      />

      <ResultsView result={bt.result} />
    </div>
  );
}
