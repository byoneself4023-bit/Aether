// DEV-FE-1 / ADR 0028: MSW node server — Vitest jsdom 환경 영역 사용.

import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
