'use client';

import { Play, Loader2 } from 'lucide-react';
import TickerSearch from '@/components/portfolio/TickerSearch';
import type { BacktestStrategy } from '@/hooks/useBacktest';

interface BacktestFormProps {
  selectedTickers: string[];
  addTicker: (ticker: string) => void;
  removeTicker: (ticker: string) => void;
  strategy: BacktestStrategy;
  setStrategy: (v: BacktestStrategy) => void;
  startDate: string;
  setStartDate: (v: string) => void;
  endDate: string;
  setEndDate: (v: string) => void;
  rebalanceEvery: number;
  setRebalanceEvery: (v: number) => void;
  isLoading: boolean;
  onRun: () => void;
}

export default function BacktestForm(props: BacktestFormProps) {
  const {
    selectedTickers, addTicker, removeTicker,
    strategy, setStrategy,
    startDate, setStartDate, endDate, setEndDate,
    rebalanceEvery, setRebalanceEvery,
    isLoading, onRun,
  } = props;

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <h2 className="text-lg font-semibold text-white mb-4">종목 선택</h2>
          <TickerSearch
            selectedTickers={selectedTickers}
            onAdd={addTicker}
            onRemove={removeTicker}
            accentColor="green"
          />
        </div>

        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-white mb-2">설정</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="bt-strategy" className="block text-sm text-zinc-400 mb-2">전략</label>
              <select id="bt-strategy" value={strategy}
                onChange={(e) => setStrategy(e.target.value as BacktestStrategy)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-green-500">
                <option value="max_sharpe">최대 Sharpe</option>
                <option value="min_variance">최소 분산</option>
                <option value="equal_weight">동일 비중</option>
              </select>
            </div>
            <div>
              <label htmlFor="bt-rebalance" className="block text-sm text-zinc-400 mb-2">리밸런싱</label>
              <select id="bt-rebalance" value={rebalanceEvery}
                onChange={(e) => setRebalanceEvery(Number(e.target.value))}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-green-500">
                <option value={21}>월간 (21일)</option>
                <option value={63}>분기 (63일)</option>
                <option value={126}>반기 (126일)</option>
                <option value={252}>연간 (252일)</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="bt-start" className="block text-sm text-zinc-400 mb-2">시작일</label>
              <input id="bt-start" type="date" value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-green-500 [color-scheme:dark]" />
            </div>
            <div>
              <label htmlFor="bt-end" className="block text-sm text-zinc-400 mb-2">종료일</label>
              <input id="bt-end" type="date" value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-green-500 [color-scheme:dark]" />
            </div>
          </div>
        </div>
      </div>

      <button onClick={onRun} disabled={selectedTickers.length < 2 || isLoading}
        className="flex items-center gap-2 px-6 py-3 bg-green-500 text-white font-semibold rounded-xl hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
        {isLoading ? '실행 중...' : '백테스트 실행'}
      </button>
    </>
  );
}
