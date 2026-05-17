import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for browser-level product proof tests.
 */
const startLiveStack = process.env.PLAYWRIGHT_START_LIVE_STACK === '1';
const databaseMode = process.env.LEXI_E2E_DATABASE || 'sqlite';
const apiPort = process.env.LEXI_E2E_API_PORT || '8010';
const frontendPort = process.env.LEXI_E2E_FRONTEND_PORT || '3100';
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || `http://127.0.0.1:${apiPort}/api/v1`;
const pythonCommand = process.env.LEXI_PYTHON || 'conda run --no-capture-output -n lexi python';
const apiTmpRoot = process.env.LEXI_E2E_TMP_ROOT || `/tmp/lexi_playwright_api_${databaseMode}_${apiPort}`;

export default defineConfig({
  testDir: './tests',
  globalTeardown: startLiveStack ? './tests/live-stack-teardown.js' : undefined,
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0, // No retries - we want to see actual failures
  workers: 1, // Single worker to avoid conflicts
  reporter: 'list',

  use: {
    baseURL: startLiveStack ? `http://127.0.0.1:${frontendPort}` : 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: startLiveStack
    ? [
        {
          command: `LEXI_E2E_TMP_ROOT="${apiTmpRoot}" ${pythonCommand} ../scripts/testing/live_api_server.py --port ${apiPort} --database ${databaseMode}`,
          url: `http://127.0.0.1:${apiPort}/health`,
          reuseExistingServer: false,
          timeout: 120000,
        },
        {
          command: `NEXT_PUBLIC_API_BASE_URL=${apiBaseUrl} ./node_modules/.bin/next dev -p ${frontendPort} --hostname 127.0.0.1`,
          url: `http://127.0.0.1:${frontendPort}`,
          reuseExistingServer: false,
          timeout: 120000,
        },
      ]
    : undefined,
});
