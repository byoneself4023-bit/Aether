'use client';

import { useState, useRef, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { SP500_TICKERS } from '@/lib/data/sp500';
import { DEFAULT_TICKERS } from '@/lib/utils/constants';

interface TickerSearchProps {
  selectedTickers: string[];
  onAdd: (ticker: string) => void;
  onRemove: (ticker: string) => void;
  accentColor?: string; // 'blue' | 'green'
}

export default function TickerSearch({
  selectedTickers,
  onAdd,
  onRemove,
  accentColor = 'blue',
}: TickerSearchProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [highlightIdx, setHighlightIdx] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const accent = accentColor === 'green'
    ? { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30', focus: 'focus:border-green-500' }
    : { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30', focus: 'focus:border-blue-500' };

  // Filter results
  const results = query.trim().length > 0
    ? SP500_TICKERS.filter((t) => {
        const q = query.toUpperCase();
        return t.symbol.includes(q) || t.name.toUpperCase().includes(q);
      }).slice(0, 8)
    : [];

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Reset highlight when results change
  useEffect(() => {
    setHighlightIdx(0);
  }, [query]);

  const selectTicker = (symbol: string) => {
    if (!selectedTickers.includes(symbol)) {
      onAdd(symbol);
    }
    setQuery('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || results.length === 0) {
      if (e.key === 'ArrowDown' && query.trim().length > 0) {
        setIsOpen(true);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightIdx((prev) => Math.min(prev + 1, results.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightIdx((prev) => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        selectTicker(results[highlightIdx].symbol);
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  };

  const toggleDefaultTicker = (ticker: string) => {
    if (selectedTickers.includes(ticker)) {
      onRemove(ticker);
    } else {
      onAdd(ticker);
    }
  };

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div ref={containerRef} className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => query.trim().length > 0 && setIsOpen(true)}
            onKeyDown={handleKeyDown}
            placeholder="종목 검색 (예: TSLA, Apple)"
            className={`w-full pl-10 pr-4 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none ${accent.focus} transition-colors text-sm`}
          />
        </div>

        {/* Dropdown */}
        {isOpen && results.length > 0 && (
          <div className="absolute z-50 w-full mt-1 bg-zinc-800 border border-zinc-700 rounded-lg shadow-xl overflow-hidden">
            {results.map((item, idx) => {
              const isSelected = selectedTickers.includes(item.symbol);
              return (
                <button
                  key={item.symbol}
                  onClick={() => selectTicker(item.symbol)}
                  disabled={isSelected}
                  className={`w-full px-4 py-2.5 text-left text-sm flex items-center justify-between transition-colors ${
                    idx === highlightIdx ? 'bg-zinc-700' : 'hover:bg-zinc-750'
                  } ${isSelected ? 'opacity-50 cursor-default' : 'cursor-pointer'}`}
                >
                  <span>
                    <span className="font-medium text-white">{item.symbol}</span>
                    <span className="text-zinc-400 ml-2">{item.name}</span>
                  </span>
                  {isSelected && (
                    <span className="text-xs text-zinc-500">선택됨</span>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Tickers as Tags */}
      {selectedTickers.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedTickers.map((ticker) => (
            <span
              key={ticker}
              className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium ${accent.bg} ${accent.text} border ${accent.border}`}
            >
              {ticker}
              <button
                onClick={() => onRemove(ticker)}
                className="hover:text-white transition-colors"
                aria-label={`${ticker} 제거`}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Popular Tickers */}
      <div>
        <p className="text-xs text-zinc-500 mb-2">인기 종목</p>
        <div className="flex flex-wrap gap-1.5">
          {DEFAULT_TICKERS.map((ticker) => (
            <button
              key={ticker}
              onClick={() => toggleDefaultTicker(ticker)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                selectedTickers.includes(ticker)
                  ? `${accent.bg} ${accent.text} border ${accent.border}`
                  : 'bg-zinc-800 text-zinc-400 border border-zinc-700 hover:border-zinc-600'
              }`}
            >
              {ticker}
            </button>
          ))}
        </div>
      </div>

      <p className="text-sm text-zinc-500">
        선택됨: {selectedTickers.length}개 종목
      </p>
    </div>
  );
}
