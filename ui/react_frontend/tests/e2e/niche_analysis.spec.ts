import { test, expect } from '@playwright/test';

// Adjust this URL if your dev server runs elsewhere
const BASE_URL = 'http://localhost:3000';

test.describe('Niche Analysis Workflow', () => {
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
    await page.waitForLoadState('load', { timeout: 10000 });

    // Step 1: Ensure the Niche Analysis entry point is visible
    const nicheAnalysisText = page.getByText(/niche analysis/i);
    await nicheAnalysisText.waitFor({ timeout: 30000 });
    await expect(nicheAnalysisText).toBeVisible();

    // Accessibility: The Niche Analysis element is focusable
    await expect(nicheAnalysisText).toHaveAttribute('tabindex', /-?1|0/);

    await page.screenshot({ path: 'niche-analysis-found.png', fullPage: true });

    // Step 2: Start analysis; button is enabled, has ARIA label
    const startButton = page.getByRole('button', { name: /start niche analysis/i });
    await expect(startButton).toBeEnabled();
    await expect(startButton).toHaveAttribute(/aria-label/i, /start niche analysis/i);
    await startButton.focus();
    await expect(startButton).toBeFocused();
    await startButton.press('Enter');

    // Step 3: Loading state: spinner/progress bar shown, button disabled
    const loadingSpinner = await page.waitForSelector('[role=progressbar], .MuiCircularProgress-root, .spinner', { timeout: 10000 });
    expect(loadingSpinner).not.toBeNull();
    await expect(startButton).toBeDisabled();

    // Step 4: Wait for analysis to complete
    const analysisCompleteText = page.getByText(/analysis complete|project plan/i, { exact: false });
    await analysisCompleteText.waitFor({ timeout: 30000 });
    await expect(analysisCompleteText).toBeVisible();

    // Step 5: Expand project plan details, keyboard accessible
    const viewPlanButton = page.getByRole('button', { name: /view project plan/i });
    await expect(viewPlanButton).toBeVisible();
    await viewPlanButton.focus();
    await expect(viewPlanButton).toBeFocused();
    await viewPlanButton.press('Space');

    const projectPlanText = page.getByText(/niche|solution|monetization|marketing/i);
    await projectPlanText.waitFor({ timeout: 10000 });
    await expect(projectPlanText).toBeVisible();

    // Accessibility: project plan region is labelled
    const region = await page.$('[role=region][aria-label*="project plan"], [aria-labelledby*="project-plan"]');
    expect(region).not.toBeNull();

    await page.screenshot({ path: 'niche-analysis-result.png', fullPage: true });
  });

  test('Shows error message if analysis fails', async ({ page }) => {
    // This assumes you can trigger a backend/API failure, e.g., via query param, mock, or by disabling network.
    await page.goto(BASE_URL + '?mock_niche_analysis=fail', { timeout: 10000 });
    await page.waitForLoadState('load', { timeout: 10000 });

    // Start analysis (simulate API failure)
    const startButton = page.getByRole('button', { name: /start niche analysis/i });
    await startButton.click();

    // Wait for error message to appear
    const errorMsg = await page.getByText(/failed|error|could not complete niche analysis/i, { exact: false, timeout: 20000 });
    await expect(errorMsg).toBeVisible();
    await page.screenshot({ path: 'niche-analysis-error.png', fullPage: true });
  });
});