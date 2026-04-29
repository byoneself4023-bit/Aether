import { describe, it, expect } from "vitest";
import Header from "@/components/layout/Header";

describe("Header", () => {
  it("module loads and exports default function component", () => {
    expect(Header).toBeDefined();
    expect(typeof Header).toBe("function");
  });
});
