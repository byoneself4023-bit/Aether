import { describe, it, expect } from "vitest";
import OptimizePage from "@/app/dashboard/optimize/page";

describe("OptimizePage", () => {
  it("module loads and exports default function component", () => {
    expect(OptimizePage).toBeDefined();
    expect(typeof OptimizePage).toBe("function");
  });
});
