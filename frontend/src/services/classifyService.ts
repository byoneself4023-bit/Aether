import { apiFetch } from './api';
import type { ClassifyResult } from '@/types';

export async function classifyText(text: string): Promise<ClassifyResult> {
  const result = await apiFetch<ClassifyResult>('/classify', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });

  // 카테고리 분류 (선택 — 모델 미배치 시 스킵)
  try {
    const catData = await apiFetch<{
      category: string;
      category_id: number;
      confidence: number;
    }>('/classify/category', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
    result.category = catData.category;
    result.category_id = catData.category_id;
    result.category_confidence = catData.confidence;
  } catch {
    // 카테고리 모델 미배치 시 무시
  }

  return result;
}
