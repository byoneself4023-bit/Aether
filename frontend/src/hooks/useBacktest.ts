'use client';

import { useState } from 'react';
import axios from 'axios';
import { runBacktest } from '@/lib/api/portfolio';
import type { BacktestResult } from '@/types/portfolio';

function defaultStartDate() {
  const d = new Date();
  d.setFullYear(d.getFullYear() - 5);
  return d.toISOString().slice(0, 10);
}

function todayDate() {
  return new Date().toISOString().slice(0, 10);
}

export type BacktestStrategy = 'max_sharpe' | 'min_variance' | 'equal_weight';

export function useBacktest() {
  const [selectedTickers, setSelectedTickers] = useState<string[]>(['AAPL', 'MSFT', 'GOOGL']);
  const [strategy, setStrategy] = useState<BacktestStrategy>('max_sharpe');
  const [startDate, setStartDate] = useState(defaultStartDate);
  const [endDate, setEndDate] = useState(todayDate);
  const [rebalanceEvery, setRebalanceEvery] = useState(63);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<BacktestResult | null>(null);

  const addTicker = (ticker: string) =>
    setSelectedTickers((prev) => (prev.includes(ticker) ? prev : [...prev, ticker]));
  const removeTicker = (ticker: string) =>
    setSelectedTickers((prev) => prev.filter((t) => t !== ticker));

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

  return {
    selectedTickers,
    addTicker,
    removeTicker,
    strategy,
    setStrategy,
    startDate,
    setStartDate,
    endDate,
    setEndDate,
    rebalanceEvery,
    setRebalanceEvery,
    isLoading,
    error,
    result,
    handleBacktest,
  };
}
