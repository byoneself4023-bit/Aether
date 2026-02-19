'use client';

import { useState } from 'react';
import { TrendingUp, Play, Loader2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { runBacktest } from '@/lib/api/portfolio';
import type { BacktestResult } from '@/types/portfolio';
import TickerSearch from '@/components/portfolio/TickerSearch';
import axios from 'axios';

function defaultStartDate() {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 5);
  return d.toISOString().slice(0, 10);
}

function todayDate() {
  return new Date().toISOString().slice(0, 10);
}

export default function BacktestPage() {
  const [selectedTickers, setSelectedTickers] = useState<string[]>(['AAPL', 'MSFT', 'GOOGL']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [strategy, setStrategy] = useState<'max_sharpe' | 'min_variance' | 'equal_weight'>('max_sharpe');
  const [startDate, setStartDate] = useState(defaultStartDate);
  const [endDate, setEndDate] = useState(todayDate);
  const [rebalanceEvery, setRebalanceEvery] = useState(63);
  const [result, setResult] = useState<BacktestResult | null>(null);

  const addTicker = (ticker: string) => {
    setSelectedTickers((prev) => prev.includes(ticker) ? prev : [...prev, ticker]);
  };
  const removeTicker = (ticker: string) => {
    setSelectedTickers((prev) => prev.filter((t) => t !== ticker));
  };

  const handleBacktest = async () => {
    if (selectedTickers.length < 2) {
      setError('2개 이상의 종목을 선택해주세요.');
      return;
    }
    setError('');
    setResult(null);
    setIsLoading(true);

    try {
      const data = await runBacktest({
        tickers: selectedTickers,
        strategy,
        start_date: startDate,
        end_date: endDate,
        rebalance_every: rebalanceEvery,
      });
      setResult(data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === 'string' ? detail : err.message);
      } else {
        setError('백테스트 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formatPercent = (value: number) => (value * 100).toFixed(2) + '%';

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <p className="text-zinc-400">과거 데이터로 포트폴리오 전략을 검증하세요.</p>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Ticker Selection */}
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <h2 className="text-lg font-semibold text-white mb-4">종목 선택</h2>
          <TickerSearch
            selectedTickers={selectedTickers}
            onAdd={addTicker}
            onRemove={removeTicker}
            accentColor="green"
          />
        </div>

        {/* Settings */}
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-white mb-2">설정</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="bt-strategy" className="block text-sm text-zinc-400 mb-2">전략</label>
              <select id="bt-strategy" value={strategy}
                onChange={(e) => setStrategy(e.target.value as 'max_sharpe' | 'min_variance' | 'equal_weight')}
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

      {/* Run Button */}
      <button onClick={handleBacktest} disabled={selectedTickers.length < 2 || isLoading}
        className="flex items-center gap-2 px-6 py-3 bg-green-500 text-white font-semibold rounded-xl hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
        {isLoading ? '실행 중...' : '백테스트 실행'}
      </button>

      {/* Results */}
      {result ? (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">누적 수익률</p>
              <p className={`text-xl font-bold ${result.metrics.total_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatPercent(result.metrics.total_return)}
              </p>
            </div>
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">연환산 수익률</p>
              <p className={`text-xl font-bold ${result.metrics.annual_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatPercent(result.metrics.annual_return)}
              </p>
            </div>
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">Sharpe Ratio</p>
              <p className="text-xl font-bold text-blue-400">{result.metrics.sharpe_ratio.toFixed(4)}</p>
            </div>
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">최대 낙폭 (MDD)</p>
              <p className="text-xl font-bold text-red-400">{formatPercent(result.metrics.max_drawdown)}</p>
            </div>
          </div>

          {result.portfolio_values.length > 0 && (
            <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
              <h2 className="text-lg font-semibold text-white mb-4">포트폴리오 가치</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={result.portfolio_values}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="date" stroke="#71717a" tick={{ fontSize: 11 }}
                    tickFormatter={(d: string) => d.slice(0, 7)} interval="preserveStartEnd" />
                  <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
                    labelStyle={{ color: '#a1a1aa' }}
                    itemStyle={{ color: '#3b82f6' }}
                  />
                  <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">연환산 변동성</p>
              <p className="text-lg font-bold text-yellow-400">{formatPercent(result.metrics.annual_volatility)}</p>
            </div>
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">칼마 비율</p>
              <p className="text-lg font-bold text-zinc-300">{result.metrics.calmar_ratio.toFixed(4)}</p>
            </div>
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">승률</p>
              <p className="text-lg font-bold text-zinc-300">{formatPercent(result.metrics.win_rate)}</p>
            </div>
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400 mb-1">리밸런싱 횟수</p>
              <p className="text-lg font-bold text-zinc-300">{result.rebalance_count}회</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 bg-zinc-900 border border-zinc-800 rounded-xl text-center">
          <TrendingUp className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <p className="text-zinc-500">백테스트 결과가 여기에 표시됩니다.</p>
          <p className="text-sm text-zinc-600 mt-1">종목을 선택하고 &quot;백테스트 실행&quot;을 클릭하세요.</p>
        </div>
      )}
    </div>
  );
}
