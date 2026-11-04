import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./server";

// msw 3 renamed onUnhandledRequest to onUnhandledFrame. "error" makes a request without a handler fail the test instead of silently hitting the network.
beforeAll(() => server.listen({ onUnhandledFrame: "error" }));
afterEach(() => {
  cleanup(); // globals are off, so Testing Library can't register this itself
  server.resetHandlers();
  localStorage.clear(); // storage is per-test state (F11-F13)
});
afterAll(() => server.close());
