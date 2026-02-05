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
