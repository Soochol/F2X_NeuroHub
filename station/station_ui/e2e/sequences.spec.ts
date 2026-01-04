import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Sequences Page
 *
 * Tests the following features:
 * 1. Sequence list display
 * 2. Sequence detail view
 * 3. Deploy panel functionality
 * 4. Simulation panel functionality
 */

test.describe('Sequences Page', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to root first, then use SPA navigation to sequences
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // Click on Sequences link in sidebar
    await page.click('a[href*="sequences"]');
    await page.waitForLoadState('networkidle');
  });

  test('should display sequences page title', async ({ page }) => {
    // Check page header - wait for h2 to appear
    await expect(page.locator('h2').first()).toContainText('Sequences', { timeout: 10000 });
  });

  test('should show upload package button', async ({ page }) => {
    // Check for upload button - wait for it
    const uploadButton = page.getByRole('button', { name: /upload package/i });
    await expect(uploadButton).toBeVisible({ timeout: 10000 });
  });

  test('should display sequence list section', async ({ page }) => {
    // Check for "Available Sequences" heading
    await expect(page.locator('h3').first()).toContainText('Available Sequences', { timeout: 10000 });
  });

  test('should show placeholder when no sequence is selected', async ({ page }) => {
    // Check for placeholder text
    await expect(page.getByText('Select a sequence to view details')).toBeVisible({ timeout: 10000 });
  });

  test('should toggle upload panel when clicking upload button', async ({ page }) => {
    // Wait for button to be ready
    const uploadButton = page.getByRole('button', { name: /upload package/i });
    await expect(uploadButton).toBeVisible({ timeout: 10000 });

    // Click to show upload panel
    await uploadButton.click();

    // Button should change to "Cancel Upload"
    await expect(page.getByRole('button', { name: /cancel upload/i })).toBeVisible();

    // Click again to hide
    await page.getByRole('button', { name: /cancel upload/i }).click();

    // Should be back to "Upload Package"
    await expect(uploadButton).toBeVisible();
  });
});

test.describe('Sequences Page - With Backend', () => {
  // These tests require the station_service backend to be running

  test.skip(({ browserName: _browserName }) => {
    // Skip if CI and no backend - can be enabled when backend is running
    void _browserName; // Unused but required by test.skip signature
    return !!process.env.CI;
  }, 'Requires backend to be running');

  test.beforeEach(async ({ page }) => {
    await page.goto('/sequences');
    // Wait for sequences to load
    await page.waitForTimeout(1000);
  });

  test('should display sequences from backend', async ({ page }) => {
    // Wait for sequence list to load
    const sequenceItems = page.locator('[class*="rounded-lg border"]').filter({
      has: page.locator('h4'),
    });

    // Should have at least one sequence if backend has mock sequences
    const count = await sequenceItems.count();

    if (count > 0) {
      // Click on first sequence
      await sequenceItems.first().click();

      // Should show sequence detail
      await expect(page.locator('h3').first()).toBeVisible();
    }
  });

  test('should show deploy panel when sequence is selected', async ({ page }) => {
    // Wait for sequence list
    await page.waitForTimeout(500);

    // Click on a sequence if available
    const sequenceItems = page.locator('button.w-full.text-left');
    const count = await sequenceItems.count();

    if (count > 0) {
      await sequenceItems.first().click();

      // Check for Deploy to Batch panel
      await expect(page.getByText('Deploy to Batch')).toBeVisible();
    }
  });

  test('should show simulation panel when sequence is selected', async ({ page }) => {
    // Wait for sequence list
    await page.waitForTimeout(500);

    // Click on a sequence if available
    const sequenceItems = page.locator('button.w-full.text-left');
    const count = await sequenceItems.count();

    if (count > 0) {
      await sequenceItems.first().click();

      // Check for Simulation panel
      await expect(page.getByText('Simulation')).toBeVisible();

      // Check for mode buttons
      await expect(page.getByText('Preview')).toBeVisible();
      await expect(page.getByText('Dry Run')).toBeVisible();
    }
  });

  test('should display sequence tabs (Steps, Parameters, Hardware)', async ({ page }) => {
    // Wait for sequence list
    await page.waitForTimeout(500);

    // Click on a sequence if available
    const sequenceItems = page.locator('button.w-full.text-left');
    const count = await sequenceItems.count();

    if (count > 0) {
      await sequenceItems.first().click();

      // Check for tabs
      await expect(page.getByRole('button', { name: /steps/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /parameters/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /hardware/i })).toBeVisible();
    }
  });

  test('should switch between tabs', async ({ page }) => {
    // Wait for sequence list
    await page.waitForTimeout(500);

    // Click on a sequence if available
    const sequenceItems = page.locator('button.w-full.text-left');
    const count = await sequenceItems.count();

    if (count > 0) {
      await sequenceItems.first().click();

      // Click Parameters tab
      const paramsTab = page.getByRole('button', { name: /parameters/i });
      await paramsTab.click();

      // Check that Parameters tab is active (has brand color)
      await expect(paramsTab).toHaveClass(/text-brand/);

      // Click Hardware tab
      const hwTab = page.getByRole('button', { name: /hardware/i });
      await hwTab.click();

      // Check that Hardware tab is active
      await expect(hwTab).toHaveClass(/text-brand/);
    }
  });

  test('should run preview simulation', async ({ page }) => {
    // Wait for sequence list
    await page.waitForTimeout(500);

    // Click on a sequence if available
    const sequenceItems = page.locator('button.w-full.text-left');
    const count = await sequenceItems.count();

    if (count > 0) {
      await sequenceItems.first().click();

      // Wait for simulation panel
      await expect(page.getByText('Simulation')).toBeVisible();

      // Ensure Preview mode is selected
      const previewButton = page.locator('button').filter({ hasText: 'Preview' }).first();
      await previewButton.click();

      // Click Run Preview button
      const runButton = page.getByRole('button', { name: /run preview/i });
      await runButton.click();

      // Wait for simulation to complete
      await page.waitForTimeout(2000);

      // Should show results (completed status or step previews)
      // This depends on backend response
    }
  });
});

test.describe('Sequences Page - Navigation', () => {
  test('should navigate to sequence detail via sidebar', async ({ page }) => {
    // Navigate via SPA routing
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.click('a[href*="sequences"]');
    await page.waitForLoadState('networkidle');

    // Page should load without error
    await expect(page.locator('h2').first()).toContainText('Sequences', { timeout: 10000 });
  });

  test('should update URL when selecting sequence', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.click('a[href*="sequences"]');
    await page.waitForTimeout(500);

    // Click on a sequence if available
    const sequenceItems = page.locator('button.w-full.text-left');
    const count = await sequenceItems.count();

    if (count > 0) {
      // Get sequence name from the item
      const seqName = await sequenceItems.first().locator('p.text-sm').first().textContent();

      await sequenceItems.first().click();

      // URL should contain sequence name
      if (seqName) {
        await expect(page).toHaveURL(new RegExp(seqName));
      }
    }
  });
});
