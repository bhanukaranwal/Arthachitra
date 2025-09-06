import { test, expect } from '@playwright/test';

test.describe('Trading Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[placeholder="Username"]', 'demo_user');
    await page.fill('input[placeholder="Password"]', 'demo_password');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
  });

  test('should display main dashboard', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Arthachitra');
    await expect(page.locator('[data-testid="chart-container"]')).toBeVisible();
    await expect(page.locator('[data-testid="orderbook-container"]')).toBeVisible();
  });

  test('should change chart symbol', async ({ page }) => {
    // Wait for chart to load
    await page.waitForSelector('[data-testid="chart-container"]');
    
    // Change symbol
    await page.click('[data-testid="symbol-selector"]');
    await page.click('text=RELIANCE');
    
    // Verify symbol changed
    await expect(page.locator('[data-testid="current-symbol"]')).toContainText('RELIANCE');
  });

  test('should switch between chart types', async ({ page }) => {
    await page.waitForSelector('[data-testid="chart-container"]');
    
    // Click chart type selector
    await page.click('[data-testid="chart-type-selector"]');
    await page.click('text=Line');
    
    // Verify chart type changed
    await expect(page.locator('[data-testid="chart-type-selector"]')).toContainText('Line');
  });

  test('should add technical indicator', async ({ page }) => {
    await page.waitForSelector('[data-testid="chart-container"]');
    
    // Open indicators menu
    await page.click('[data-testid="indicators-button"]');
    await page.click('text=RSI');
    
    // Verify indicator added
    await expect(page.locator('[data-testid="active-indicators"]')).toContainText('RSI');
  });

  test('should place market order', async ({ page }) => {
    // Navigate to order entry
    await page.click('[data-testid="order-entry-button"]');
    
    // Fill order form
    await page.fill('[data-testid="quantity-input"]', '100');
    await page.selectOption('[data-testid="order-type-select"]', 'MARKET');
    await page.click('[data-testid="buy-button"]');
    
    // Confirm order
    await page.click('[data-testid="confirm-order-button"]');
    
    // Verify order placed
    await expect(page.locator('[data-testid="order-success-message"]')).toBeVisible();
  });

  test('should display order book updates', async ({ page }) => {
    const orderBook = page.locator('[data-testid="orderbook-container"]');
    await expect(orderBook).toBeVisible();
    
    // Check for bid/ask levels
    await expect(orderBook.locator('[data-testid="bid-levels"]')).toBeVisible();
    await expect(orderBook.locator('[data-testid="ask-levels"]')).toBeVisible();
    
    // Verify spread is displayed
    await expect(orderBook.locator('[data-testid="spread-value"]')).toBeVisible();
  });

  test('should switch themes', async ({ page }) => {
    // Open theme switcher
    await page.click('[data-testid="theme-switcher"]');
    await page.click('text=Dark Pro');
    
    // Verify theme changed
    await expect(page.locator('body')).toHaveClass(/dark/);
  });

  test('should view portfolio', async ({ page }) => {
    await page.click('text=Portfolio');
    await page.waitForURL('/portfolio');
    
    // Verify portfolio elements
    await expect(page.locator('[data-testid="total-value"]')).toBeVisible();
    await expect(page.locator('[data-testid="day-pnl"]')).toBeVisible();
    await expect(page.locator('[data-testid="positions-table"]')).toBeVisible();
  });

  test('should handle WebSocket disconnection', async ({ page }) => {
    // Wait for initial connection
    await page.waitForSelector('[data-testid="connection-status"]');
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('Live');
    
    // Simulate network disconnection
    await page.context().setOffline(true);
    
    // Wait for disconnection indicator
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('Disconnected');
    
    // Restore connection
    await page.context().setOffline(false);
    
    // Verify reconnection
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('Live');
  });
});

test.describe('Order Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Username"]', 'demo_user');
    await page.fill('input[placeholder="Password"]', 'demo_password');
    await page.click('button[type="submit"]');
    await page.goto('/orders');
  });

  test('should display orders list', async ({ page }) => {
    await expect(page.locator('[data-testid="orders-table"]')).toBeVisible();
    await expect(page.locator('text=Symbol')).toBeVisible();
    await expect(page.locator('text=Quantity')).toBeVisible();
    await expect(page.locator('text=Status')).toBeVisible();
  });

  test('should cancel pending order', async ({ page }) => {
    // Find first pending order
    const firstPendingOrder = page.locator('[data-testid="order-row"]').first();
    await firstPendingOrder.locator('[data-testid="cancel-button"]').click();
    
    // Confirm cancellation
    await page.click('[data-testid="confirm-cancel-button"]');
    
    // Verify order cancelled
    await expect(page.locator('[data-testid="cancel-success-message"]')).toBeVisible();
  });
});
