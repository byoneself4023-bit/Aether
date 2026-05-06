'use client';

import { useState } from 'react';
import axios from 'axios';
import { optimizePortfolio } from '@/lib/api/portfolio';
import { analyzePortfolio } from '@/lib/api/llm';
import type { OptimizationResult } from '@/types/portfolio';

function defaultStartDate() {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 3);
  return d.toISOString().slice(0, 10);
}

function todayDate() {
  return new Date().toISOString().slice(0, 10);
}

export function useOptimize() {
  const [selectedTickers, setSelectedTickers] = useState<string[]>(['AAPL', 'MSFT', 'GOOGL']);
  const [startDate, setStartDate] = useState(defaultStartDate);
  const [endDate, setEndDate] = useState(todayDate);
  const [strategy, setStrategy] = useState<'max_sharpe' | 'min_variance'>('max_sharpe');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [analysis, setAnalysis] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const addTicker = (ticker: string) =>
    setSelectedTickers((prev) => (prev.includes(ticker) ? prev : [...prev, ticker]));
  const removeTicker = (ticker: string) =>
    setSelectedTickers((prev) => prev.filter((t) => t !== ticker));

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
      setIsAnalyzing(true);
      try {
        const text = await analyzePortfolio(data.weights, {
          expected_return: data.metrics.expected_return,
          volatility: data.metrics.volatility,
          sharpe_ratio: data.metrics.sharpe_ratio,
        });
        setAnalysis(text);
      } catch (e) {
        console.error('AI 분석 실패:', e);
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

  return {
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
    error,
    result,
    analysis,
    isAnalyzing,
    handleOptimize,
  };
}
