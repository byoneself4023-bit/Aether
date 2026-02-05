/**
 * SSE 파이프라인 서비스 (Claro 특화)
 */
import { API_BASE } from './api';
import type { PipelineEvent } from '@/types';

export function connectPipeline(
  query: string,
  compareMode: boolean,
  onEvent: (event: PipelineEvent) => void,
  onError: (error: Error) => void,
  onDone: () => void,
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/pipeline/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, compare_mode: compareMode }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Pipeline error: ${response.statusText}`);
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE 이벤트 파싱
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event: PipelineEvent = JSON.parse(line.slice(6));
              onEvent(event);
            } catch {
              // 파싱 실패 무시
            }
          }
        }
      }

      onDone();
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        onError(err as Error);
      }
    }
  })();

  return controller;
}
