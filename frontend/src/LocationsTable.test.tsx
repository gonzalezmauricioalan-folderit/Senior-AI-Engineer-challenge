import { render, screen, within } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import App from "./App";
import type { WeeklyInsight } from "./api/types";
import {
  insightLowVolumeRow,
  insightNotEnoughRow,
  insightS1,
  insightS2,
  insightS4,
  insightUnsortedRows,
} from "./test/fixtures";
import { API, server } from "./test/server";

function serve(insight: WeeklyInsight) {
  server.use(http.get(`${API}/accounts/:id/weekly-insight`, () => HttpResponse.json(insight)));
}

/** Body rows as arrays of cell texts, e.g. ["East", "4", "~20", "−80%", "▼ Lower than usual"]. */
async function bodyRows(): Promise<string[][]> {
  const table = await screen.findByRole("table", { name: /locations/i });
  const [, ...rows] = within(table).getAllByRole("row");
  return rows.map((row) => Array.from(row.children, (c) => c.textContent?.trim() ?? ""));
}

describe("F4 ranked table (S4)", () => {
  it("lists East, South, North, West in API order with their badges while the account is Normal", async () => {
    serve(insightS4);
    render(<App />);

    expect(await bodyRows()).toEqual([
      ["East", "4", "~20", "−80%", "▼ Lower than usual"],
      ["South", "8", "~20", "−60%", "▼ Lower than usual"],
      ["North", "20", "~20", "0%", "● Normal"],
      ["West", "35", "~20", "+75%", "▲ Higher than usual"],
    ]);
    expect(screen.getByRole("heading", { name: "Locations (4)" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Locations (4)" })).toHaveTextContent("needs attention first");
    // The account itself is fine: its badge is Normal while two rows are Lower.
    expect(within(screen.getByRole("region", { name: "Verdict" })).getByText("● Normal")).toBeInTheDocument();
  });

  it("has column headers with scope=col and an accessible name", async () => {
    serve(insightS4);
    render(<App />);
    const table = await screen.findByRole("table", { name: "Locations, needs attention first" });
    const headers = within(table).getAllByRole("columnheader");
    expect(headers.map((h) => h.textContent)).toEqual(["Location", "This week", "Usual", "vs usual", "Status"]);
    for (const h of headers) expect(h).toHaveAttribute("scope", "col");
  });
});

describe("F5 low-volume row", () => {
  it("shows the Low volume tag with its tooltip only on the low-volume row", async () => {
    serve(insightLowVolumeRow);
    render(<App />);
    await bodyRows();

    const tag = screen.getByText("Low volume", { selector: ".tag" });
    expect(tag).toHaveAttribute("title", "Low weekly volume: results may be unreliable.");
    expect(within(screen.getByRole("table")).getAllByText("Low volume")).toHaveLength(1);
  });

  it("shows no tag when no row is low volume", async () => {
    serve(insightS4);
    render(<App />);
    await bodyRows();
    expect(screen.queryByText("Low volume", { selector: ".tag" })).not.toBeInTheDocument();
  });
});

describe("F7 single location", () => {
  it("still shows the table, with one row", async () => {
    serve(insightS2);
    render(<App />);
    expect(await bodyRows()).toEqual([["Main", "21", "~20", "+5%", "● Normal"]]);
    expect(screen.getByRole("heading", { name: "Locations (1)" })).toBeInTheDocument();
  });
});

describe("F10 not_enough_history row", () => {
  it("shows an em dash for usual and %, and keeps the badge", async () => {
    serve(insightNotEnoughRow);
    render(<App />);
    expect(await bodyRows()).toEqual([
      ["Old", "20", "~20", "0%", "● Normal"],
      ["New", "5", "—", "—", "○ Not enough history"],
    ]);
  });
});

describe("F1 empty table", () => {
  it("shows Locations (0) and the empty message instead of a table", async () => {
    serve(insightS1);
    render(<App />);
    expect(await screen.findByText("No locations with activity yet.")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Locations (0)" })).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });
});

describe("API order is kept", () => {
  it("renders rows exactly as sent, without sorting by name or by %", async () => {
    serve(insightUnsortedRows);
    render(<App />);
    const names = (await bodyRows()).map((r) => r[0]);
    expect(names).toEqual(["Site K", "Site B", "Site Z", "Site A"]);
  });
});
