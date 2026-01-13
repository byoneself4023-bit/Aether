const ML_SERVICE_URL = process.env.NEXT_PUBLIC_ML_SERVICE_URL || 'http://localhost:8001';
const LLM_SERVICE_URL = process.env.NEXT_PUBLIC_LLM_SERVICE_URL || 'http://localhost:8002';

// ============ 타입 정의 ============

export interface ClassifyResult {
  domain: string;
  domain_id: number;
  confidence: number;
}

export interface SimilarComplaint {
  question: string;
  answer: string;
  domain: string;
  category: string;
  score: number;
}

export interface GenerateAnswerResult {
  answer: string;
  sources: SimilarComplaint[];
}

export interface LLMResult {
  answer: string;
  elapsed_time: number;
  model_name: string;
}

export interface CompareResult {
  query: string;
  ollama: LLMResult;
  gemini: LLMResult;
  sources: string[];
}

// ============ API 함수 ============

export async function classifyText(text: string): Promise<ClassifyResult> {
  const response = await fetch(`${ML_SERVICE_URL}/api/v1/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error(`분류 실패: ${response.statusText}`);
  }

  return response.json();
}

export async function searchSimilar(text: string, k: number = 5): Promise<SimilarComplaint[]> {
  const response = await fetch(`${LLM_SERVICE_URL}/search/similar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: text, top_k: k }),
  });

  if (!response.ok) {
    throw new Error(`검색 실패: ${response.statusText}`);
  }

  const data = await response.json();
  return data.results;
}

export async function generateAnswer(text: string): Promise<GenerateAnswerResult> {
  const response = await fetch(`${LLM_SERVICE_URL}/generate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: text }),
  });

  if (!response.ok) {
    throw new Error(`답변 생성 실패: ${response.statusText}`);
  }

  return response.json();
}

export async function compareLLMs(text: string): Promise<CompareResult> {
  const response = await fetch(`${LLM_SERVICE_URL}/compare/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: text }),
  });

  if (!response.ok) {
    throw new Error(`비교 실패: ${response.statusText}`);
  }

  return response.json();
}

export async function healthCheck(): Promise<{ ml: boolean; llm: boolean }> {
  const results = { ml: false, llm: false };

  try {
    const mlRes = await fetch(`${ML_SERVICE_URL}/health`);
    results.ml = mlRes.ok;
  } catch {
    results.ml = false;
  }

  try {
    const llmRes = await fetch(`${LLM_SERVICE_URL}/health`);
    results.llm = llmRes.ok;
  } catch {
    results.llm = false;
  }

  return results;
}
