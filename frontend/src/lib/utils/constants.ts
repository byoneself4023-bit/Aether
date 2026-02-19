// API Base URLs
export const API_URLS = {
  AUTH: process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8003',
  PORTFOLIO: process.env.NEXT_PUBLIC_PORTFOLIO_URL || 'http://localhost:8001',
  LLM: process.env.NEXT_PUBLIC_LLM_URL || 'http://localhost:8002',
} as const;

// Default tickers for demo
export const DEFAULT_TICKERS = [
  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
  'META', 'TSLA', 'JPM', 'V', 'JNJ',
];

// Color palette for charts
export const CHART_COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#06b6d4', // cyan
  '#ec4899', // pink
  '#84cc16', // lime
  '#f97316', // orange
  '#6366f1', // indigo
];

// Format options
export const FORMAT_OPTIONS = {
  currency: {
    style: 'currency' as const,
    currency: 'USD',
  },
  percent: {
    style: 'percent' as const,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },
  decimal: {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  },
};
