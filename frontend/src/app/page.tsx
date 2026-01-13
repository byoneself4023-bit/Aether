'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Send,
  Loader2,
  Target,
  Database,
  Clock,
  Headphones,
  Sparkles,
  GitCompare,
} from 'lucide-react';

import { ProcessingSteps } from '@/components/ProcessingSteps';
import { SimilarComplaints } from '@/components/SimilarComplaints';
import { AnswerDraft } from '@/components/AnswerDraft';
import { LLMCompare } from '@/components/LLMCompare';
import {
  classifyText,
  searchSimilar,
  generateAnswer,
  compareLLMs,
  type ClassifyResult,
  type SimilarComplaint,
  type LLMResult,
} from '@/lib/api';

export default function Home() {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const startTimeRef = useRef<number>(0);
  const [elapsedTime, setElapsedTime] = useState<number | undefined>(undefined);

  // 결과 상태
  const [classification, setClassification] = useState<ClassifyResult | null>(null);
  const [similarComplaints, setSimilarComplaints] = useState<SimilarComplaint[]>([]);
  const [aiAnswer, setAiAnswer] = useState<string | null>(null);

  // 비교 모드 결과
  const [ollamaResult, setOllamaResult] = useState<LLMResult | null>(null);
  const [geminiResult, setGeminiResult] = useState<LLMResult | null>(null);

  // 스텝 상태
  const [steps, setSteps] = useState<{
    classify: 'idle' | 'loading' | 'done';
    search: 'idle' | 'loading' | 'done';
    generate: 'idle' | 'loading' | 'done';
  }>({
    classify: 'idle',
    search: 'idle',
    generate: 'idle',
  });

  const handleSubmit = async () => {
    if (!input.trim()) return;

    setIsProcessing(true);
    setClassification(null);
    setSimilarComplaints([]);
    setAiAnswer(null);
    setOllamaResult(null);
    setGeminiResult(null);
    setSteps({ classify: 'idle', search: 'idle', generate: 'idle' });
    startTimeRef.current = Date.now();
    setElapsedTime(0);

    const timer = setInterval(() => {
      setElapsedTime(Date.now() - startTimeRef.current);
    }, 100);

    try {
      // 1. 분류
      setSteps(prev => ({ ...prev, classify: 'loading' }));
      const classifyResult = await classifyText(input);
      setClassification(classifyResult);
      setSteps(prev => ({ ...prev, classify: 'done' }));

      // 2. 유사 민원 검색
      setSteps(prev => ({ ...prev, search: 'loading' }));
      const searchResult = await searchSimilar(input, 5);
      setSimilarComplaints(searchResult);
      setSteps(prev => ({ ...prev, search: 'done' }));

      // 3. AI 답변 생성
      setSteps(prev => ({ ...prev, generate: 'loading' }));
      
      if (compareMode) {
        const compareResult = await compareLLMs(input);
        setOllamaResult(compareResult.ollama);
        setGeminiResult(compareResult.gemini);
        setAiAnswer(compareResult.gemini.answer);
      } else {
        const answerResult = await generateAnswer(input);
        setAiAnswer(answerResult.answer);
      }
      
      setSteps(prev => ({ ...prev, generate: 'done' }));

    } catch (error) {
      console.error('처리 중 오류:', error);
    } finally {
      clearInterval(timer);
      setElapsedTime(Date.now() - startTimeRef.current);
      setIsProcessing(false);
    }
  };

  const handleRegenerate = async () => {
    if (!input.trim()) return;
    setSteps(prev => ({ ...prev, generate: 'loading' }));
    try {
      if (compareMode) {
        const compareResult = await compareLLMs(input);
        setOllamaResult(compareResult.ollama);
        setGeminiResult(compareResult.gemini);
        setAiAnswer(compareResult.gemini.answer);
      } else {
        const result = await generateAnswer(input);
        setAiAnswer(result.answer);
      }
    } catch (error) {
      console.error('재생성 오류:', error);
    } finally {
      setSteps(prev => ({ ...prev, generate: 'done' }));
    }
  };

  // 유사 민원 선택 시 입력창도 변경
  const handleSelectComplaint = async (complaint: SimilarComplaint) => {
    // 입력창을 유사 민원 질문으로 변경
    setInput(complaint.question);
    
    setSteps(prev => ({ ...prev, generate: 'loading' }));
    try {
      if (compareMode) {
        const compareResult = await compareLLMs(complaint.question);
        setOllamaResult(compareResult.ollama);
        setGeminiResult(compareResult.gemini);
        setAiAnswer(compareResult.gemini.answer);
      } else {
        const result = await generateAnswer(complaint.question);
        setAiAnswer(result.answer);
      }
    } catch (error) {
      console.error('답변 생성 오류:', error);
    } finally {
      setSteps(prev => ({ ...prev, generate: 'done' }));
    }
  };

  const handleSendAnswer = (answer: string) => {
    console.log('답변 전송:', answer);
    alert('답변이 전송되었습니다!');
  };

  const isAllDone = steps.classify === 'done' && steps.search === 'done' && steps.generate === 'done';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* 헤더 */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Headphones className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-900">Claro</h1>
                <p className="text-xs text-slate-500">민원 AI 어시스턴트</p>
              </div>
            </div>

            {/* 모델 스펙 & 응답 시간 */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-sm">
                <Target className="h-4 w-4 text-green-500" />
                <span className="text-slate-600">분류 정확도 <strong className="text-slate-900">81.1%</strong></span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Database className="h-4 w-4 text-blue-500" />
                <span className="text-slate-600">벡터 DB <strong className="text-slate-900">57,402</strong>건</span>
              </div>
              {elapsedTime !== undefined && elapsedTime > 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-orange-500" />
                  <span className="text-slate-600">응답 <strong className="text-slate-900">{(elapsedTime / 1000).toFixed(1)}초</strong></span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* 민원 입력 */}
        <Card className="mb-6 shadow-sm border-slate-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-500" />
                <h2 className="font-semibold text-slate-900">민원 내용 입력</h2>
              </div>
              
              {/* 비교 모드 토글 */}
              <div className="flex items-center gap-2">
                <GitCompare className={`h-4 w-4 ${compareMode ? 'text-blue-500' : 'text-slate-400'}`} />
                <Label htmlFor="compare-mode" className="text-sm text-slate-600">LLM 비교</Label>
                <Switch
                  id="compare-mode"
                  checked={compareMode}
                  onCheckedChange={setCompareMode}
                />
              </div>
            </div>
            
            <Textarea
              placeholder="민원 내용을 입력하세요... (예: 인터넷뱅킹 비밀번호를 잊어버렸어요)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="min-h-[120px] resize-none text-base border-slate-200 focus:border-blue-400 focus:ring-blue-400"
            />
            <div className="flex justify-between items-center mt-4">
              <p className="text-sm text-slate-500">
                {compareMode 
                  ? '로컬 LLM(Gemma)과 클라우드 API(Gemini)를 동시에 비교합니다.'
                  : 'AI가 민원을 분류하고, 유사 사례를 검색하여, 답변 초안을 생성합니다.'
                }
              </p>
              <Button
                onClick={handleSubmit}
                disabled={!input.trim() || isProcessing}
                className="bg-blue-600 hover:bg-blue-700 px-6"
                size="lg"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    분석 중...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    분석하기
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 처리 단계 시각화 */}
        <ProcessingSteps
          steps={steps}
          results={{
            domain: classification?.domain,
            confidence: classification?.confidence,
            similarCount: similarComplaints.length,
          }}
        />

        {/* 결과 영역 */}
        {isAllDone && (
          <>
            {compareMode ? (
              /* 비교 모드 UI */
              <div className="space-y-6">
                <LLMCompare
                  ollama={ollamaResult}
                  gemini={geminiResult}
                  isLoading={steps.generate === 'loading'}
                />
                <SimilarComplaints
                  complaints={similarComplaints}
                  isLoading={steps.search === 'loading'}
                  onSelect={handleSelectComplaint}
                />
              </div>
            ) : (
              /* 일반 모드 UI */
              <div className="grid grid-cols-2 gap-6">
                <SimilarComplaints
                  complaints={similarComplaints}
                  isLoading={steps.search === 'loading'}
                  onSelect={handleSelectComplaint}
                />
                <AnswerDraft
                  answer={aiAnswer}
                  isLoading={steps.generate === 'loading'}
                  onRegenerate={handleRegenerate}
                  onSend={handleSendAnswer}
                />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
