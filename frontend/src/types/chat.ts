export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  sources?: ChatSource[];
}

export interface ChatRequest {
  message: string;
  tickers?: string[];
  strategy?: 'min_variance' | 'max_sharpe';
  include_backtest?: boolean;
}

export interface ChatSource {
  title: string;
  source: string;
  relevance: number;
}

export interface ChatResponse {
  answer: string;
  sources?: ChatSource[];
  portfolio_data?: Record<string, unknown>;
}

export interface RAGQueryResponse {
  answer: string;
  sources: ChatSource[];
  confidence: number;
}
