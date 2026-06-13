---
name: playwright-testing
description: Playwright E2E testing conventions. Use when writing, running, or maintaining end-to-end tests.
---

# Playwright E2E Testing Conventions

## File Locations

- Test files: `tests/e2e/PRD-XXX.spec.ts` (same number as the PRD)
- Page Objects: `tests/e2e/pages/<page-name>.ts`
- Test data: `tests/e2e/fixtures/`
- Config: `playwright.config.ts`

## Required Test File Header

Every .spec.ts file links to its documents via JSDoc:

```typescript
/**
 * @prd PRD-008 User Points Deduction
 * @spec SPEC-008
 * @test-plan TEST-PLAN-008
 * @scope happy-path + key error cases
 */
```

## Writing Rules

### 1. Prefer Semantic Locators

```typescript
// ❌ Fragile
await page.click('.btn-primary');

// ✅ Recommended
await page.getByRole('button', { name: 'Submit Order' }).click();
await page.getByLabel('Email').fill('user@example.com');
await page.getByTestId('checkout-btn-submit').click();
```

Priority: getByRole > getByLabel > getByTestId > others

### 2. Page Object Encapsulation

Use the Page Object pattern for complex pages:

```typescript
// tests/e2e/pages/checkout-page.ts
export class CheckoutPage {
  constructor(private page: Page) {}
  
  async applyPoints(amount: number) {
    await this.page.getByTestId('checkout-input-points').fill(String(amount));
    await this.page.getByTestId('checkout-btn-apply-points').click();
  }
  
  async submitOrder() {
    await this.page.getByTestId('checkout-btn-submit').click();
  }
  
  async expectOrderSuccess() {
    await expect(this.page.getByTestId('order-confirmation')).toBeVisible();
  }
}
```

### 3. Data Isolation (fixture)

Give each test its own data and clean it up after the run:

```typescript
const test = base.extend<{ testUser: User }>({
  testUser: async ({}, use) => {
    const user = await createTestUser();
    await use(user);
    await deleteTestUser(user.id);
  }
});
```

### 4. Waiting Strategy

```typescript
// ❌ Don't
await page.waitForTimeout(3000);

// ✅ Wait for an element to appear
await expect(page.getByText('Order Successful')).toBeVisible();

// ✅ Wait for the network to go idle
await page.waitForLoadState('networkidle');

// ✅ Wait for the URL to change
await page.waitForURL('/order/success');
```

### 5. Accessibility Scan (recommended to include)

```typescript
import AxeBuilder from '@axe-core/playwright';

test('PRD-008 checkout page a11y', async ({ page }) => {
  await page.goto('/checkout');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

## Test Structure Example

```typescript
/**
 * @prd PRD-008 User Points Deduction
 * @spec SPEC-008
 * @test-plan TEST-PLAN-008
 */
import { test, expect } from '@playwright/test';
import { CheckoutPage } from './pages/checkout-page';

test.describe('PRD-008 User Points Deduction', () => {
  let checkoutPage: CheckoutPage;
  
  test.beforeEach(async ({ page, testUser }) => {
    checkoutPage = new CheckoutPage(page);
    await page.goto('/checkout');
  });

  // Happy path (PRD acceptance criterion #1)
  test('user can deduct 1 yuan with 100 points', async ({ page }) => {
    await checkoutPage.applyPoints(100);
    await expect(page.getByTestId('checkout-discount')).toContainText('-¥1.00');
    await checkoutPage.submitOrder();
    await checkoutPage.expectOrderSuccess();
  });

  // Error path 1 (PRD acceptance criterion #3)
  test('shows an error when points exceed the balance', async ({ page }) => {
    await checkoutPage.applyPoints(99999);
    await expect(page.getByTestId('checkout-points-error')).toBeVisible();
  });

  // Error path 2 (PRD acceptance criterion #5)
  test('points deduction does not exceed 50% of the order amount', async ({ page }) => {
    // ... omitted
  });
});
```

## Running Tests

```bash
# All
npx playwright test

# A single PRD
npx playwright test tests/e2e/PRD-008.spec.ts

# UI mode (debugging)
npx playwright test --ui

# Only the failed ones
npx playwright test --last-failed
```

## Scale Guidance

- Per PRD: 1 happy path + 1-2 key error cases
- The full suite runs in < 15 minutes
- Slow tests (> 30 seconds) should be moved to nightly runs

## Anti-Patterns

- ❌ `page.waitForTimeout(N)` — use expect/waitFor instead
- ❌ Clicking a CSS selector directly — use getByRole/getByLabel/getByTestId
- ❌ Writing business logic in tests — business logic belongs in fixtures / Page Objects
- ❌ Sharing state between tests
- ❌ Tests depending on production data
- ❌ One test covering every scenario
