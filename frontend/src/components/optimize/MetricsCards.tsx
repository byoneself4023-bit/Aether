'use client';

import { TrendingUp, Activity, Target } from 'lucide-react';

interface MetricsCardsProps {
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
}

const formatPercent = (value: number) => (value * 100).toFixed(2) + '%';

export default function MetricsCards({ expected_return, volatility, sharpe_ratio }: MetricsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-4 h-4 text-green-400" />
          <p className="text-sm text-zinc-400">기대 수익률 (연율)</p>
        </div>
        <p className="text-2xl font-bold text-green-400">{formatPercent(expected_return)}</p>
      </div>
      <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
        <div className="flex items-center gap-2 mb-2">
          <Activity className="w-4 h-4 text-yellow-400" />
          <p className="text-sm text-zinc-400">변동성 (연율)</p>
        </div>
        <p className="text-2xl font-bold text-yellow-400">{formatPercent(volatility)}</p>
      </div>
      <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
        <div className="flex items-center gap-2 mb-2">
          <Target className="w-4 h-4 text-blue-400" />
          <p className="text-sm text-zinc-400">Sharpe Ratio</p>
        </div>
        <p className="text-2xl font-bold text-blue-400">{sharpe_ratio.toFixed(4)}</p>
      </div>
    </div>
  );
}
