import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import type { WeeklyInsight } from "../api/types";
import { accounts, insightS2 } from "./fixtures";

// Same default as src/api/client.ts; tests never set VITE_API_URL.
export const API = "http://localhost:8000";

/** The S2 insight re-targeted at the requested account and week, so assertions can read it back. */
export function insightFor(accountId: number, weekStart: string): WeeklyInsight {
  const account = accounts.find((a) => a.id === accountId);
  const end = new Date(Date.parse(`${weekStart}T00:00:00Z`) + 6 * 86_400_000).toISOString().slice(0, 10);
  return {
    ...insightS2,
    account: { id: accountId, name: account?.name ?? "Unknown", timezone: account?.timezone ?? "UTC" },
    week: { start: weekStart, end },
  };
}

export const handlers = [
  http.get(`${API}/accounts`, () => HttpResponse.json(accounts)),
  http.get(`${API}/accounts/:id/weekly-insight`, ({ params, request }) => {
    const weekStart = new URL(request.url).searchParams.get("week_start") ?? "2026-07-20";
    return HttpResponse.json(insightFor(Number(params["id"]), weekStart));
  }),
];

export const server = setupServer(...handlers);
