// DEV-FE-1 / ADR 0028: MSW handlers — 8 endpoint mock (auth + portfolio + llm).
// 응답 영역 = TG-2d 시연 결과 일치 (Sharpe 1.5971 / 누적 155.74% 등).

import { http, HttpResponse } from "msw";

const AUTH = "http://localhost:8003";
const PORTFOLIO = "http://localhost:8001";
const LLM = "http://localhost:8002";

export const handlers = [
  // ===== Auth (8003) — ApiResponse<T> wrapper =====

  http.post(`${AUTH}/api/auth/signup`, async ({ request }) => {
    const body = (await request.json()) as { email: string; name: string };
    return HttpResponse.json(
      {
        success: true,
        data: {
          id: 1,
          email: body.email,
          name: body.name,
          role: "USER",
          enabled: true,
        },
      },
      { status: 201 },
    );
  }),

  http.post(`${AUTH}/api/auth/login`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        accessToken: "eyJhbGciOiJIUzUxMiJ9.mock_access_token",
        refreshToken: "eyJhbGciOiJIUzUxMiJ9.mock_refresh_token",
        tokenType: "Bearer",
        expiresIn: 1800,
      },
    });
  }),

  http.post(`${AUTH}/api/auth/refresh`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        accessToken: "eyJhbGciOiJIUzUxMiJ9.mock_access_token_v2",
        refreshToken: "eyJhbGciOiJIUzUxMiJ9.mock_refresh_token_v2",
        tokenType: "Bearer",
        expiresIn: 1800,
      },
    });
  }),

  http.get(`${AUTH}/api/auth/me`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: 1,
        email: "test@example.com",
        name: "Test User",
        role: "USER",
        enabled: true,
      },
    });
  }),

  http.post(`${AUTH}/api/auth/logout`, () => {
    return HttpResponse.json({ success: true });
  }),

  // ===== Portfolio (8001) — raw response =====

  http.post(`${PORTFOLIO}/api/optimize`, () => {
    // TG-2d 시연 결과 (백엔드 실제 응답 영역 영역)
    return HttpResponse.json({
      weights: { AAPL: 0.1053, MSFT: 0.0, GOOGL: 0.8947 },
      metrics: {
        expected_return: 0.4598,
        volatility: 0.2754,
        sharpe_ratio: 1.5971,
      },
      n_stocks: 3,
      strategy: "max_sharpe",
      period: "3y",
      failed_tickers: [],
      warnings: [],
    });
  }),

  http.post(`${PORTFOLIO}/api/risk`, () => {
    return HttpResponse.json({
      var_95: -0.0234,
      cvar_95: -0.0312,
      annual_volatility: 0.2754,
      max_drawdown: -0.3034,
    });
  }),

  http.post(`${PORTFOLIO}/api/backtest`, () => {
    // TG-2d 시연 결과 (백엔드 실제 응답 영역 영역 / 8 메트릭)
    return HttpResponse.json({
      metrics: {
        total_return: 1.5574,
        annual_return: 0.2661,
        annual_volatility: 0.294,
        sharpe_ratio: 0.9051,
        max_drawdown: 0.3034,
        calmar_ratio: 0.8773,
        avg_turnover: 0.4521,
        win_rate: 0.5816,
      },
      portfolio_values: [],
      rebalance_count: 16,
      rebalance_history: [],
      strategy: "max_sharpe",
      tickers: ["AAPL", "MSFT", "GOOGL"],
      final_weights: { AAPL: 0.1053, MSFT: 0.0, GOOGL: 0.8947 },
    });
  }),

  http.get(`${PORTFOLIO}/health`, () => {
    return HttpResponse.json({ status: "healthy" });
  }),

  // ===== LLM (8002) — raw response =====

  http.post(`${LLM}/api/chat`, () => {
    return HttpResponse.json({
      answer:
        "샤프 비율은 위험 조정 수익률을 나타내는 지표입니다. 1.0 이상은 양호한 수준으로 평가됩니다.",
      sources: [
        {
          title: "샤프 비율 (Sharpe Ratio)",
          source: "investment_metrics.md",
          relevance: 0.92,
        },
        {
          title: "성과 평가 지표",
          source: "performance_evaluation.md",
          relevance: 0.85,
        },
      ],
      portfolio_data: null,
    });
  }),

  http.post(`${LLM}/api/chat/analyze-result`, () => {
    return HttpResponse.json({
      analysis:
        "포트폴리오는 GOOGL에 89.47% 집중되어 있어 단일 종목 리스크가 높습니다. Sharpe 1.5971은 우수한 수준이나, 분산도 영역 검토 의무.",
    });
  }),

  http.post(`${LLM}/api/rag/query`, () => {
    return HttpResponse.json({
      answer: "RAG mock answer",
      sources: [
        { title: "Mock", source: "mock.md", relevance: 0.9 },
      ],
    });
  }),

  http.get(`${LLM}/health`, () => {
    return HttpResponse.json({
      status: "healthy",
      api_key: "ok",
      vectorstore: "ok",
      portfolio_service: "ok",
    });
  }),
];

// 에러 시나리오 — 테스트 영역 server.use(...errorHandlers) 영역 영역 영역.
export const errorHandlers = {
  unauthorized: http.get(`${AUTH}/api/auth/me`, () => {
    return HttpResponse.json(
      {
        success: false,
        error: { code: "A002", message: "토큰이 만료되었습니다" },
      },
      { status: 401 },
    );
  }),

  serviceUnavailable: http.post(`${PORTFOLIO}/api/optimize`, () => {
    return HttpResponse.json(
      { detail: "Portfolio service is unavailable" },
      { status: 503 },
    );
  }),

  duplicateEmail: http.post(`${AUTH}/api/auth/signup`, () => {
    return HttpResponse.json(
      {
        success: false,
        error: { code: "U002", message: "이미 사용 중인 이메일입니다" },
      },
      { status: 409 },
    );
  }),

  networkError: http.post(`${LLM}/api/chat`, () => {
    return HttpResponse.error();
  }),
};
