import { apiFetch } from './api';
import type { CompareResult } from '@/types';

export async function compareLLMs(text: string): Promise<CompareResult> {
  return apiFetch<CompareResult>('/compare/', {
    method: 'POST',
    body: JSON.stringify({ query: text }),
  });
}
