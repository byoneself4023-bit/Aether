import { apiFetch } from './api';
import type { GenerateAnswerResult } from '@/types';

export async function generateAnswer(
  text: string,
): Promise<GenerateAnswerResult> {
  return apiFetch<GenerateAnswerResult>('/generate/', {
    method: 'POST',
    body: JSON.stringify({ query: text }),
  });
}
