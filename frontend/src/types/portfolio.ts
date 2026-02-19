// ============================================================
// Optimize
// ============================================================

export interface OptimizationRequest {
  tickers: string[];
  strategy?: 'max_sharpe' | 'min_variance';
  period?: '1y' | '3y' | '5y';
  start_date?: string;
  end_date?: string;
  include_frontier?: boolean;
  include_diagnostics?: boolean;
  rf?: number;
}

export interface PortfolioMetricsResponse {
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
}

export interface FrontierPoint {
  expected_return: number;
  volatility: number;
  weights: Record<string, number>;
}

export interface OptimizationResult {
  weights: Record<string, number>;
  metrics: PortfolioMetricsResponse;
  n_stocks: number;
  strategy: string;
  period: string;
  frontier?: FrontierPoint[];
  failed_tickers?: string[];
  warnings?: string[];
}

// ============================================================
// Risk
// ============================================================

export interface RiskMetrics {
  var_95: number;
  var_99: number;
  cvar_95: number;
  cvar_99: number;
  max_drawdown: number;
  beta?: number;
  correlation_matrix?: Record<string, Record<string, number>>;
}

// ============================================================
// Backtest
// ============================================================

export interface BacktestRequest {
  tickers: string[];
  strategy?: 'max_sharpe' | 'min_variance' | 'equal_weight';
  period?: '3y' | '5y' | '10y';
  start_date?: string;
  end_date?: string;
  train_window?: number;
  rebalance_every?: number;
  transaction_cost?: number;
  use_shrinkage?: boolean;
}

export interface PerformanceMetrics {
  total_return: number;
  annual_return: number;
  annual_volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  calmar_ratio: number;
  avg_turnover: number;
  win_rate: number;
}

export interface RebalanceRecord {
  date: string;
  weights: Record<string, number>;
  turnover: number;
}

export interface BacktestResult {
  metrics: PerformanceMetrics;
  portfolio_values: { date: string; value: number }[];
  rebalance_count: number;
  rebalance_history: RebalanceRecord[];
  strategy: string;
  tickers: string[];
  final_weights: Record<string, number>;
}

export interface PortfolioValue {
  date: string;
  value: number;
}

export interface DrawdownPoint {
  date: string;
  drawdown: number;
}

export interface RebalanceEvent {
  date: string;
  before: Record<string, number>;
  after: Record<string, number>;
  cost?: number;
}
