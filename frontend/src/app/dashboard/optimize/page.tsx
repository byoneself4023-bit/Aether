'use client';

import { useState } from 'react';
import { PieChart, Play, Loader2, Bot, TrendingUp, Activity, Target } from 'lucide-react';
import { PieChart as RechartsPie, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import ReactMarkdown from 'react-markdown';
import { CHART_COLORS } from '@/lib/utils/constants';
import { optimizePortfolio } from '@/lib/api/portfolio';
import { analyzePortfolio } from '@/lib/api/llm';
import type { OptimizationResult } from '@/types/portfolio';
import TickerSearch from '@/components/portfolio/TickerSearch';
import axios from 'axios';

function defaultStartDate() {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 3);
  return d.toISOString().slice(0, 10);
}

function todayDate() {
  return new Date().toISOString().slice(0, 10);
}

export default function OptimizePage() {
  const [selectedTickers, setSelectedTickers] = useState<string[]>(['AAPL', 'MSFT', 'GOOGL']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [startDate, setStartDate] = useState(defaultStartDate);
  const [endDate, setEndDate] = useState(todayDate);
  const [strategy, setStrategy] = useState<'max_sharpe' | 'min_variance'>('max_sharpe');
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [analysis, setAnalysis] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const addTicker = (ticker: string) => {
    setSelectedTickers((prev) => prev.includes(ticker) ? prev : [...prev, ticker]);
  };
  const removeTicker = (ticker: string) => {
    setSelectedTickers((prev) => prev.filter((t) => t !== ticker));
  };

  const handleOptimize = async () => {
    if (selectedTickers.length < 2) return;
    setError('');
    setResult(null);
    setAnalysis('');
    setIsLoading(true);

    try {
      const data = await optimizePortfolio({
        tickers: selectedTickers,
        strategy,
        start_date: startDate,
        end_date: endDate,
        include_frontier: false,
      });
      setResult(data);

      // AI 분석 (실패해도 최적화 결과는 유지)
      setIsAnalyzing(true);
      try {
        const text = await analyzePortfolio(data.weights, {
          expected_return: data.metrics.expected_return,
          volatility: data.metrics.volatility,
          sharpe_ratio: data.metrics.sharpe_ratio,
        });
        setAnalysis(text);
      } catch {
        // 분석 실패는 조용히 무시
      } finally {
        setIsAnalyzing(false);
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === 'string' ? detail : err.message);
      } else {
        setError('최적화 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formatPercent = (value: number) => (value * 100).toFixed(2) + '%';

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <p className="text-zinc-400">종목을 선택하고 최적의 자산 배분을 찾으세요.</p>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Ticker Selection */}
      <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
        <h2 className="text-lg font-semibold text-white mb-4">종목 선택</h2>
        <TickerSearch
          selectedTickers={selectedTickers}
          onAdd={addTicker}
          onRemove={removeTicker}
          accentColor="blue"
        />
      </div>

      {/* Settings */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <label htmlFor="opt-start" className="block text-sm text-zinc-400 mb-2">시작일</label>
          <input id="opt-start" type="date" value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-blue-500 [color-scheme:dark]" />
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <label htmlFor="opt-end" className="block text-sm text-zinc-400 mb-2">종료일</label>
          <input id="opt-end" type="date" value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-blue-500 [color-scheme:dark]" />
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <label htmlFor="strategy" className="block text-sm text-zinc-400 mb-2">전략</label>
          <select id="strategy" value={strategy} onChange={(e) => setStrategy(e.target.value as 'max_sharpe' | 'min_variance')}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-blue-500">
            <option value="max_sharpe">최대 Sharpe Ratio</option>
            <option value="min_variance">최소 분산</option>
          </select>
        </div>
      </div>

      {/* Run Button */}
      <button onClick={handleOptimize} disabled={selectedTickers.length < 2 || isLoading}
        className="flex items-center gap-2 px-6 py-3 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
        {isLoading ? '최적화 중...' : '최적화 실행'}
      </button>

      {/* Skeleton Loading */}
      {isLoading && (
        <div className="space-y-6 animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[0, 1, 2].map((i) => (
              <div key={i} className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
                <div className="h-4 w-24 bg-zinc-800 rounded mb-3" />
                <div className="h-8 w-32 bg-zinc-800 rounded" />
              </div>
            ))}
          </div>
          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
            <div className="h-5 w-20 bg-zinc-800 rounded mb-4" />
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="w-full md:w-1/2 flex items-center justify-center h-64">
                <div className="w-48 h-48 rounded-full border-[20px] border-zinc-800" />
              </div>
              <div className="w-full md:w-1/2 space-y-3">
                {[0, 1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-zinc-800" />
                    <div className="h-4 w-12 bg-zinc-800 rounded" />
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full" />
                    <div className="h-4 w-14 bg-zinc-800 rounded" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {!isLoading && result ? (
        <div className="space-y-6">
          {result.warnings && result.warnings.length > 0 && (
            <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400 text-sm space-y-1">
              {result.warnings.map((w, i) => <p key={i}>{w}</p>)}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <p className="text-sm text-zinc-400">기대 수익률 (연율)</p>
              </div>
              <p className="text-2xl font-bold text-green-400">{formatPercent(result.metrics.expected_return)}</p>
            </div>
            <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4 text-yellow-400" />
                <p className="text-sm text-zinc-400">변동성 (연율)</p>
              </div>
              <p className="text-2xl font-bold text-yellow-400">{formatPercent(result.metrics.volatility)}</p>
            </div>
            <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-blue-400" />
                <p className="text-sm text-zinc-400">Sharpe Ratio</p>
              </div>
              <p className="text-2xl font-bold text-blue-400">{result.metrics.sharpe_ratio.toFixed(4)}</p>
            </div>
          </div>

          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
            <h2 className="text-lg font-semibold text-white mb-4">최적 비중</h2>
            {(() => {
              const chartData = Object.entries(result.weights)
                .filter(([, w]) => w > 0.001)
                .sort(([, a], [, b]) => b - a)
                .map(([ticker, weight]) => ({ name: ticker, value: weight }));
              const allEntries = Object.entries(result.weights)
                .sort(([, a], [, b]) => b - a);
              return (
                <div className="flex flex-col md:flex-row items-center gap-6">
                  <div className="w-full md:w-1/2 h-64 relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPie>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          innerRadius="60%"
                          outerRadius="80%"
                          dataKey="value"
                          stroke="none"
                        >
                          {chartData.map((_, idx) => (
                            <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip
                          formatter={(value: number | undefined) => value != null ? formatPercent(value) : ''}
                          contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
                          itemStyle={{ color: '#e4e4e7' }}
                        />
                      </RechartsPie>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-white">{chartData.length}</p>
                        <p className="text-xs text-zinc-500">종목</p>
                      </div>
                    </div>
                  </div>
                  <div className="w-full md:w-1/2 space-y-2">
                    {allEntries.map(([ticker, weight]) => {
                      const chartIdx = chartData.findIndex((d) => d.name === ticker);
                      const isZero = weight <= 0.001;
                      return (
                        <div key={ticker} className="flex items-center gap-3">
                          <span
                            className="w-3 h-3 rounded-full flex-shrink-0"
                            style={{ backgroundColor: isZero ? '#3f3f46' : CHART_COLORS[chartIdx % CHART_COLORS.length] }}
                          />
                          <span className={`text-sm font-medium w-14 ${isZero ? 'text-zinc-600' : 'text-zinc-300'}`}>{ticker}</span>
                          <div className="flex-1 bg-zinc-800 rounded-full h-1.5">
                            {!isZero && (
                              <div
                                className="h-full rounded-full"
                                style={{
                                  width: `${Math.max(weight * 100, 2)}%`,
                                  backgroundColor: CHART_COLORS[chartIdx % CHART_COLORS.length],
                                }}
                              />
                            )}
                          </div>
                          <span className={`text-sm w-16 text-right ${isZero ? 'text-zinc-600' : 'text-zinc-400'}`}>
                            {formatPercent(weight)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })()}
          </div>

          {/* AI 분석 */}
          {(isAnalyzing || analysis) && (
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
                  <ReactMarkdown>{analysis}</ReactMarkdown>
                </div>
              )}
            </div>
          )}

          {result.failed_tickers && result.failed_tickers.length > 0 && (
            <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl">
              <p className="text-sm text-zinc-400">
                데이터 수집 실패: <span className="text-red-400">{result.failed_tickers.join(', ')}</span>
              </p>
            </div>
          )}
        </div>
      ) : !isLoading && (
        <div className="p-12 bg-zinc-900 border border-zinc-800 rounded-xl text-center">
          <PieChart className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <p className="text-zinc-500">최적화 결과가 여기에 표시됩니다.</p>
          <p className="text-sm text-zinc-600 mt-1">2개 이상의 종목을 선택하고 &quot;최적화 실행&quot;을 클릭하세요.</p>
        </div>
      )}
    </div>
  );
}
