'use client';

import type { BacktestResult } from '@/types/portfolio';

interface MetricsGridProps {
  result: BacktestResult;
}

const formatPercent = (value: number) => (value * 100).toFixed(2) + '%';

export default function MetricsGrid({ result }: MetricsGridProps) {
  const m = result.metrics;
  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">누적 수익률</p>
          <p className={`text-xl font-bold ${m.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatPercent(m.total_return)}
          </p>
        </div>
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">연환산 수익률</p>
          <p className={`text-xl font-bold ${m.annual_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatPercent(m.annual_return)}
          </p>
        </div>
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">Sharpe Ratio</p>
          <p className="text-xl font-bold text-blue-400">{m.sharpe_ratio.toFixed(4)}</p>
        </div>
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">최대 낙폭 (MDD)</p>
          <p className="text-xl font-bold text-red-400">{formatPercent(m.max_drawdown)}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">연환산 변동성</p>
          <p className="text-lg font-bold text-yellow-400">{formatPercent(m.annual_volatility)}</p>
        </div>
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">칼마 비율</p>
          <p className="text-lg font-bold text-zinc-300">{m.calmar_ratio.toFixed(4)}</p>
        </div>
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">승률</p>
          <p className="text-lg font-bold text-zinc-300">{formatPercent(m.win_rate)}</p>
        </div>
        <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
          <p className="text-sm text-zinc-400 mb-1">리밸런싱 횟수</p>
          <p className="text-lg font-bold text-zinc-300">{result.rebalance_count}회</p>
        </div>
      </div>
    </>
  );
}
