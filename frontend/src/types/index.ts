export type { ClassifyResult } from './classify';
export type { SimilarComplaint } from './search';
export type { GenerateAnswerResult } from './generate';
export type { LLMResult, CompareResult } from './compare';

/** 피드백 */
export interface FeedbackRequest {
  query: string;
  answer: string;
  model_name?: string;
  domain?: string;
  category?: string;
  rating: number;
  comment?: string;
}

/** SSE 파이프라인 이벤트 */
export interface PipelineEvent {
  name: 'classify' | 'search' | 'generate';
  status: 'pending' | 'running' | 'done' | 'error';
  result?: any;
  error?: string;
}

/** 표준 API 응답 */
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  error?: string;
}
