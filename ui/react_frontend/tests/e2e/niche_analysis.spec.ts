import { test, expect } from '@playwright/test';

// Adjust this URL if your dev server runs elsewhere
const BASE_URL = 'http://localhost:3000';

test.describe('Niche Analysis Workflow', () => {
  test('User can run a niche analysis and see project plan', async ({ page }) => {
    // Go to the React app
    await page.goto(BASE_URL);

    // The landing page should have a way to start niche analysis
    // Replace these selectors and text with actual ones from your UI
    await expect(page.getByText(/niche analysis/i)).toBeVisible({ timeout: 10000 });

    // Click "Start Niche Analysis" (example: adjust selector as needed)
    await page.getByRole('button', { name: /start niche analysis/i }).click();

    // Wait for analysis to complete (replace with actual UI logic)
    await expect(page.getByText(/analysis complete|project plan/i, { exact: false })).toBeVisible();

    // Optionally: expand project plan details
    await page.getByRole('button', { name: /view project plan/i }).click();

    // Check that project plan is displayed (adjust selector as needed)
    await expect(page.getByText(/niche|solution|monetization|marketing/i)).toBeVisible();

    // Optionally: take a screenshot for visual regression
    await page.screenshot({ path: 'niche-analysis-result.png', fullPage: true });
  });
});
