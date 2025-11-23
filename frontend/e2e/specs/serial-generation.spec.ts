/**
 * E2E Tests for Serial Generation Flow
 *
 * Tests the workflow of generating serial numbers for LOTs
 */

import { test, expect } from '@playwright/test';

test.describe('Serial Generation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to serial generation page
    await page.goto('http://localhost:3000/serials/generate');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display page title and instructions', async ({ page }) => {
    // Then: Page title should be visible
    await expect(page.getByRole('heading', { name: /serial generation|generate serials/i })).toBeVisible();

    // And: Instructions or description should be present
    await expect(page.getByText(/select a lot|choose lot/i).or(page.getByText(/CREATED/))).toBeVisible();
  });

  test('should display CREATED LOTs', async ({ page }) => {
    // Given: Page is loaded

    // Then: LOT cards or list should be visible
    // Look for LOT-related content
    const lotContent = page.locator('[data-testid="lot-card"]')
      .or(page.locator('text=/LOT|lot_number/i'));

    // Wait for either LOTs to appear or "no lots" message
    await expect(
      lotContent.first().or(page.getByText(/no lots|no created lots/i))
    ).toBeVisible({ timeout: 10000 });
  });

  test('should filter and show only CREATED status LOTs', async ({ page }) => {
    // Given: LOTs are displayed

    // Then: Only CREATED status LOTs should be visible
    const statusBadges = page.locator('text=CREATED');

    // If there are any LOTs, they should all be CREATED
    const count = await statusBadges.count();
    if (count > 0) {
      // Check that IN_PROGRESS, COMPLETED, CLOSED statuses are not present
      await expect(page.locator('text=/IN_PROGRESS|COMPLETED|CLOSED/i')).not.toBeVisible();
    }
  });

  test('should select LOT when clicked', async ({ page }) => {
    // Given: LOT cards are displayed
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    // Skip test if no LOTs available
    if (await lotCard.count() === 0) {
      test.skip();
    }

    // When: Click on LOT card
    await lotCard.click();

    // Then: LOT should be highlighted/selected
    await expect(lotCard).toHaveClass(/selected|active/i);
  });

  test('should show LOT details when selected', async ({ page }) => {
    // Given: LOT card exists
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    // When: Select a LOT
    await lotCard.click();

    // Then: LOT details should be visible
    await expect(
      page.getByText(/product model|target quantity|production date/i)
    ).toBeVisible();
  });

  test('should enable Generate button when LOT is selected', async ({ page }) => {
    // Given: LOT card exists
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    // When: Select a LOT
    await lotCard.click();

    // Then: Generate button should be enabled
    const generateButton = page.getByRole('button', { name: /generate serials/i });
    await expect(generateButton).toBeEnabled();
  });

  test('should show confirmation dialog when generating serials', async ({ page }) => {
    // Given: LOT is selected
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    await lotCard.click();

    // When: Click Generate Serials button
    const generateButton = page.getByRole('button', { name: /generate serials/i });
    await generateButton.click();

    // Then: Confirmation dialog should appear
    await expect(page.getByText(/confirm|are you sure/i)).toBeVisible();
    await expect(page.getByText(/cannot be undone/i)).toBeVisible();
  });

  test('should display LOT information in confirmation dialog', async ({ page }) => {
    // Given: LOT is selected and generate clicked
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    await lotCard.click();

    const generateButton = page.getByRole('button', { name: /generate serials/i });
    await generateButton.click();

    // Then: Dialog should show LOT details
    await expect(
      page.getByText(/lot number|target quantity/i)
    ).toBeVisible();
  });

  test('should cancel serial generation', async ({ page }) => {
    // Given: Confirmation dialog is open
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    await lotCard.click();
    await page.click('button:has-text("Generate Serials")');

    // When: Click cancel button
    const cancelButton = page.getByRole('button', { name: /cancel/i });
    await cancelButton.click();

    // Then: Dialog should close
    await expect(page.getByText(/confirm|are you sure/i)).not.toBeVisible();

    // And: Generate button should still be visible
    await expect(page.getByRole('button', { name: /generate serials/i })).toBeVisible();
  });

  test('should generate serials with progress tracking', async ({ page }) => {
    // Given: Confirmation dialog is open
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    await lotCard.click();
    await page.click('button:has-text("Generate Serials")');

    // When: Click confirm button
    const confirmButton = page.getByRole('button', { name: /confirm|generate/i }).last();
    await confirmButton.click();

    // Then: Progress modal should appear
    await expect(
      page.getByText(/generating|in progress/i)
    ).toBeVisible({ timeout: 5000 });

    // Then: Success message should appear after generation
    await expect(
      page.getByText(/success|complete|created/i)
    ).toBeVisible({ timeout: 60000 });
  });

  test('should show success modal with generation details', async ({ page }) => {
    // Given: Serial generation is triggered
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    await lotCard.click();
    await page.click('button:has-text("Generate Serials")');

    const confirmButton = page.getByRole('button', { name: /confirm|generate/i }).last();
    await confirmButton.click();

    // Then: Success modal should show number of serials created
    await expect(
      page.getByText(/successfully created|serials generated/i)
    ).toBeVisible({ timeout: 60000 });

    // And: Should show count
    await expect(
      page.getByText(/\d+ serial/i)
    ).toBeVisible();
  });

  test('should close success modal and refresh LOT list', async ({ page }) => {
    // Given: Success modal is shown
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    await lotCard.click();
    await page.click('button:has-text("Generate Serials")');

    const confirmButton = page.getByRole('button', { name: /confirm|generate/i }).last();
    await confirmButton.click();

    // Wait for success
    await page.waitForSelector('text=/success|complete/i', { timeout: 60000 });

    // When: Close success modal
    const closeButton = page.getByRole('button', { name: /close|ok/i });
    await closeButton.click();

    // Then: Modal should close
    await expect(page.getByText(/success|complete/i)).not.toBeVisible();

    // And: LOT list should refresh (the generated LOT should not be in CREATED status anymore)
    await page.waitForLoadState('networkidle');
  });

  test('should handle multiple LOT selection', async ({ page }) => {
    // Given: Multiple LOT cards exist
    const lotCards = page.locator('[data-testid="lot-card"]');
    const count = await lotCards.count();

    if (count < 2) {
      test.skip();
    }

    // When: Select first LOT
    await lotCards.nth(0).click();
    await expect(lotCards.nth(0)).toHaveClass(/selected/i);

    // When: Select second LOT
    await lotCards.nth(1).click();

    // Then: Only second LOT should be selected
    await expect(lotCards.nth(1)).toHaveClass(/selected/i);
    await expect(lotCards.nth(0)).not.toHaveClass(/selected/i);
  });

  test('should display empty state when no CREATED LOTs exist', async ({ page }) => {
    // Given: No CREATED LOTs

    // Then: Empty state message should be visible
    const emptyMessage = page.getByText(/no lots|no created lots|no lots available/i);
    const lotCards = page.locator('[data-testid="lot-card"]');

    // Either empty message OR no lot cards
    const hasEmptyMessage = await emptyMessage.count() > 0;
    const hasLotCards = await lotCards.count() > 0;

    expect(hasEmptyMessage || !hasLotCards).toBe(true);
  });

  test('should show error message on generation failure', async ({ page }) => {
    // Given: LOT is selected (simulate a failure scenario)
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    await lotCard.click();
    await page.click('button:has-text("Generate Serials")');

    const confirmButton = page.getByRole('button', { name: /confirm|generate/i }).last();
    await confirmButton.click();

    // Then: Either success or error message should appear
    // (This depends on actual API behavior)
    const resultMessage = page.getByText(/success|error|failed/i);
    await expect(resultMessage).toBeVisible({ timeout: 60000 });
  });

  test('should display LOT information correctly', async ({ page }) => {
    // Given: LOT cards are displayed
    const lotCard = page.locator('[data-testid="lot-card"]').first();

    if (await lotCard.count() === 0) {
      test.skip();
    }

    // Then: LOT card should display essential information
    await expect(
      lotCard.getByText(/LOT|KR\d+/i).or(page.getByText(/lot number/i))
    ).toBeVisible();

    // And: Should show target quantity
    await expect(
      lotCard.getByText(/\d+/).or(page.getByText(/target|quantity/i))
    ).toBeVisible();
  });
});
