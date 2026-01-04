/**
 * Manual Test E2E 테스트.
 *
 * 테스트 대상: Manual Test 탭 전체 워크플로우
 */

import { test, expect, type Page } from '@playwright/test';

// 테스트 설정
const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test.describe('Manual Test E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Manual Control 페이지로 이동
    await page.goto(`${BASE_URL}/ui/manual`);

    // Manual Test 탭 클릭
    await page.click('text=Manual Test');

    // 탭이 활성화될 때까지 대기
    await expect(page.locator('text=Real Hardware Mode')).toBeVisible();
  });

  // =========================================================================
  // E2E-01: 전체 워크플로우
  // =========================================================================
  test('E2E-01: complete workflow - create, initialize, run steps, finalize', async ({
    page,
  }) => {
    // 1. 시퀀스 선택
    const sequenceSelect = page.locator('select').first();
    await sequenceSelect.selectOption({ index: 1 }); // 첫 번째 시퀀스 선택

    // 2. 세션 생성
    await page.click('text=Create Session');
    await expect(page.locator('text=Connect & Initialize')).toBeVisible({
      timeout: 10000,
    });

    // 3. 초기화 (하드웨어 연결)
    await page.click('text=Connect & Initialize');

    // 4. Ready 상태 확인 (하드웨어 연결 시간 고려)
    await expect(page.locator('[data-testid="session-status"]')).toContainText(
      'ready',
      { timeout: 30000 }
    );

    // 5. 스텝 실행
    const runButtons = page.locator('button:has-text("Run")');
    const buttonCount = await runButtons.count();

    for (let i = 0; i < buttonCount; i++) {
      const button = runButtons.nth(i);
      if (await button.isVisible()) {
        await button.click();
        // 스텝 완료 대기
        await page.waitForTimeout(1000);
      }
    }

    // 6. Finalize
    await page.click('text=Finalize');

    // 7. 완료 상태 확인
    await expect(page.locator('[data-testid="session-status"]')).toContainText(
      'completed',
      { timeout: 10000 }
    );
  });

  // =========================================================================
  // E2E-02: 스텝 건너뛰기
  // =========================================================================
  test('E2E-02: skip step workflow', async ({ page }) => {
    // 세션 생성 및 초기화
    const sequenceSelect = page.locator('select').first();
    await sequenceSelect.selectOption({ index: 1 });
    await page.click('text=Create Session');
    await expect(page.locator('text=Connect & Initialize')).toBeVisible();
    await page.click('text=Connect & Initialize');

    // Ready 상태 대기
    await page.waitForTimeout(5000);

    // Skip 버튼이 있는 스텝 찾아서 건너뛰기
    const skipButton = page.locator('button:has-text("Skip")').first();
    if (await skipButton.isVisible()) {
      await skipButton.click();

      // Skipped 상태 확인
      await expect(page.locator('text=skipped')).toBeVisible({ timeout: 5000 });
    }
  });

  // =========================================================================
  // E2E-03: 세션 중단
  // =========================================================================
  test('E2E-03: abort session', async ({ page }) => {
    // 세션 생성 및 초기화
    const sequenceSelect = page.locator('select').first();
    await sequenceSelect.selectOption({ index: 1 });
    await page.click('text=Create Session');
    await expect(page.locator('text=Connect & Initialize')).toBeVisible();
    await page.click('text=Connect & Initialize');

    // 초기화 대기
    await page.waitForTimeout(3000);

    // Abort 버튼 클릭
    const abortButton = page.locator('button:has-text("Abort")');
    if (await abortButton.isVisible()) {
      await abortButton.click();

      // Aborted 상태 확인
      await expect(page.locator('text=aborted')).toBeVisible({ timeout: 5000 });
    }
  });

  // =========================================================================
  // E2E-04: 하드웨어 직접 명령
  // =========================================================================
  test('E2E-04: hardware direct command', async ({ page }) => {
    // 세션 생성 및 초기화
    const sequenceSelect = page.locator('select').first();
    await sequenceSelect.selectOption({ index: 1 });
    await page.click('text=Create Session');
    await expect(page.locator('text=Connect & Initialize')).toBeVisible();
    await page.click('text=Connect & Initialize');

    // Ready 상태 대기
    await page.waitForTimeout(5000);

    // 하드웨어 선택
    const hwSelect = page.locator('select').nth(1); // 두 번째 select는 하드웨어
    const options = await hwSelect.locator('option').allTextContents();

    if (options.length > 1) {
      await hwSelect.selectOption({ index: 1 });

      // 명령 버튼 클릭
      const commandButton = page.locator('[data-testid="command-button"]').first();
      if (await commandButton.isVisible()) {
        await commandButton.click();

        // 결과 확인
        await expect(page.locator('text=Success').or(page.locator('text=Failed'))).toBeVisible({
          timeout: 5000,
        });
      }
    }
  });

  // =========================================================================
  // E2E-05: 세션 리셋
  // =========================================================================
  test('E2E-05: reset session', async ({ page }) => {
    // 세션 생성
    const sequenceSelect = page.locator('select').first();
    await sequenceSelect.selectOption({ index: 1 });
    await page.click('text=Create Session');
    await expect(page.locator('text=Connect & Initialize')).toBeVisible();

    // Reset 버튼 클릭
    await page.click('text=Reset');

    // 초기 상태로 복귀 확인
    await expect(page.locator('text=Create Manual Test Session')).toBeVisible({
      timeout: 5000,
    });
  });

  // =========================================================================
  // UI 요소 테스트
  // =========================================================================
  test('UI-01: should render sequence selection', async ({ page }) => {
    // 시퀀스 선택 드롭다운 확인
    await expect(page.locator('text=Select Sequence')).toBeVisible();
    await expect(page.locator('select').first()).toBeVisible();
  });

  test('UI-02: should show session controls after creation', async ({ page }) => {
    // 세션 생성
    const sequenceSelect = page.locator('select').first();
    await sequenceSelect.selectOption({ index: 1 });
    await page.click('text=Create Session');

    // 세션 컨트롤 표시 확인
    await expect(page.locator('text=Connect & Initialize')).toBeVisible();
    await expect(page.locator('text=Reset')).toBeVisible();
  });

  test('should display real hardware warning banner', async ({ page }) => {
    // 경고 배너 확인
    await expect(page.locator('text=Real Hardware Mode')).toBeVisible();
    await expect(
      page.locator('text=This connects to actual hardware')
    ).toBeVisible();
  });
});

// 헬퍼 함수: 세션 생성 및 초기화
async function createAndInitializeSession(page: Page): Promise<void> {
  // 시퀀스 선택
  const sequenceSelect = page.locator('select').first();
  await sequenceSelect.selectOption({ index: 1 });

  // 세션 생성
  await page.click('text=Create Session');
  await expect(page.locator('text=Connect & Initialize')).toBeVisible();

  // 초기화
  await page.click('text=Connect & Initialize');

  // Ready 상태 대기
  await page.waitForTimeout(5000);
}
