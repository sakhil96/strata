import { defineConfig } from "@playwright/test";

const port = Number(process.env.STRATA_PORT ?? 8077);

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 30_000,
  retries: 0,
  reporter: [["list"]],
  use: { baseURL: `http://127.0.0.1:${port}`, colorScheme: "dark" },
  projects: [
    { name: "phone", use: { viewport: { width: 390, height: 844 } } },
    { name: "laptop", use: { viewport: { width: 1024, height: 768 } } },
    { name: "desk", use: { viewport: { width: 1440, height: 900 } } },
  ],
  webServer: process.env.STRATA_EXTERNAL
    ? undefined
    : {
        command: `cd .. && SCM_BACKEND=local SCM_STATE_DIR=.strata/e2e SCM_RATE_PER_MINUTE=10000 .venv/bin/uvicorn api.main:app --port ${port}`,
        url: `http://127.0.0.1:${port}/health`,
        reuseExistingServer: true,
        timeout: 60_000,
      },
});
