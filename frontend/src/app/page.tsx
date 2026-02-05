'use client';

import AppLayout from '@/components/layout/AppLayout';
import { useState, useCallback } from 'react';
import { usePipeline, type StepStatus } from '@/hooks/usePipeline';
import { submitFeedback } from '@/services/feedbackService';
import { useToastContext } from '@/components/common/ToastProvider';
import {
  Send, Loader2, RotateCcw, Copy, Check,
  ThumbsUp, ThumbsDown, Search, Tag, FileText,
  Sparkles, MessageSquare, GitCompareArrows, Clock,
} from 'lucide-react';

export default function HomePage() {
  const toast = useToastContext();
  const [query, setQuery] = useState('');
  const [copied, setCopied] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<'positive' | 'negative' | null>(null);

  const {
    isProcessing,
    steps,
    classification,
    similarComplaints,
    aiAnswer,
    ollamaResult,
    geminiResult,
    executeLegacy,
    regenerate,
  } = usePipeline();

  const isIdle = steps.classify === 'idle' && steps.search === 'idle' && steps.generate === 'idle';
  const allDone = steps.classify === 'done' && steps.search === 'done' && steps.generate === 'done';

  const handleSubmit = useCallback(async () => {
    if (!query.trim() || isProcessing) return;
    setFeedbackSent(null);
    await executeLegacy(query, compareMode);
  }, [query, isProcessing, compareMode, executeLegacy]);

  const handleRegenerate = useCallback(async () => {
    if (!query.trim()) return;
    await regenerate(query, compareMode);
  }, [query, compareMode, regenerate]);

  const handleCopy = useCallback((text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.info('클립보드에 복사되었습니다');
    setTimeout(() => setCopied(false), 2000);
  }, [toast]);

  const handleFeedback = useCallback(async (rating: 'positive' | 'negative') => {
    if (!aiAnswer || feedbackSent) return;
    try {
      await submitFeedback({
        query,
        answer: aiAnswer,
        rating: rating === 'positive' ? 1 : 0,
        domain: classification?.domain,
        category: classification?.category,
      });
      setFeedbackSent(rating);
      toast.success('피드백이 저장되었습니다');
    } catch {
      toast.error('피드백 저장에 실패했습니다');
    }
  }, [query, aiAnswer, classification, feedbackSent]);

  const pipelineSteps: Array<{ id: keyof typeof steps; label: string; icon: typeof Tag }> = [
    { id: 'classify', label: '분류', icon: Tag },
    { id: 'search', label: '검색', icon: Search },
    { id: 'generate', label: '생성', icon: Sparkles },
  ];

  const getStepStyle = (status: StepStatus) => {
    if (status === 'done') return 'bg-green-500/10 text-green-400 border border-green-500/20';
    if (status === 'loading') return 'bg-blue-500/10 text-blue-400 border border-blue-500/20';
    return 'bg-zinc-900 text-zinc-500 border border-zinc-800';
  };

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-500">
        {/* Input Card */}
        <div className={`bg-zinc-900 border rounded-xl p-5 transition-all ${isProcessing ? 'border-blue-500/30 pulse-glow' : 'border-zinc-800 hover:border-zinc-700'}`}>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-zinc-400">민원 내용 입력</label>
            <button
              onClick={() => setCompareMode(!compareMode)}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg transition-all border ${
                compareMode
                  ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                  : 'bg-zinc-800 text-zinc-500 border-zinc-700 hover:text-zinc-300'
              }`}
            >
              <GitCompareArrows className="w-3.5 h-3.5" />
              모델 비교
            </button>
          </div>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="민원 내용을 입력해주세요... (Enter로 전송, Shift+Enter로 줄바꿈)"
            rows={3}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all resize-none text-sm"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
          />
          <div className="flex justify-end mt-3">
            <button
              onClick={handleSubmit}
              disabled={!query.trim() || isProcessing}
              className="flex items-center gap-2 px-5 py-2.5 bg-blue-500 text-white text-sm font-bold rounded-lg hover:bg-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              {isProcessing ? '처리 중...' : '분석 요청'}
            </button>
          </div>
        </div>

        {/* Pipeline Progress */}
        {!isIdle && (
          <div className="flex items-center gap-3 px-2">
            {pipelineSteps.map((s, i) => (
              <div key={s.id} className="flex items-center gap-3 flex-1">
                <div className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${getStepStyle(steps[s.id])}`}>
                  {steps[s.id] === 'done' ? <Check className="w-4 h-4" /> :
                   steps[s.id] === 'loading' ? <Loader2 className="w-4 h-4 animate-spin" /> :
                   <s.icon className="w-4 h-4" />}
                  {s.label}
                </div>
                {i < pipelineSteps.length - 1 && (
                  <div className={`flex-1 h-px transition-all ${steps[s.id] === 'done' ? 'bg-green-500/30' : 'bg-zinc-800'}`} />
                )}
              </div>
            ))}
          </div>
        )}

        {/* Results Grid */}
        {!isIdle && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Classification */}
              {classification && (
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
                  <h3 className="text-sm font-bold text-zinc-400 mb-3 flex items-center gap-2">
                    <Tag className="w-4 h-4" /> 분류 결과
                  </h3>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-3 py-1 bg-blue-500/10 text-blue-400 text-sm font-medium rounded-lg border border-blue-500/20">
                        {classification.domain}
                      </span>
                      {classification.category && (
                        <span className="px-3 py-1 bg-zinc-800 text-zinc-300 text-sm rounded-lg border border-zinc-700">
                          {classification.category}
                        </span>
                      )}
                    </div>
                    {classification.confidence > 0 && (
                      <div className="flex items-center gap-2 mt-2">
                        <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500 rounded-full transition-all duration-700"
                            style={{ width: `${classification.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-zinc-500 w-12 text-right">
                          {(classification.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Similar Cases */}
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
                <h3 className="text-sm font-bold text-zinc-400 mb-3 flex items-center gap-2">
                  <FileText className="w-4 h-4" /> 유사 민원
                  {similarComplaints.length > 0 && (
                    <span className="text-xs text-zinc-600 ml-auto">{similarComplaints.length}건</span>
                  )}
                </h3>
                {similarComplaints.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {similarComplaints.map((c, i) => (
                      <div key={i} className="group bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-3 hover:bg-zinc-800 hover:border-zinc-600 transition-all cursor-pointer">
                        <p className="text-sm text-white line-clamp-2">{c.question}</p>
                        <p className="text-xs text-zinc-400 mt-1.5 line-clamp-2 group-hover:line-clamp-none transition-all">{c.answer}</p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-zinc-500">유사도</span>
                          <span className={`text-xs font-medium ${
                            c.score > 0.8 ? 'text-green-400' : c.score > 0.6 ? 'text-amber-400' : 'text-zinc-400'
                          }`}>
                            {(c.score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : steps.search === 'loading' ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => <div key={i} className="skeleton h-20 w-full rounded-lg" />)}
                  </div>
                ) : (
                  <div className="py-8 text-center">
                    <div className="w-12 h-12 mx-auto mb-3 bg-zinc-800 rounded-xl flex items-center justify-center">
                      <FileText className="w-6 h-6 text-zinc-600" />
                    </div>
                    <p className="text-sm text-zinc-600">유사 민원이 없습니다</p>
                  </div>
                )}
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* AI Answer (or Compare) */}
              {compareMode && ollamaResult && geminiResult ? (
                <>
                  {/* Ollama */}
                  <AnswerCard
                    title={`Ollama (${ollamaResult.model_name})`}
                    answer={ollamaResult.answer}
                    latency={ollamaResult.elapsed_time}
                    onCopy={() => handleCopy(ollamaResult.answer)}
                    copied={copied}
                  />
                  {/* Gemini */}
                  <AnswerCard
                    title={`Gemini (${geminiResult.model_name})`}
                    answer={geminiResult.answer}
                    latency={geminiResult.elapsed_time}
                    onCopy={() => handleCopy(geminiResult.answer)}
                    copied={copied}
                  />
                </>
              ) : (
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
                  <h3 className="text-sm font-bold text-zinc-400 mb-3 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" /> AI 답변
                  </h3>
                  {aiAnswer ? (
                    <div>
                      <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-4 text-sm text-zinc-200 leading-relaxed whitespace-pre-wrap">
                        {aiAnswer}
                      </div>
                      <div className="flex items-center gap-2 mt-3">
                        <button
                          onClick={() => handleCopy(aiAnswer)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-zinc-800 text-zinc-400 hover:text-white rounded-lg transition-colors border border-zinc-700"
                        >
                          {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                          {copied ? '복사됨' : '복사'}
                        </button>
                        <button
                          onClick={handleRegenerate}
                          disabled={isProcessing}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-zinc-800 text-zinc-400 hover:text-white rounded-lg transition-colors border border-zinc-700 disabled:opacity-50"
                        >
                          <RotateCcw className="w-3.5 h-3.5" /> 재생성
                        </button>
                        <div className="flex-1" />
                        <button
                          onClick={() => handleFeedback('positive')}
                          disabled={feedbackSent !== null}
                          className={`p-1.5 transition-colors ${
                            feedbackSent === 'positive' ? 'text-green-500' : 'text-zinc-500 hover:text-green-500'
                          }`}
                        >
                          <ThumbsUp className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleFeedback('negative')}
                          disabled={feedbackSent !== null}
                          className={`p-1.5 transition-colors ${
                            feedbackSent === 'negative' ? 'text-red-500' : 'text-zinc-500 hover:text-red-500'
                          }`}
                        >
                          <ThumbsDown className="w-4 h-4" />
                        </button>
                      </div>
                      {feedbackSent && (
                        <p className="text-xs text-green-500/70 mt-2">피드백이 저장되었습니다</p>
                      )}
                    </div>
                  ) : steps.generate === 'loading' ? (
                    <div className="space-y-3">
                      <div className="skeleton h-4 w-full rounded" />
                      <div className="skeleton h-4 w-5/6 rounded" />
                      <div className="skeleton h-4 w-4/6 rounded" />
                      <div className="skeleton h-4 w-full rounded" />
                      <div className="skeleton h-4 w-3/6 rounded" />
                    </div>
                  ) : !allDone ? (
                    <div className="py-12 text-center">
                      <Sparkles className="w-8 h-8 mx-auto mb-2 text-zinc-700" />
                      <p className="text-sm text-zinc-600">분류 및 검색 완료 후 답변을 생성합니다</p>
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Empty State */}
        {isIdle && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center mb-4 border-2 border-dashed border-zinc-800">
              <MessageSquare className="w-8 h-8 text-zinc-600" />
            </div>
            <h3 className="text-lg font-bold text-zinc-400 mb-2">민원 내용을 입력해주세요</h3>
            <p className="text-sm text-zinc-600 max-w-md">
              AI가 민원을 분류하고, 유사 사례를 검색한 뒤, 최적의 답변을 생성합니다.
            </p>
          </div>
        )}
      </div>
    </AppLayout>
  );
}

/** LLM 비교 모드용 답변 카드 */
function AnswerCard({
  title,
  answer,
  latency,
  onCopy,
  copied,
}: {
  title: string;
  answer: string;
  latency?: number;
  onCopy: () => void;
  copied: boolean;
}) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
      <h3 className="text-sm font-bold text-zinc-400 mb-3 flex items-center gap-2">
        <Sparkles className="w-4 h-4" /> {title}
        {latency !== undefined && (
          <span className="ml-auto flex items-center gap-1 text-xs text-zinc-500">
            <Clock className="w-3 h-3" />
            {latency.toFixed(1)}s
          </span>
        )}
      </h3>
      <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-4 text-sm text-zinc-200 leading-relaxed whitespace-pre-wrap">
        {answer}
      </div>
      <div className="flex items-center gap-2 mt-3">
        <button
          onClick={onCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-zinc-800 text-zinc-400 hover:text-white rounded-lg transition-colors border border-zinc-700"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? '복사됨' : '복사'}
        </button>
      </div>
    </div>
  );
}
