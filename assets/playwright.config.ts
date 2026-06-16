import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['list'],
    ['json', { outputFile: 'playwright-report.json' }],
  ],

  use: {
    // Set BASE_URL (or edit this default) to your app's dev URL.
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // The architect fills this in during bootstrap from the project's real start
  // command and port (these defaults assume a Node app on :3000). For a
  // non-web / non-Node project, or if you start the server yourself, delete or
  // leave this commented out — E2E will just use BASE_URL as-is.
  // webServer: {
  //   command: process.env.DEV_CMD || 'npm run dev',
  //   url: process.env.BASE_URL || 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },
});
