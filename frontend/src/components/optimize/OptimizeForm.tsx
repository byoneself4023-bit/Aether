'use client';

import { Play, Loader2 } from 'lucide-react';
import TickerSearch from '@/components/portfolio/TickerSearch';

interface OptimizeFormProps {
  selectedTickers: string[];
  addTicker: (ticker: string) => void;
  removeTicker: (ticker: string) => void;
  startDate: string;
  setStartDate: (v: string) => void;
  endDate: string;
  setEndDate: (v: string) => void;
  strategy: 'max_sharpe' | 'min_variance';
  setStrategy: (v: 'max_sharpe' | 'min_variance') => void;
  isLoading: boolean;
  onOptimize: () => void;
}

export default function OptimizeForm(props: OptimizeFormProps) {
  const {
    selectedTickers,
    addTicker,
    removeTicker,
    startDate,
    setStartDate,
    endDate,
    setEndDate,
    strategy,
    setStrategy,
    isLoading,
    onOptimize,
  } = props;

  return (
    <>
      <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
        <h2 className="text-lg font-semibold text-white mb-4">종목 선택</h2>
        <TickerSearch
          selectedTickers={selectedTickers}
          onAdd={addTicker}
          onRemove={removeTicker}
          accentColor="blue"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <label htmlFor="opt-start" className="block text-sm text-zinc-400 mb-2">시작일</label>
          <input
            id="opt-start"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-blue-500 [color-scheme:dark]"
          />
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <label htmlFor="opt-end" className="block text-sm text-zinc-400 mb-2">종료일</label>
          <input
            id="opt-end"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-blue-500 [color-scheme:dark]"
          />
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <label htmlFor="strategy" className="block text-sm text-zinc-400 mb-2">전략</label>
          <select
            id="strategy"
            value={strategy}
            onChange={(e) => setStrategy(e.target.value as 'max_sharpe' | 'min_variance')}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="max_sharpe">최대 Sharpe Ratio</option>
            <option value="min_variance">최소 분산</option>
          </select>
        </div>
      </div>

      <button
        onClick={onOptimize}
        disabled={selectedTickers.length < 2 || isLoading}
        className="flex items-center gap-2 px-6 py-3 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
        {isLoading ? '최적화 중...' : '최적화 실행'}
      </button>
    </>
  );
}
