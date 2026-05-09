// DEV-FE-1 / ADR 0028: Auth Flow E2E — signup + login + getMe + logout.
// API 함수 영역 영역 (MSW network intercept). 페이지 렌더링 X (next/navigation 의존 영역).

import { describe, it, expect, beforeEach } from "vitest";

import { signUp, login, getMe, logout, refreshToken } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/authStore";
import { server } from "@/test/mocks/server";
import { errorHandlers } from "@/test/mocks/handlers";

describe("Auth Flow E2E", () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
  });

  it("signup — 정상 응답 (201 / id + email + name)", async () => {
    const result = await signUp({
      email: "test@example.com",
      password: "TestPass123!",
      name: "Test User",
    });

    expect(result.id).toBe(1);
    expect(result.email).toBe("test@example.com");
    expect(result.name).toBe("Test User");
    expect(result.role).toBe("USER");
    expect(result.enabled).toBe(true);
  });

  it("login — 200 / accessToken + refreshToken 반환", async () => {
    const result = await login({
      email: "test@example.com",
      password: "TestPass123!",
    });

    expect(result.accessToken).toMatch(/^eyJhbGciOiJIUzUxMiJ9/);
    expect(result.refreshToken).toMatch(/^eyJhbGciOiJIUzUxMiJ9/);
    expect(result.tokenType).toBe("Bearer");
    expect(result.expiresIn).toBe(1800);
  });

  it("getMe — Authorization 헤더 자동 주입 + 사용자 정보 반환", async () => {
    // login 영역 토큰 영역
    const tokens = await login({
      email: "test@example.com",
      password: "TestPass123!",
    });
    useAuthStore.getState().setTokens(tokens.accessToken, tokens.refreshToken);

    const me = await getMe();

    expect(me.email).toBe("test@example.com");
    expect(me.name).toBe("Test User");
    expect(me.role).toBe("USER");
  });

  it("logout — 200 (서버 영역 토큰 blacklist)", async () => {
    const tokens = await login({
      email: "test@example.com",
      password: "TestPass123!",
    });
    useAuthStore.getState().setTokens(tokens.accessToken, tokens.refreshToken);

    await expect(logout()).resolves.toBeUndefined();
  });

  it("refreshToken — 200 / 새 accessToken 반환", async () => {
    const result = await refreshToken("old.refresh.token");

    expect(result.accessToken).toMatch(/_v2$/);
    expect(result.tokenType).toBe("Bearer");
  });

  it("signup — 409 DUPLICATE_EMAIL (U002) 에러 처리", async () => {
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
});
