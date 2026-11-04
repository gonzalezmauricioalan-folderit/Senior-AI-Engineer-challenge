import { render, screen, waitFor, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import App from "./App";
import type { WeeklyInsight } from "./api/types";
import {
  DUPLICATE_NOTE,
  UTC_NOTE,
  insightLowVolume,
  insightS1,
  insightS3a,
  insightS3b,
  insightWithNotes,
} from "./test/fixtures";
import { API, server } from "./test/server";

/** Every weekly-insight request answers with `insight` (the account picker's default account loads first). */
function serve(insight: WeeklyInsight) {
  server.use(http.get(`${API}/accounts/:id/weekly-insight`, () => HttpResponse.json(insight)));
}

const NOT_ENOUGH = "Not enough history yet — at least 4 complete weeks are needed to tell what's normal.";
const LOW_VOLUME = "This account has low weekly volume, so results may be unreliable.";

describe("F1 account without events (card and chart)", () => {
  it("shows the not-enough-history card and a chart with 7 zero bars", async () => {
    serve(insightS1);
    render(<App />);

    const card = await screen.findByRole("region", { name: "Verdict" });
    expect(within(card).getByText("○ Not enough history")).toBeInTheDocument();
    expect(within(card).getByText(NOT_ENOUGH)).toBeInTheDocument();
    // No numbers are invented for a week without a baseline.
    expect(card).not.toHaveTextContent("usual");
    expect(card).not.toHaveTextContent("null");
    expect(card).not.toHaveTextContent("vs. previous");

    const chart = screen.getByRole("img", { name: /events per day/i });
    for (const day of ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]) {
      expect(within(chart).getByText(day)).toBeInTheDocument();
    }
    const summary = screen.getByRole("list", { name: "Daily totals" });
    const items = within(summary).getAllByRole("listitem");
    expect(items).toHaveLength(7);
    expect(items[0]).toHaveTextContent("Mon: 0 events, usual —");
    expect(items[6]).toHaveTextContent("Sun: 0 events, usual —");
    // Recharts draws no <rect> for a zero-height bar, so "7 zero bars" = the bar layer is mounted
    // (the axis labels above prove the chart rendered) and has no rectangles. The 7 zero values
    // are asserted through the text summary. The bars-are-drawn side is checked in F2.
    expect(chart.querySelector(".recharts-bar")).not.toBeNull();
    expect(chart.querySelectorAll(".recharts-bar-rectangle")).toHaveLength(0);
    for (const item of items) expect(item).toHaveTextContent(/: 0 events/);
  });
});

describe("F2 normal week", () => {
  it("shows the badge and the exact summary line", async () => {
    render(<App />);

    const card = await screen.findByRole("region", { name: "Verdict" });
    expect(within(card).getByText("● Normal")).toBeInTheDocument();
    // lower 8.8 -> 9 and upper 31.2 -> 31; usual 20.0 -> ~20; +0.05 -> +5%.
    expect(within(card).getByText("21 events · usual ~20 (range 9–31) · +5%")).toBeInTheDocument();
    expect(within(card).getByText("vs. previous 8 weeks")).toBeInTheDocument();
    expect(within(card).queryByText(NOT_ENOUGH)).not.toBeInTheDocument();
    expect(within(card).queryByText(LOW_VOLUME)).not.toBeInTheDocument();

    const chart = screen.getByRole("img", { name: /events per day/i });
    await waitFor(() => expect(chart.querySelectorAll(".recharts-bar-rectangle")).toHaveLength(7));
    expect(screen.getAllByRole("listitem")).toHaveLength(7);
    // Bars are driven by `total`, not `usual`: Mon and Tue have the same usual (3) but totals 3 and 4.
    const heights = Array.from(chart.querySelectorAll(".recharts-bar-rectangle path")).map((p) => Number(p.getAttribute("height")));
    expect(heights).toHaveLength(7);
    expect(heights[1]).toBeGreaterThan(heights[0] ?? Infinity);
    expect(screen.getByText("Wed: 3 events, usual 3")).toBeInTheDocument();
  });

  it("prints a dash, not ~null, when usual, range or pct are missing", async () => {
    serve({
      ...insightS3a,
      summary: { ...insightS3a.summary, usual: null, lower: null, upper: null, pct_vs_usual: null, status: "normal" },
    });
    render(<App />);

    expect(await screen.findByText("5 events · usual — (range —) · —")).toBeInTheDocument();
    expect(screen.queryByText(/null/)).not.toBeInTheDocument();
  });
});

describe("F3 lower and higher weeks", () => {
  it("S3a: lower than usual with -75% (U+2212)", async () => {
    serve(insightS3a);
    render(<App />);

    const card = await screen.findByRole("region", { name: "Verdict" });
    expect(within(card).getByText("▼ Lower than usual")).toBeInTheDocument();
    expect(within(card).getByText("5 events · usual ~20 (range 9–31) · −75%")).toBeInTheDocument();
  });

  it("S3b: higher than usual with +100%", async () => {
    serve(insightS3b);
    render(<App />);

    const card = await screen.findByRole("region", { name: "Verdict" });
    expect(within(card).getByText("▲ Higher than usual")).toBeInTheDocument();
    expect(within(card).getByText("40 events · usual ~20 (range 9–31) · +100%")).toBeInTheDocument();
  });

  it("uses the status colour variables", async () => {
    serve(insightS3a);
    render(<App />);
    expect(await screen.findByText("▼ Lower than usual")).toHaveStyle({ color: "var(--color-lower)" });
  });
});

describe("F5 low volume (account)", () => {
  it("shows the account warning", async () => {
    serve(insightLowVolume);
    render(<App />);

    const card = await screen.findByRole("region", { name: "Verdict" });
    expect(within(card).getByText(LOW_VOLUME)).toBeInTheDocument();
    expect(within(card).getByText("0 events · usual ~5 (range 0–12) · −100%")).toBeInTheDocument();
  });
});

describe("F6 data notes", () => {
  it("renders the duplicate and UTC notes exactly as given", async () => {
    serve(insightWithNotes);
    render(<App />);

    const notes = await screen.findByRole("list", { name: "Data notes" });
    const items = within(notes).getAllByRole("listitem");
    expect(items).toHaveLength(2);
    expect(within(items[0] as HTMLElement).getByText(DUPLICATE_NOTE)).toBeInTheDocument();
    expect(within(items[1] as HTMLElement).getByText(UTC_NOTE)).toBeInTheDocument();
  });

  it("renders no notes list when there are none", async () => {
    render(<App />);
    await screen.findByRole("region", { name: "Verdict" });
    expect(screen.queryByRole("list", { name: "Data notes" })).not.toBeInTheDocument();
  });
});
