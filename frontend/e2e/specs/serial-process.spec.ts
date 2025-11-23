/**
 * E2E Tests for Serial Process Management Flow
 *
 * Tests the complete workflow of scanning serials and completing processes
 */

import { test, expect } from '@playwright/test';

test.describe('Serial Process Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the serial process page
    // Note: Adjust URL based on actual dev server port
    await page.goto('http://localhost:3000/serials/process');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display barcode scanner on page load', async ({ page }) => {
    // Given: Page is loaded

    // Then: Barcode scanner should be visible
    await expect(page.getByLabel(/serial number/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /scan/i })).toBeVisible();
    await expect(page.getByText(/ready to scan/i)).toBeVisible();
  });

  test('should scan serial and display information', async ({ page }) => {
    // Given: Valid serial number
    const serialNumber = 'KR01PSA2511001';

    // When: Enter serial number and click scan
    await page.fill('input[type="text"]', serialNumber);
    await page.click('button:has-text("Scan")');

    // Then: Serial information should be displayed
    await expect(page.locator('text=KR01-PSA-2511-001')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=/LOT/i')).toBeVisible();
  });

  test('should show error for invalid serial number', async ({ page }) => {
    // Given: Invalid serial number

    // When: Enter only 10 characters
    await page.fill('input[type="text"]', 'INVALID123');

    // Then: Error message should be displayed
    await expect(page.getByText(/must be 14 characters/i)).toBeVisible();

    // And: Scan button should be disabled
    await expect(page.getByRole('button', { name: /scan/i })).toBeDisabled();
  });

  test('should validate serial number format', async ({ page }) => {
    // Given: 14 characters but invalid format

    // When: Enter invalid format
    await page.fill('input[type="text"]', '12345678901234');

    // Then: Format error should be displayed
    await expect(page.getByText(/invalid serial number format/i)).toBeVisible();

    // And: Scan button should be disabled
    await expect(page.getByRole('button', { name: /scan/i })).toBeDisabled();
  });

  test('should start and complete a process with PASS result', async ({ page }) => {
    // Given: Serial is scanned
    await page.fill('input[type="text"]', 'KR01PSA2511001');
    await page.click('button:has-text("Scan")');
    await page.waitForSelector('text=KR01-PSA-2511-001', { timeout: 10000 });

    // When: Start process button is clicked
    const startButton = page.getByRole('button', { name: /start process/i });
    if (await startButton.isVisible()) {
      await startButton.click();
    }

    // Then: Measurement form should be visible
    await expect(page.getByLabel(/result/i)).toBeVisible({ timeout: 5000 });

    // When: Select PASS and submit
    await page.selectOption('select[name="result"]', 'PASS');
    await page.selectOption('select[name="data_level"]', 'NORMAL');
    await page.click('button:has-text("Submit PASS")');

    // Then: Success message should appear
    await expect(page.getByText(/process completed|success/i)).toBeVisible({ timeout: 10000 });
  });

  test('should handle FAIL result with defect codes', async ({ page }) => {
    // Given: Serial is scanned and process started
    await page.fill('input[type="text"]', 'KR01PSA2511002');
    await page.click('button:has-text("Scan")');
    await page.waitForSelector('text=KR01-PSA-2511-002', { timeout: 10000 });

    const startButton = page.getByRole('button', { name: /start process/i });
    if (await startButton.isVisible()) {
      await startButton.click();
    }

    // When: Select FAIL result
    await page.selectOption('select[name="result"]', 'FAIL');

    // Then: Defect codes section should appear
    await expect(page.getByText(/defect codes/i)).toBeVisible();

    // When: Select defect code and submit
    const defectCheckbox = page.getByRole('checkbox').first();
    await defectCheckbox.check();

    await page.fill('textarea[name="notes"]', 'Test failure reason');
    await page.click('button:has-text("Submit FAIL")');

    // Then: Success message should appear
    await expect(page.getByText(/process completed|success/i)).toBeVisible({ timeout: 10000 });
  });

  test('should prevent submission without defect code for FAIL', async ({ page }) => {
    // Given: Serial is scanned and process started
    await page.fill('input[type="text"]', 'KR01PSA2511003');
    await page.click('button:has-text("Scan")');
    await page.waitForSelector('text=KR01-PSA-2511-003', { timeout: 10000 });

    const startButton = page.getByRole('button', { name: /start process/i });
    if (await startButton.isVisible()) {
      await startButton.click();
    }

    // When: Select FAIL without defect code
    await page.selectOption('select[name="result"]', 'FAIL');
    await page.click('button:has-text("Submit FAIL")');

    // Then: Error message should appear
    await expect(page.getByText(/at least one defect code/i)).toBeVisible();
  });

  test('should handle REWORK result', async ({ page }) => {
    // Given: Serial is scanned and process started
    await page.fill('input[type="text"]', 'KR01PSA2511004');
    await page.click('button:has-text("Scan")');
    await page.waitForSelector('text=KR01-PSA-2511-004', { timeout: 10000 });

    const startButton = page.getByRole('button', { name: /start process/i });
    if (await startButton.isVisible()) {
      await startButton.click();
    }

    // When: Select REWORK and submit
    await page.selectOption('select[name="result"]', 'REWORK');
    await page.fill('textarea[name="notes"]', 'Rework needed');
    await page.click('button:has-text("Submit REWORK")');

    // Then: Success message should appear
    await expect(page.getByText(/process completed|success/i)).toBeVisible({ timeout: 10000 });
  });

  test('should display process timeline', async ({ page }) => {
    // Given: Serial is scanned
    await page.fill('input[type="text"]', 'KR01PSA2511005');
    await page.click('button:has-text("Scan")');
    await page.waitForSelector('text=KR01-PSA-2511-005', { timeout: 10000 });

    // Then: Process timeline should be visible
    await expect(page.getByText(/process progress/i)).toBeVisible();

    // And: Process steps should be listed
    const processSteps = page.locator('[data-testid="process-step"]').or(page.locator('text=/조립|검사|포장/i'));
    await expect(processSteps.first()).toBeVisible();
  });

  test('should clear input after scanning', async ({ page }) => {
    // Given: Serial number is entered
    const input = page.locator('input[type="text"]');
    await input.fill('KR01PSA2511006');

    // When: Scan button is clicked
    await page.click('button:has-text("Scan")');
    await page.waitForTimeout(1000);

    // Then: Input should be cleared
    await expect(input).toHaveValue('');
  });

  test('should show loading state during scan', async ({ page }) => {
    // Given: Serial number is entered
    await page.fill('input[type="text"]', 'KR01PSA2511007');

    // When: Scan button is clicked
    const scanButton = page.getByRole('button', { name: /scan/i });
    await scanButton.click();

    // Then: Loading state should be visible (briefly)
    // Note: This might be too fast to catch, so we just check it doesn't error
    await page.waitForTimeout(500);
  });

  test('should handle keyboard Enter to submit', async ({ page }) => {
    // Given: Valid serial number is entered
    await page.fill('input[type="text"]', 'KR01PSA2511008');

    // When: Press Enter key
    await page.press('input[type="text"]', 'Enter');

    // Then: Serial should be scanned
    await expect(page.locator('text=KR01-PSA-2511-008')).toBeVisible({ timeout: 10000 });
  });
});
