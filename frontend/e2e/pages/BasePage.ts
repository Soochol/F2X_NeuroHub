import { Page, Locator } from '@playwright/test';

/**
 * Base Page Object Model
 */
export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async navigate(path: string) {
    await this.page.goto(path);
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  async clickButton(text: string) {
    await this.page.click(`button:has-text("${text}")`);
  }

  async fillInput(label: string, value: string) {
    const input = this.page.locator(`label:has-text("${label}") + input, label:has-text("${label}") input`);
    await input.fill(value);
  }

  async selectOption(label: string, value: string) {
    const select = this.page.locator(`label:has-text("${label}") + select, label:has-text("${label}") select`);
    await select.selectOption(value);
  }
}
