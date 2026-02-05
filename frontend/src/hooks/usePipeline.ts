/**
 * SSE 기반 파이프라인 상태 관리 훅 (Claro 특화)
 */
import { useState, useCallback, useRef } from 'react';
import { connectPipeline } from '@/services/pipelineService';
import { classifyText } from '@/services/classifyService';
import { searchSimilar } from '@/services/searchService';
import { generateAnswer } from '@/services/generateService';
import { compareLLMs } from '@/services/compareService';
import type {
  ClassifyResult,
  SimilarComplaint,
  LLMResult,
  PipelineEvent,
} from '@/types';

export type StepStatus = 'idle' | 'loading' | 'done';

export interface PipelineState {
  isProcessing: boolean;
  steps: { classify: StepStatus; search: StepStatus; generate: StepStatus };
  classification: ClassifyResult | null;
  similarComplaints: SimilarComplaint[];
  aiAnswer: string | null;
  ollamaResult: LLMResult | null;
  geminiResult: LLMResult | null;
}

export function usePipeline() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [steps, setSteps] = useState<PipelineState['steps']>({
    classify: 'idle',
    search: 'idle',
    generate: 'idle',
  });
  const [classification, setClassification] = useState<ClassifyResult | null>(null);
  const [similarComplaints, setSimilarComplaints] = useState<SimilarComplaint[]>([]);
  const [aiAnswer, setAiAnswer] = useState<string | null>(null);
  const [ollamaResult, setOllamaResult] = useState<LLMResult | null>(null);
  const [geminiResult, setGeminiResult] = useState<LLMResult | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const resetState = useCallback(() => {
    setClassification(null);
    setSimilarComplaints([]);
    setAiAnswer(null);
    setOllamaResult(null);
    setGeminiResult(null);
    setSteps({ classify: 'idle', search: 'idle', generate: 'idle' });
  }, []);

  /** SSE 파이프라인으로 실행 */
  const executePipeline = useCallback(
    (query: string, compareMode: boolean) => {
      resetState();
      setIsProcessing(true);

      const abort = connectPipeline(
        query,
        compareMode,
        (event: PipelineEvent) => {
          const stepName = event.name;
          if (event.status === 'running') {
            setSteps((prev) => ({ ...prev, [stepName]: 'loading' }));
          } else if (event.status === 'done') {
            setSteps((prev) => ({ ...prev, [stepName]: 'done' }));

            if (stepName === 'classify' && event.result) {
              setClassification(event.result as ClassifyResult);
            }
            if (stepName === 'search' && event.result) {
              setSimilarComplaints(event.result as SimilarComplaint[]);
            }
            if (stepName === 'generate' && event.result) {
              if (compareMode && event.result.ollama) {
                setOllamaResult(event.result.ollama);
                setGeminiResult(event.result.gemini);
                setAiAnswer(event.result.gemini?.answer || null);
              } else {
                setAiAnswer(event.result.answer || null);
              }
            }
          } else if (event.status === 'error') {
            setSteps((prev) => ({ ...prev, [stepName]: 'done' }));
          }
        },
        (error) => {
          console.error('Pipeline SSE error:', error);
          setIsProcessing(false);
        },
        () => {
          setIsProcessing(false);
        },
      );

      abortRef.current = abort;
    },
    [resetState],
  );

  /** 개별 API로 실행 (폴백/재생성용) */
  const executeLegacy = useCallback(
    async (query: string, compareMode: boolean) => {
      resetState();
      setIsProcessing(true);

      try {
        // 1. 분류
        setSteps((prev) => ({ ...prev, classify: 'loading' }));
        const classifyResult = await classifyText(query);
        setClassification(classifyResult);
        setSteps((prev) => ({ ...prev, classify: 'done' }));

        // 2. 유사 검색
        setSteps((prev) => ({ ...prev, search: 'loading' }));
        const searchResult = await searchSimilar(query, 5);
        setSimilarComplaints(searchResult);
        setSteps((prev) => ({ ...prev, search: 'done' }));

        // 3. 생성
        setSteps((prev) => ({ ...prev, generate: 'loading' }));
        if (compareMode) {
          const compareResult = await compareLLMs(query);
          setOllamaResult(compareResult.ollama);
          setGeminiResult(compareResult.gemini);
          setAiAnswer(compareResult.gemini.answer);
        } else {
          const answerResult = await generateAnswer(query);
          setAiAnswer(answerResult.answer);
        }
        setSteps((prev) => ({ ...prev, generate: 'done' }));
      } catch (error) {
        console.error('처리 중 오류:', error);
      } finally {
        setIsProcessing(false);
      }
    },
    [resetState],
  );

  /** 재생성 (generate 스텝만 재실행) */
  const regenerate = useCallback(
    async (query: string, compareMode: boolean) => {
      setSteps((prev) => ({ ...prev, generate: 'loading' }));
      try {
        if (compareMode) {
          const compareResult = await compareLLMs(query);
          setOllamaResult(compareResult.ollama);
          setGeminiResult(compareResult.gemini);
          setAiAnswer(compareResult.gemini.answer);
        } else {
          const result = await generateAnswer(query);
          setAiAnswer(result.answer);
        }
      } catch (error) {
        console.error('재생성 오류:', error);
      } finally {
        setSteps((prev) => ({ ...prev, generate: 'done' }));
      }
    },
    [],
  );

  const abort = useCallback(() => {
    abortRef.current?.abort();
    setIsProcessing(false);
  }, []);

  return {
    isProcessing,
    steps,
    classification,
    similarComplaints,
    aiAnswer,
    ollamaResult,
    geminiResult,
    executePipeline,
    executeLegacy,
    regenerate,
    abort,
    resetState,
  };
}
