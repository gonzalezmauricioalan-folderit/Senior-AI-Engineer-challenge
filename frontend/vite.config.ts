import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config"; // re-exports vite's defineConfig plus the `test` key

export default defineConfig({
  plugins: [react()],
  server: {
    // 0.0.0.0 so the dev server is reachable from outside a container (Task 12 runs it behind compose).
    host: true,
    port: 5173,
  },
  test: {
    // jsdom gives Testing Library a DOM; Vitest has no browser of its own (PLAN.md 3.1).
    environment: "jsdom",
    // Registers jest-dom matchers and the MSW server lifecycle for every test file (PLAN.md 3.7).
    setupFiles: ["./src/test/setup.ts"],
    // Explicit imports from "vitest" in tests instead of implicit globals: keeps tsconfig free of vitest types.
    globals: false,
    // The first test of a file pays for importing React + Recharts + MSW and two mocked round trips;
    // under load that passed the 5s default. Tests still finish as soon as the UI is ready (asyncUtilTimeout in setup.ts).
    testTimeout: 20000,
  },
});
