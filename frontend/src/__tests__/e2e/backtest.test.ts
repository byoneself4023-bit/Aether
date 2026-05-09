// DEV-FE-1 / ADR 0028: Backtest E2E — walk-forward 백테스트 API 통합.
// TG-2d 시연 결과 일치 (누적 155.74% / Sharpe 0.9051 / MDD 30.34% / 16회 리밸런싱).

import { describe, it, expect, beforeEach } from "vitest";

import { runBacktest } from "@/lib/api/portfolio";
import { useAuthStore } from "@/stores/authStore";

describe("Backtest E2E", () => {
  beforeEach(() => {
    useAuthStore.getState().setTokens("mock.access.token", "mock.refresh.token");
  });

  it("walk-forward — 누적 155.74% / Sharpe 0.9051", async () => {
    const result = await runBacktest({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      start_date: "2022-01-01",
      end_date: "2024-12-31",
      rebalance_every: 63,
    });

    expect(result.metrics.total_return).toBeCloseTo(1.5574, 4);
    expect(result.metrics.annual_return).toBeCloseTo(0.2661, 4);
    expect(result.metrics.sharpe_ratio).toBeCloseTo(0.9051, 4);
    expect(result.metrics.max_drawdown).toBeCloseTo(0.3034, 4);
  });

  it("8 메트릭 영역 영역 영역", async () => {
    const result = await runBacktest({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      start_date: "2022-01-01",
      end_date: "2024-12-31",
      rebalance_every: 63,
    });

    expect(result.metrics.total_return).toBeDefined();
    expect(result.metrics.annual_return).toBeDefined();
    expect(result.metrics.sharpe_ratio).toBeDefined();
    expect(result.metrics.max_drawdown).toBeDefined();
    expect(result.metrics.calmar_ratio).toBeDefined();
    expect(result.metrics.avg_turnover).toBeDefined();
    expect(result.metrics.win_rate).toBeDefined();
    expect(result.rebalance_count).toBeDefined();
  });

  it("calmar_ratio = annual_return / max_drawdown 영역", async () => {
    const result = await runBacktest({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      start_date: "2022-01-01",
      end_date: "2024-12-31",
      rebalance_every: 63,
    });

    const computed = result.metrics.annual_return / result.metrics.max_drawdown;
    expect(result.metrics.calmar_ratio).toBeCloseTo(computed, 2);
  });

  it("리밸런싱 16회 (분기 / 4년 영역)", async () => {
    const result = await runBacktest({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      start_date: "2022-01-01",
      end_date: "2024-12-31",
      rebalance_every: 63,
    });

    expect(result.rebalance_count).toBe(16);
  });
});
