// DEV-FE-1 / ADR 0028: Chat E2E — RAG ReAct 챗봇 API 통합.
// 답변 + sources 영역 영역.

import { describe, it, expect, beforeEach } from "vitest";

import {
  sendChatMessage,
  analyzePortfolio,
  queryRAG,
} from "@/lib/api/llm";
import { useAuthStore } from "@/stores/authStore";

describe("Chat / RAG E2E", () => {
  beforeEach(() => {
    useAuthStore.getState().setTokens("mock.access.token", "mock.refresh.token");
  });

  it("sendChatMessage — answer + sources 반환", async () => {
    const result = await sendChatMessage({
      message: "샤프 비율이 무엇인가요?",
    });

    expect(result.answer).toContain("샤프 비율");
    expect(result.sources).toBeDefined();
    expect(result.sources?.length).toBeGreaterThan(0);
  });

  it("sources 영역 title + source + relevance 영역", async () => {
    const result = await sendChatMessage({
      message: "Sharpe ratio 영역",
    });

    expect(result.sources).toBeDefined();
    const first = result.sources![0];
    expect(first.title).toBeDefined();
    expect(first.source).toBeDefined();
    expect(first.relevance).toBeGreaterThan(0);
    expect(first.relevance).toBeLessThanOrEqual(1);
  });

  it("analyzePortfolio — weights + metrics 영역 분석 답변", async () => {
    const analysis = await analyzePortfolio(
      { AAPL: 0.1053, MSFT: 0.0, GOOGL: 0.8947 },
      { sharpe_ratio: 1.5971, expected_return: 0.4598, volatility: 0.2754 },
    );

    expect(analysis).toContain("GOOGL");
    expect(analysis).toContain("89.47");
    expect(analysis.length).toBeGreaterThan(20);
  });

  it("queryRAG — 영역 영역 검색 영역", async () => {
    const result = await queryRAG("Markowitz", 3);

    expect(result.answer).toBeDefined();
    expect(result.sources).toBeDefined();
    expect(result.sources.length).toBeGreaterThan(0);
  });
});
