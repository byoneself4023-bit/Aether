'use client';

import { Check, Loader2, Clock } from 'lucide-react';

interface ProcessingStepsProps {
  steps: {
    classify: 'idle' | 'loading' | 'done';
    search: 'idle' | 'loading' | 'done';
    generate: 'idle' | 'loading' | 'done';
  };
  results?: {
    domain?: string;
    confidence?: number;
    similarCount?: number;
  };
}

export function ProcessingSteps({ steps, results }: ProcessingStepsProps) {
  const getStepStyle = (status: 'idle' | 'loading' | 'done') => {
    switch (status) {
      case 'done':
        return 'bg-green-500 text-white border-green-500';
      case 'loading':
        return 'bg-blue-500 text-white border-blue-500 animate-pulse';
      default:
        return 'bg-white text-slate-400 border-slate-200';
    }
  };

  const getLineStyle = (status: 'idle' | 'loading' | 'done') => {
    return status === 'done' ? 'bg-green-500' : 'bg-slate-200';
  };

  const getIcon = (status: 'idle' | 'loading' | 'done') => {
    switch (status) {
      case 'done':
        return <Check className="h-4 w-4" />;
      case 'loading':
        return <Loader2 className="h-4 w-4 animate-spin" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const isActive = steps.classify !== 'idle' || steps.search !== 'idle' || steps.generate !== 'idle';

  if (!isActive) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
      {/* 스텝 인디케이터 */}
      <div className="flex items-center justify-between">
        {/* Step 1: 분류 */}
        <div className="flex flex-col items-center flex-1">
          <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all ${getStepStyle(steps.classify)}`}>
            {getIcon(steps.classify)}
          </div>
          <span className="mt-2 text-sm font-medium text-slate-700">분류</span>
          {steps.classify === 'done' && results?.domain && (
            <div className="mt-1 text-center">
              <span className="text-xs font-semibold text-blue-600">{results.domain}</span>
              {results.confidence && (
                <span className="text-xs text-green-600 ml-1">
                  {(results.confidence * 100).toFixed(1)}%
                </span>
              )}
            </div>
          )}
        </div>

        {/* Line 1-2 */}
        <div className={`h-1 flex-1 mx-2 rounded transition-all ${getLineStyle(steps.search)}`} />

        {/* Step 2: 유사 검색 */}
        <div className="flex flex-col items-center flex-1">
          <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all ${getStepStyle(steps.search)}`}>
            {getIcon(steps.search)}
          </div>
          <span className="mt-2 text-sm font-medium text-slate-700">유사 검색</span>
          {steps.search === 'done' && results?.similarCount !== undefined && (
            <span className="mt-1 text-xs text-slate-500">{results.similarCount}건 발견</span>
          )}
        </div>

        {/* Line 2-3 */}
        <div className={`h-1 flex-1 mx-2 rounded transition-all ${getLineStyle(steps.generate)}`} />

        {/* Step 3: 답변 생성 */}
        <div className="flex flex-col items-center flex-1">
          <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center transition-all ${getStepStyle(steps.generate)}`}>
            {getIcon(steps.generate)}
          </div>
          <span className="mt-2 text-sm font-medium text-slate-700">답변 생성</span>
          {steps.generate === 'done' && (
            <span className="mt-1 text-xs text-green-600">완료!</span>
          )}
        </div>
      </div>
    </div>
  );
}
