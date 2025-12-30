/* eslint-disable react-hooks/rules-of-hooks */
import { test as base, Page } from '@playwright/test';

/**
 * Authentication fixture for E2E tests
 * Note: 'use' is a Playwright fixture function, not a React hook
 */
export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ page }, use) => {
    // Navigate to login
    await page.goto('/login');

    // Wait for page to be ready
    await page.waitForLoadState('networkidle');

    // Fill login form with test credentials
    await page.locator('input[type="text"]').fill('test');
    await page.locator('input[type="password"]').fill('Test1234!');

    // Click submit button
    await page.locator('button[type="submit"]').click();

    // Wait for navigation away from login page
    await page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 15000 });

    // Ensure page is fully loaded
    await page.waitForLoadState('networkidle');

    // Use authenticated page
    await use(page);
  },
});

export { expect } from '@playwright/test';
