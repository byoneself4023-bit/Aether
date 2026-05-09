// DEV-FE-1 / ADR 0028: Error Handling E2E — 401 / 503 / 네트워크 에러.
// MSW errorHandlers 영역 영역 시나리오 시뮬레이션.

import { describe, it, expect, beforeEach } from "vitest";

import { sendChatMessage } from "@/lib/api/llm";
import { optimizePortfolio } from "@/lib/api/portfolio";
import { signUp } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/authStore";
import { server } from "@/test/mocks/server";
import { errorHandlers } from "@/test/mocks/handlers";

describe("Error Handling E2E", () => {
  beforeEach(() => {
    useAuthStore.getState().setTokens("mock.access.token", "mock.refresh.token");
  });

  it("503 Portfolio service unavailable — detail 영역", async () => {
    server.use(errorHandlers.serviceUnavailable);

    await expect(
      optimizePortfolio({
        tickers: ["AAPL", "MSFT"],
        strategy: "max_sharpe",
        period: "3y",
      }),
    ).rejects.toMatchObject({
      response: {
        status: 503,
        data: { detail: "Portfolio service is unavailable" },
      },
    });
  });

  it("409 Duplicate email (U002) — error code 영역", async () => {
    server.use(errorHandlers.duplicateEmail);

    await expect(
      signUp({
        email: "existing@example.com",
        password: "TestPass123!",
        name: "User",
      }),
    ).rejects.toMatchObject({
      response: {
        status: 409,
        data: {
          success: false,
          error: { code: "U002" },
        },
      },
    });
  });

  it("Network error — error.message 영역 (axios reject)", async () => {
    server.use(errorHandlers.networkError);

    await expect(
      sendChatMessage({ message: "test" }),
    ).rejects.toBeInstanceOf(Error);
  });
});
