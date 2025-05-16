import { test, expect } from '@playwright/test';

// Adjust this URL if your dev server runs elsewhere
const BASE_URL = 'http://localhost:3000';

test.describe.skip('Niche Analysis Workflow', () => {
  // Add a hook to capture screenshots on test failure
  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status !== 'passed') {
      // Capture a screenshot on test failure
      await page.screenshot({ path: `test-failure-${testInfo.title.replace(/\s+/g, '-')}.png`, fullPage: true });
      console.log('Test failed. Screenshot captured.');
    }
  });

  test.beforeEach(async ({ page }) => {
    // Check if the app is running before proceeding
    try {
      await page.goto(BASE_URL, { timeout: 5000 });
      console.log('Successfully connected to the React app');
    } catch (error) {
      console.error('Could not connect to the React app. Is it running?');
      console.error('To run the app: pnpm start');
      test.skip();
    }
  });

  test('User can run a niche analysis and see project plan', async ({ page }) => {
    // Go to the React app (already done in beforeEach)

    // The landing page should have a way to start niche analysis
    // Replace these selectors and text with actual ones from your UI
    // Increased timeout to 30 seconds to allow for slower API responses
    console.log('Waiting for Niche Analysis text to be visible...');

    // First wait for navigation to complete
    await page.waitForLoadState('load', { timeout: 10000 });

    // Then wait for the element with increased timeout
    // Wait for the niche analysis text to be visible
    const nicheAnalysisText = page.getByText(/niche analysis/i);
    await nicheAnalysisText.waitFor({ timeout: 30000 });
    await expect(nicheAnalysisText).toBeVisible();
    console.log('Niche Analysis text is visible!');

    // Take a screenshot if the element is found for debugging
    await page.screenshot({ path: 'niche-analysis-found.png', fullPage: true });

    // Click "Start Niche Analysis" (example: adjust selector as needed)
    const startButton = page.getByRole('button', { name: /start niche analysis/i });
    await startButton.click();

    // Wait for analysis to complete (replace with actual UI logic)
    const analysisCompleteText = page.getByText(/analysis complete|project plan/i, { exact: false });
    await analysisCompleteText.waitFor({ timeout: 30000 });
    await expect(analysisCompleteText).toBeVisible();

    // Optionally: expand project plan details
    const viewPlanButton = page.getByRole('button', { name: /view project plan/i });
    await viewPlanButton.click();

    // Check that project plan is displayed (adjust selector as needed)
    const projectPlanText = page.getByText(/niche|solution|monetization|marketing/i);
    await projectPlanText.waitFor({ timeout: 10000 });
    await expect(projectPlanText).toBeVisible();

    // Optionally: take a screenshot for visual regression
    await page.screenshot({ path: 'niche-analysis-result.png', fullPage: true });
  });
});