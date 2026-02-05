import { apiFetch } from './api';
import type { SimilarComplaint } from '@/types';

export async function searchSimilar(
  text: string,
  k: number = 5,
): Promise<SimilarComplaint[]> {
  const data = await apiFetch<{ query: string; results: SimilarComplaint[] }>(
    '/search/similar',
    {
      method: 'POST',
      body: JSON.stringify({ query: text, top_k: k }),
    },
  );
  return data.results;
}
