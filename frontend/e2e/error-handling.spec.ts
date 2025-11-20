/**
 * E2E Tests for Error Handling System
 *
 * Tests the standardized error response system across the application.
 * Validates that errors are properly caught, formatted, and displayed to users.
 */

import { test, expect } from '@playwright/test';

test.describe('Error Handling System', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto('/');
  });

  test.describe('404 Not Found Errors', () => {
    test('should display Korean error message for non-existent LOT', async ({ page }) => {
      // Try to access non-existent LOT
      await page.goto('/lots/99999');

      // Should show error toast or message
      const errorMessage = page.locator('text=/찾을 수 없습니다/i');
      await expect(errorMessage).toBeVisible({ timeout: 5000 });

      // Verify error code in console (optional - requires CDP)
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          const text = msg.text();
          if (text.includes('RES_002')) {
            // LOT_NOT_FOUND error code detected
            console.log('✅ Standard error code detected:', text);
          }
        }
      });
    });

    test('should handle resource not found gracefully', async ({ page }) => {
      // Navigate to non-existent resource
      await page.goto('/serials/99999');

      // Should not crash, should show error
      await page.waitForLoadState('networkidle');

      // Should still be able to navigate away
      await page.click('a[href="/"]');
      await expect(page).toHaveURL('/');
    });
  });

  test.describe('401 Authentication Errors', () => {
    test('should redirect to login on token expiry', async ({ page, context }) => {
      // Clear auth token to simulate expiry
      await context.clearCookies();
      await page.evaluate(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      });

      // Try to access protected route
      await page.goto('/lots');

      // Should redirect to login
      await expect(page).toHaveURL('/login', { timeout: 3000 });
    });

    test('should show session expired message', async ({ page, context }) => {
      // Set invalid token
      await page.evaluate(() => {
        localStorage.setItem('access_token', 'invalid_token');
      });

      // Make API request
      await page.goto('/lots');

      // Should show warning toast
      const warningToast = page.locator('text=/세션이 만료/i');
      await expect(warningToast).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('422 Validation Errors', () => {
    test('should display field-level validation errors', async ({ page }) => {
      // Login first
      await page.goto('/login');
      await page.fill('input[name="username"]', 'test_user');
      await page.fill('input[name="password"]', 'password');
      await page.click('button[type="submit"]');
      await page.waitForURL('/');

      // Navigate to LOT creation form
      await page.goto('/lots/new');

      // Submit empty form
      await page.click('button[type="submit"]');

      // Should show validation errors
      const validationError = page.locator('text=/올바르지 않습니다|필수|required/i');
      await expect(validationError).toBeVisible({ timeout: 5000 });

      // Should show specific field errors
      const fieldError = page.locator('text=/product_model_id|target_quantity/i');
      await expect(fieldError).toBeVisible({ timeout: 3000 });
    });
  });

  test.describe('500 Server Errors', () => {
    test('should display server error with trace ID', async ({ page }) => {
      // Intercept API request and return 500
      await page.route('**/api/v1/lots/*', (route) => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            error_code: 'SRV_001',
            message: 'Internal server error',
            timestamp: new Date().toISOString(),
            path: route.request().url(),
            trace_id: 'test-trace-id-12345',
          }),
        });
      });

      await page.goto('/lots');

      // Should show server error message
      const serverError = page.locator('text=/서버 오류|server error/i');
      await expect(serverError).toBeVisible({ timeout: 5000 });

      // Trace ID should be logged to console
      const consoleLogs: string[] = [];
      page.on('console', (msg) => {
        consoleLogs.push(msg.text());
      });

      // Wait for console log
      await page.waitForTimeout(1000);

      // Check if trace ID was logged
      const hasTraceId = consoleLogs.some((log) =>
        log.includes('test-trace-id')
      );
      expect(hasTraceId).toBeTruthy();
    });
  });

  test.describe('Network Errors', () => {
    test('should handle network failure gracefully', async ({ page, context }) => {
      // Simulate offline
      await context.setOffline(true);

      await page.goto('/lots');

      // Should show network error
      const networkError = page.locator('text=/네트워크|network/i');
      await expect(networkError).toBeVisible({ timeout: 5000 });

      // Restore connection
      await context.setOffline(false);
    });
  });

  test.describe('Error Recovery', () => {
    test('should allow user to recover from error', async ({ page }) => {
      // Trigger error
      await page.goto('/lots/99999');

      // Wait for error
      await page.waitForTimeout(1000);

      // Navigate to valid page
      await page.click('a[href="/lots"]');

      // Should load successfully
      await expect(page).toHaveURL('/lots');
      await expect(page.locator('h1')).toContainText(/lot|목록/i);
    });

    test('should clear error state on navigation', async ({ page }) => {
      // Trigger error
      await page.goto('/lots/99999');

      // Wait for error toast
      await page.waitForTimeout(2000);

      // Navigate away
      await page.goto('/');

      // Error toast should be gone (or auto-dismissed)
      const errorToast = page.locator('[class*="toast"]:visible');
      await expect(errorToast).toHaveCount(0, { timeout: 5000 });
    });
  });

  test.describe('Error Code Mapping', () => {
    test('should show Korean message for standard error codes', async ({ page }) => {
      // Intercept and return standard error
      await page.route('**/api/v1/lots/99999', (route) => {
        route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({
            error_code: 'RES_002',
            message: 'Lot with ID 99999 not found',
            timestamp: new Date().toISOString(),
            path: '/api/v1/lots/99999',
            trace_id: 'test-trace',
          }),
        });
      });

      await page.goto('/lots/99999');

      // Should display Korean message from ERROR_MESSAGES_KO
      const koreanMessage = page.locator('text=/해당 LOT를 찾을 수 없습니다/i');
      await expect(koreanMessage).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Toast Notifications', () => {
    test('should display toast for client errors', async ({ page }) => {
      await page.goto('/lots/99999');

      // Toast should appear
      const toast = page.locator('[role="alert"], [class*="toast"]').first();
      await expect(toast).toBeVisible({ timeout: 5000 });

      // Toast should auto-dismiss
      await expect(toast).not.toBeVisible({ timeout: 5000 });
    });

    test('should display notify for validation errors with details', async ({ page }) => {
      // Mock validation error response
      await page.route('**/api/v1/lots/', (route) => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 422,
            contentType: 'application/json',
            body: JSON.stringify({
              error_code: 'VAL_001',
              message: 'Request validation failed',
              details: [
                { field: 'product_model_id', message: 'Field required', code: 'missing' },
                { field: 'target_quantity', message: 'Field required', code: 'missing' },
              ],
              timestamp: new Date().toISOString(),
              path: '/api/v1/lots/',
              trace_id: 'test-trace',
            }),
          });
        } else {
          route.continue();
        }
      });

      await page.goto('/lots/new');
      await page.click('button[type="submit"]');

      // Should show notification with details
      const notification = page.locator('[role="alert"], [class*="notification"]').first();
      await expect(notification).toBeVisible({ timeout: 5000 });

      // Should contain field names
      await expect(notification).toContainText(/product_model_id|target_quantity/);
    });
  });
});

test.describe('Error Logging and Debugging', () => {
  test('should log structured error information to console', async ({ page }) => {
    const consoleLogs: { type: string; text: string }[] = [];

    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text(),
      });
    });

    // Trigger error
    await page.goto('/lots/99999');
    await page.waitForTimeout(2000);

    // Find error log with structured data
    const errorLog = consoleLogs.find(
      (log) =>
        log.type === 'error' &&
        (log.text.includes('RES_002') || log.text.includes('error_code'))
    );

    expect(errorLog).toBeDefined();
  });

  test('should include trace_id in error logs', async ({ page }) => {
    const consoleLogs: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleLogs.push(msg.text());
      }
    });

    await page.goto('/lots/99999');
    await page.waitForTimeout(2000);

    // Check if any log contains trace_id
    const hasTraceId = consoleLogs.some((log) =>
      /trace[_-]?id/i.test(log)
    );

    expect(hasTraceId).toBeTruthy();
  });
});
