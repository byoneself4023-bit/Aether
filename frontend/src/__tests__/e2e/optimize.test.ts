// DEV-FE-1 / ADR 0028: Optimize E2E — Markowitz 최적화 API 통합.
// TG-2d 시연 결과 일치 (Sharpe 1.5971 / GOOGL 89.47% / AAPL 10.53%).

import { describe, it, expect, beforeEach } from "vitest";

import { optimizePortfolio } from "@/lib/api/portfolio";
import { useAuthStore } from "@/stores/authStore";

describe("Optimize Portfolio E2E", () => {
  beforeEach(() => {
    // 인증 상태 (axios 인터셉터 Authorization 영역 영역 영역)
    useAuthStore.getState().setTokens("mock.access.token", "mock.refresh.token");
  });

  it("max_sharpe — Sharpe 1.5971 + GOOGL 89.47% 영역", async () => {
    const result = await optimizePortfolio({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      period: "3y",
    });

    expect(result.metrics.sharpe_ratio).toBeCloseTo(1.5971, 4);
    expect(result.weights.GOOGL).toBeCloseTo(0.8947, 4);
    expect(result.weights.AAPL).toBeCloseTo(0.1053, 4);
    expect(result.weights.MSFT).toBeCloseTo(0.0, 4);
  });

  it("weights 합 = 1.0 (sum 검증)", async () => {
    const result = await optimizePortfolio({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      period: "3y",
    });

    const total = Object.values(result.weights).reduce(
      (acc, w) => acc + w,
      0,
    );
    expect(total).toBeCloseTo(1.0, 4);
  });

  it("expected_return / volatility 양수 + 수치 검증", async () => {
    const result = await optimizePortfolio({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      period: "3y",
    });

    expect(result.metrics.expected_return).toBeGreaterThan(0);
    expect(result.metrics.volatility).toBeGreaterThan(0);
    // Sharpe 영역 (return - 0) / vol = 1.5971 영역 영역 (단순 검증)
    const computedSharpe =
      result.metrics.expected_return / result.metrics.volatility;
    expect(computedSharpe).toBeCloseTo(1.6695, 1);
  });

  it("n_stocks + failed_tickers 영역", async () => {
    const result = await optimizePortfolio({
      tickers: ["AAPL", "MSFT", "GOOGL"],
      strategy: "max_sharpe",
      period: "3y",
    });

    expect(result.n_stocks).toBe(3);
    expect(result.failed_tickers).toEqual([]);
    expect(result.warnings).toEqual([]);
  });
});
