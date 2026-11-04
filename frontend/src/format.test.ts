import { describe, expect, it } from "vitest";
import { addDays, formatNumber, formatPct, isMonday, tzAbbreviation, weekLabel } from "./format";

describe("formatPct", () => {
  it("uses U+2212 for negatives and + for positives", () => {
    expect(formatPct(-0.32)).toBe("−32%");
    expect(formatPct(-0.32)).not.toContain("-");
    expect(formatPct(0.05)).toBe("+5%");
    expect(formatPct(1)).toBe("+100%");
    expect(formatPct(-0.75)).toBe("−75%");
  });
  it("shows 0% without a sign and an em dash for null", () => {
    expect(formatPct(0)).toBe("0%");
    expect(formatPct(null)).toBe("—");
  });
});

describe("formatNumber", () => {
  it("rounds to an integer and handles null", () => {
    expect(formatNumber(75.6)).toBe("76");
    expect(formatNumber(4.5)).toBe("5");
    expect(formatNumber(3.5)).toBe("4");
    expect(formatNumber(3.4)).toBe("3");
    expect(formatNumber(null)).toBe("—");
  });
});

describe("weekLabel", () => {
  it("formats the Monday-Sunday range", () => {
    expect(weekLabel("2026-07-20")).toBe("Jul 20 – Jul 26, 2026");
  });
  it("adds the start year when the week crosses years", () => {
    expect(weekLabel("2026-12-28")).toBe("Dec 28, 2026 – Jan 3, 2027");
  });
});

describe("tzAbbreviation", () => {
  it("follows DST for the given date", () => {
    expect(tzAbbreviation("America/Chicago", "2026-07-20")).toBe("CDT");
    expect(tzAbbreviation("America/Chicago", "2026-01-12")).toBe("CST");
  });
  it("handles Phoenix (no DST) and UTC", () => {
    expect(tzAbbreviation("America/Phoenix", "2026-07-20")).toBe("MST");
    expect(tzAbbreviation("UTC", "2026-07-20")).toBe("UTC");
  });
});

describe("date math", () => {
  it("adds days across month boundaries without local-time shifts", () => {
    expect(addDays("2026-07-20", -7)).toBe("2026-07-13");
    expect(addDays("2026-07-27", 7)).toBe("2026-08-03");
    expect(addDays("2026-03-02", 7)).toBe("2026-03-09"); // spans the US DST change
  });
  it("detects Mondays", () => {
    expect(isMonday("2026-07-20")).toBe(true);
    expect(isMonday("2026-07-21")).toBe(false);
  });
});
