import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll, vi } from "vitest";

import { server } from "./src/test/mocks/server";

// DEV-FE-1 / ADR 0028: jsdom 영역 localStorage mock (authStore 의존 영역).
const storage: Record<string, string> = {};
const localStorageMock = {
  getItem: vi.fn((key: string) => storage[key] ?? null),
  setItem: vi.fn((key: string, value: string) => {
    storage[key] = value;
  }),
  removeItem: vi.fn((key: string) => {
    delete storage[key];
  }),
  clear: vi.fn(() => {
    Object.keys(storage).forEach((k) => delete storage[k]);
  }),
  key: vi.fn(),
  length: 0,
};
Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
  writable: true,
});

// DEV-FE-1 / ADR 0028: MSW server lifecycle (network mock 자동 영역).
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  Object.keys(storage).forEach((k) => delete storage[k]);
});
afterAll(() => server.close());
