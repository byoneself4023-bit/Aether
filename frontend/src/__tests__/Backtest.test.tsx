import { describe, it, expect } from "vitest";
import BacktestPage from "@/app/dashboard/backtest/page";

describe("BacktestPage", () => {
  it("module loads and exports default function component", () => {
    expect(BacktestPage).toBeDefined();
    expect(typeof BacktestPage).toBe("function");
  });
});
