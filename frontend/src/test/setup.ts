import "@testing-library/jest-dom/vitest";
import { cleanup, configure } from "@testing-library/react";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./server";

// findBy*/waitFor default to 1s, which a cold first render (module load + two mocked round trips)
// can exceed on a loaded CI machine. They return as soon as the UI is ready, so a larger ceiling
// only matters when something is genuinely broken.
configure({ asyncUtilTimeout: 5000 });

// msw 3 renamed onUnhandledRequest to onUnhandledFrame. "error" makes a request without a handler fail the test instead of silently hitting the network.
beforeAll(() => server.listen({ onUnhandledFrame: "error" }));
afterEach(() => {
  cleanup(); // globals are off, so Testing Library can't register this itself
  server.resetHandlers();
  localStorage.clear(); // storage is per-test state (F11-F13)
});
afterAll(() => server.close());
