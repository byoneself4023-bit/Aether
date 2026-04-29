import { describe, it, expect } from "vitest";
import ChatPage from "@/app/dashboard/chat/page";

describe("ChatPage", () => {
  it("module loads and exports default function component", () => {
    expect(ChatPage).toBeDefined();
    expect(typeof ChatPage).toBe("function");
  });
});
