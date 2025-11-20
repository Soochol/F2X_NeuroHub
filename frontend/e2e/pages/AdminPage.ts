import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Admin Page Object Model
 */
export class AdminPage extends BasePage {
  // Tabs
  readonly usersTab: Locator;
  readonly processesTab: Locator;
  readonly productsTab: Locator;

  // Buttons
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    super(page);
    this.usersTab = page.locator('button:has-text("User Management")');
    this.processesTab = page.locator('button:has-text("Process Management")');
    this.productsTab = page.locator('button:has-text("Product Models")');
    this.saveButton = page.locator('button:has-text("Save")');
    this.cancelButton = page.locator('button:has-text("Cancel")');
  }

  // Get the add button for the current tab
  get addButton(): Locator {
    return this.page.locator('button:has-text("+ Add")');
  }

  // Get input by label
  getInput(label: string): Locator {
    return this.page.locator(`label:has-text("${label}") + input, label:has-text("${label}") >> input`).first();
  }

  async goto() {
    await this.navigate('/admin');
    await this.waitForPageLoad();
  }

  async selectTab(tab: 'users' | 'processes' | 'products') {
    const tabMap = {
      users: this.usersTab,
      processes: this.processesTab,
      products: this.productsTab,
    };
    await tabMap[tab].click();
    await this.page.waitForTimeout(300);
  }

  // User Management
  async addUser(data: {
    username: string;
    fullName: string;
    email: string;
    password: string;
    role: 'ADMIN' | 'MANAGER' | 'OPERATOR';
  }) {
    await this.selectTab('users');
    await this.addButton.click();

    await this.page.fill('input[value=""]', data.username, { strict: false });
    await this.page.locator('input').nth(0).fill(data.username);
    await this.page.locator('input').nth(1).fill(data.fullName);
    await this.page.locator('input[type="email"]').fill(data.email);
    await this.page.locator('input[type="password"]').fill(data.password);

    await this.page.locator('select').selectOption(data.role);
    await this.saveButton.click();
  }

  // Process Management
  async addProcess(data: {
    processNumber: number;
    processCode: string;
    nameKo: string;
    nameEn: string;
    sortOrder: number;
  }) {
    await this.selectTab('processes');
    await this.addButton.click();

    // Wait for modal to appear
    await this.page.waitForSelector('text=Save', { state: 'visible' });

    // Fill form - find input by its sibling label text
    await this.page.locator('label:has-text("Process Number") ~ input').fill(String(data.processNumber));
    await this.page.locator('label:has-text("Process Code") ~ input').fill(data.processCode);
    await this.page.locator('label:has-text("Process Name (Korean)") ~ input').fill(data.nameKo);
    await this.page.locator('label:has-text("Process Name (English)") ~ input').fill(data.nameEn);
    await this.page.locator('label:has-text("Sort Order") ~ input').fill(String(data.sortOrder));

    await this.saveButton.click();
  }

  // Product Model Management
  async addProductModel(data: {
    modelCode: string;
    modelName: string;
    category?: string;
  }) {
    await this.selectTab('products');
    await this.addButton.click();

    // Wait for modal to appear
    await this.page.waitForSelector('text=Save', { state: 'visible' });

    // Fill form - find input by its sibling label text
    await this.page.locator('label:has-text("Model Code") ~ input').fill(data.modelCode);
    await this.page.locator('label:has-text("Model Name") ~ input').fill(data.modelName);
    if (data.category) {
      await this.page.locator('label:has-text("Category") ~ input').fill(data.category);
    }

    await this.saveButton.click();
  }

  async getTableRowCount() {
    return await this.page.locator('tbody tr').count();
  }

  async deleteFirstItem() {
    this.page.on('dialog', dialog => dialog.accept());
    await this.page.locator('button:has-text("Delete")').first().click();
    await this.page.waitForTimeout(500);
  }
}
