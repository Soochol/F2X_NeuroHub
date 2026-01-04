import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration for Station UI
 * Tests against the backend-served UI at localhost:8080/ui
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list']
  ],

  use: {
    // Test against the backend-served UI
    baseURL: 'http://localhost:8080/ui',
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

  // No webServer config - assumes station_service backend is already running
  // Run `python -m station_service.main` before tests
});
