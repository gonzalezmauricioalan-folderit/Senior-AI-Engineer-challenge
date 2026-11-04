import type { Account, WeeklyInsight } from "./types";

const BASE_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/** Non-2xx response; `detail` is the API's `{"detail": ...}` message when it has one. */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(`API ${status}: ${detail}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, { signal });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body: unknown = await response.json();
      // 422 from FastAPI's own validation has a list in `detail`; only plain messages are shown.
      if (typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Body is not JSON (e.g. a proxy error page): keep the status text.
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

export function getAccounts(signal?: AbortSignal): Promise<Account[]> {
  return getJson<Account[]>("/accounts", signal);
}

export function getWeeklyInsight(
  accountId: number,
  weekStart?: string,
  signal?: AbortSignal,
): Promise<WeeklyInsight> {
  const query = weekStart ? `?week_start=${encodeURIComponent(weekStart)}` : "";
  return getJson<WeeklyInsight>(`/accounts/${accountId}/weekly-insight${query}`, signal);
}
