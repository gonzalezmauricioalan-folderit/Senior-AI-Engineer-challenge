import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { STORAGE_KEY } from "./storage";
import { API, insightFor, server } from "./test/server";

/** Records the `week_start` of every weekly-insight request, per account. */
function recordInsightRequests() {
  const requests: { accountId: number; weekStart: string | null }[] = [];
  server.use(
    http.get(`${API}/accounts/:id/weekly-insight`, ({ params, request }) => {
      const weekStart = new URL(request.url).searchParams.get("week_start");
      requests.push({ accountId: Number(params["id"]), weekStart });
      return HttpResponse.json(insightFor(Number(params["id"]), weekStart ?? "2026-07-20"));
    }),
  );
  return requests;
}

const stored = () => localStorage.getItem(STORAGE_KEY);

afterEach(() => {
  vi.restoreAllMocks();
});

describe("F8 week navigation", () => {
  it("opens on the latest week, goes back 7 days and disables next at the latest week", async () => {
    const requests = recordInsightRequests();
    const user = userEvent.setup();
    render(<App />);

    expect(await screen.findByText("21 events")).toBeInTheDocument();
    expect(screen.getByTestId("week-range")).toHaveTextContent("Jul 20 – Jul 26, 2026");
    expect(screen.getByRole("button", { name: "Next week" })).toBeDisabled();
    expect(screen.getByText("(CDT)")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Previous week" }));
    await waitFor(() => expect(requests.at(-1)).toEqual({ accountId: 2, weekStart: "2026-07-13" }));
    expect(await screen.findByText("21 events")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Next week" })).toBeEnabled();

    await user.click(screen.getByRole("button", { name: "Next week" }));
    await waitFor(() => expect(requests.at(-1)).toEqual({ accountId: 2, weekStart: "2026-07-20" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Next week" })).toBeDisabled());
  });

  it("resets the week when the account changes", async () => {
    const requests = recordInsightRequests();
    const user = userEvent.setup();
    render(<App />);
    await screen.findByText("21 events");
    await user.click(screen.getByRole("button", { name: "Previous week" }));
    await waitFor(() => expect(requests.at(-1)?.weekStart).toBe("2026-07-13"));

    await user.selectOptions(screen.getByLabelText("Account"), "Metro Collision Centers");
    // Metro's latest complete week (2026-07-13), not "two weeks back from where we were".
    await waitFor(() => expect(requests.at(-1)).toEqual({ accountId: 6, weekStart: "2026-07-13" }));
    expect(await screen.findByText("(EDT)")).toBeInTheDocument();
    expect(JSON.parse(stored() ?? "null")).toEqual({ accountId: 6, weekStart: "2026-07-13" });
  });

  it("requests no insight for an account without a complete week", async () => {
    const requests = recordInsightRequests();
    const user = userEvent.setup();
    render(<App />);
    await screen.findByText("21 events");
    const before = requests.length;

    await user.selectOptions(screen.getByLabelText("Account"), "Quiet Harbor Spa");
    expect(await screen.findByText("No complete week yet for this account.")).toBeInTheDocument();
    expect(requests).toHaveLength(before);
    expect(screen.queryByRole("button", { name: "Next week" })).not.toBeInTheDocument();
  });
});

describe("F9 errors and loading", () => {
  it("shows Loading… while pending, then the data", async () => {
    render(<App />);
    expect(screen.getByText("Loading…")).toBeInTheDocument();
    expect(await screen.findByText("21 events")).toBeInTheDocument();
    expect(screen.queryByText("Loading…")).not.toBeInTheDocument();
  });

  it("shows the error for a 500 on the insight and Retry refetches", async () => {
    let calls = 0;
    server.use(
      http.get(`${API}/accounts/:id/weekly-insight`, () => {
        calls += 1;
        return calls === 1
          ? HttpResponse.json({ detail: "boom" }, { status: 500 })
          : HttpResponse.json(insightFor(2, "2026-07-20"));
      }),
    );
    const user = userEvent.setup();
    render(<App />);

    expect(await screen.findByText("Couldn't load data.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByText("21 events")).toBeInTheDocument();
    expect(calls).toBe(2);
  });

  it("shows the error on a network failure of /accounts and Retry refetches", async () => {
    let failing = true;
    server.use(
      http.get(`${API}/accounts`, () => (failing ? HttpResponse.error() : HttpResponse.json([]))),
    );
    const user = userEvent.setup();
    render(<App />);
    expect(await screen.findByText("Couldn't load data.")).toBeInTheDocument();

    failing = false;
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByText("No accounts found.")).toBeInTheDocument();
  });
});

describe("F11 reload", () => {
  it("opens on the stored account and week and requests that week", async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ accountId: 6, weekStart: "2026-06-01" }));
    const requests = recordInsightRequests();
    render(<App />);

    expect(await screen.findByText("21 events")).toBeInTheDocument();
    expect(requests).toEqual([{ accountId: 6, weekStart: "2026-06-01" }]);
    expect(screen.getByLabelText("Account")).toHaveValue("6");
    expect(screen.getByTestId("week-range")).toHaveTextContent("Jun 1 – Jun 7, 2026");
  });
});

describe("F12 invalid stored selection", () => {
  it.each([
    ["unknown account", JSON.stringify({ accountId: 999, weekStart: "2026-07-13" })],
    ["non-Monday", JSON.stringify({ accountId: 6, weekStart: "2026-07-07" })],
    ["week after the latest", JSON.stringify({ accountId: 6, weekStart: "2026-07-20" })],
    ["broken JSON", "{not json"],
  ])("falls back to the defaults and overwrites storage: %s", async (_name, raw) => {
    localStorage.setItem(STORAGE_KEY, raw);
    const requests = recordInsightRequests();
    render(<App />);

    expect(await screen.findByText("21 events")).toBeInTheDocument();
    expect(requests).toEqual([{ accountId: 2, weekStart: "2026-07-20" }]);
    await waitFor(() => expect(JSON.parse(stored() ?? "null")).toEqual({ accountId: 2, weekStart: "2026-07-20" }));
  });
});

describe("F13 blocked localStorage", () => {
  it("loads with the defaults and shows no error when getItem and setItem throw", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError");
    });
    const requests = recordInsightRequests();
    render(<App />);

    expect(await screen.findByText("21 events")).toBeInTheDocument();
    expect(requests).toEqual([{ accountId: 2, weekStart: "2026-07-20" }]);
    expect(screen.queryByText("Couldn't load data.")).not.toBeInTheDocument();
  });
});
