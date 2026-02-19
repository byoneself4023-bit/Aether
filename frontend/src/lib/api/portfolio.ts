import { API_URLS } from '@/lib/utils/constants';
import { createApiClient } from './client';
import type {
  OptimizationRequest,
  OptimizationResult,
  RiskMetrics,
  BacktestRequest,
  BacktestResult,
} from '@/types/portfolio';

const portfolioApi = createApiClient(API_URLS.PORTFOLIO);

export async function optimizePortfolio(
  request: OptimizationRequest
): Promise<OptimizationResult> {
  const response = await portfolioApi.post<OptimizationResult>('/api/optimize', request);
  return response.data;
}

export async function getRiskAnalysis(
  tickers: string[],
  weights: Record<string, number>,
  startDate: string,
  endDate: string
): Promise<RiskMetrics> {
  const response = await portfolioApi.post<RiskMetrics>('/api/risk', {
    tickers,
    weights,
    start_date: startDate,
    end_date: endDate,
  });
  return response.data;
}

export async function runBacktest(request: BacktestRequest): Promise<BacktestResult> {
  const response = await portfolioApi.post<BacktestResult>('/api/backtest', request);
  return response.data;
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await portfolioApi.get<{ status: string }>('/health');
  return response.data;
}
