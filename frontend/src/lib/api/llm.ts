import { API_URLS } from '@/lib/utils/constants';
import { createApiClient } from './client';
import type { ChatRequest, ChatResponse, RAGQueryResponse } from '@/types/chat';

const llmApi = createApiClient(API_URLS.LLM);

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await llmApi.post<ChatResponse>('/api/chat', request);
  return response.data;
}

export async function analyzePortfolio(
  weights: Record<string, number>,
  metrics: Record<string, number>
): Promise<string> {
  const response = await llmApi.post<{ analysis: string }>('/api/chat/analyze-result', {
    weights,
    metrics,
  });
  return response.data.analysis;
}

export async function queryRAG(question: string, k = 3): Promise<RAGQueryResponse> {
  const response = await llmApi.post<RAGQueryResponse>('/api/rag/query', {
    question,
    k,
  });
  return response.data;
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await llmApi.get<{ status: string }>('/health');
  return response.data;
}
