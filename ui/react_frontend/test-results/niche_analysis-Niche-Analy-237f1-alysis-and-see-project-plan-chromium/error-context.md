# Test info

- Name: Niche Analysis Workflow >> User can run a niche analysis and see project plan
- Location: C:\Users\ancha\Documents\AI\pAIssive_income\ui\react_frontend\tests\e2e\niche_analysis.spec.ts:16:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/
Call log:
  - navigating to "http://localhost:3000/", waiting until "load"

    at C:\Users\ancha\Documents\AI\pAIssive_income\ui\react_frontend\tests\e2e\niche_analysis.spec.ts:18:16
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 |
   3 | // Adjust this URL if your dev server runs elsewhere
   4 | const BASE_URL = 'http://localhost:3000';
   5 |
   6 | test.describe('Niche Analysis Workflow', () => {
   7 |   // Add a hook to capture screenshots on test failure
   8 |   test.afterEach(async ({ page }, testInfo) => {
   9 |     if (testInfo.status !== 'passed') {
  10 |       // Capture a screenshot on test failure
  11 |       await page.screenshot({ path: `test-failure-${testInfo.title.replace(/\s+/g, '-')}.png`, fullPage: true });
  12 |       console.log('Test failed. Screenshot captured.');
  13 |     }
  14 |   });
  15 |
  16 |   test('User can run a niche analysis and see project plan', async ({ page }) => {
  17 |     // Go to the React app
> 18 |     await page.goto(BASE_URL);
     |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/
  19 |
  20 |     // The landing page should have a way to start niche analysis
  21 |     // Replace these selectors and text with actual ones from your UI
  22 |     // Increased timeout to 30 seconds to allow for slower API responses
  23 |     console.log('Waiting for Niche Analysis text to be visible...');
  24 |
  25 |     // First wait for navigation to complete
  26 |     await page.waitForLoadState('networkidle', { timeout: 10000 });
  27 |
  28 |     // Then wait for the element with increased timeout
  29 |     try {
  30 |       await expect(page.getByText(/niche analysis/i)).toBeVisible({ timeout: 30000 });
  31 |       console.log('Niche Analysis text is visible!');
  32 |     } catch (error) {
  33 |       console.error('Failed to find Niche Analysis text:', error);
  34 |       // Take a screenshot for debugging
  35 |       await page.screenshot({ path: 'debug-niche-analysis-not-found.png', fullPage: true });
  36 |       throw error;
  37 |     }
  38 |
  39 |     // Take a screenshot if the element is found for debugging
  40 |     await page.screenshot({ path: 'niche-analysis-found.png', fullPage: true });
  41 |
  42 |     // Click "Start Niche Analysis" (example: adjust selector as needed)
  43 |     await page.getByRole('button', { name: /start niche analysis/i }).click();
  44 |
  45 |     // Wait for analysis to complete (replace with actual UI logic)
  46 |     await expect(page.getByText(/analysis complete|project plan/i, { exact: false })).toBeVisible();
  47 |
  48 |     // Optionally: expand project plan details
  49 |     await page.getByRole('button', { name: /view project plan/i }).click();
  50 |
  51 |     // Check that project plan is displayed (adjust selector as needed)
  52 |     await expect(page.getByText(/niche|solution|monetization|marketing/i)).toBeVisible();
  53 |
  54 |     // Optionally: take a screenshot for visual regression
  55 |     await page.screenshot({ path: 'niche-analysis-result.png', fullPage: true });
  56 |   });
  57 | });
  58 |
```