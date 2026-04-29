import { describe, it, expect } from "vitest";
import DashboardPage from "@/app/dashboard/page";

describe("DashboardPage", () => {
  it("module loads and exports default function component", () => {
    expect(DashboardPage).toBeDefined();
    expect(typeof DashboardPage).toBe("function");
  });
});
