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
  context?: {
    portfolio?: Record<string, number>;
    risk_metrics?: Record<string, number>;
  };
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

export interface RAGDocument {
  id: string;
  title: string;
  content: string;
  metadata?: Record<string, string>;
}
