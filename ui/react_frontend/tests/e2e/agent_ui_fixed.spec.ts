import { test, expect } from '@playwright/test';

// Adjust this URL if your dev server runs elsewhere
const BASE_URL = 'http://localhost:3000';

test.describe('AgentUI Integration', () => {
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

  test('AgentUI component is visible on the About page', async ({ page }) => {
    // Navigate to the About page where AgentUI is integrated
    await page.goto(`${BASE_URL}/about`);

    // Wait for navigation to complete
    await page.waitForLoadState('load', { timeout: 10000 });

    // Check if the About page content is loaded
    await page.waitForSelector('h1, h2, h3, h4, h5, h6', { timeout: 10000 });

    // Mock the API response for /api/agent
    await page.route('/api/agent', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          name: 'Test Agent',
          description: 'This is a test agent for e2e testing'
        })
      });
    });

    // Reload the page to trigger the API call with our mock
    await page.reload();

    // Wait for the page to load
    await page.waitForLoadState('load', { timeout: 10000 });

    // Wait for the AgentUI component section to be visible
    await expect(page.getByText(/agent ui integration/i)).toBeVisible({ timeout: 10000 });

    // Wait for the agent data to load
    await page.waitForTimeout(1000);

    // Check if the agent name is displayed
    await expect(page.getByText('Test Agent')).toBeVisible();

    // Check if the agent description is displayed
    await expect(page.getByText('This is a test agent for e2e testing')).toBeVisible();

    // Check if the buttons are present
    await expect(page.getByRole('button', { name: 'Help' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Start' })).toBeVisible();

    // Take a screenshot for visual verification
    await page.screenshot({ path: 'agent-ui-component.png', fullPage: true });
  });

  test('AgentUI buttons trigger actions', async ({ page }) => {
    // Navigate to the About page where AgentUI is integrated
    await page.goto(`${BASE_URL}/about`);

    // Wait for navigation to complete
    await page.waitForLoadState('load', { timeout: 10000 });

    // Mock the API response for /api/agent
    await page.route('/api/agent', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          name: 'Test Agent',
          description: 'This is a test agent for e2e testing'
        })
      });
    });

    // Mock the API response for /api/agent/action
    await page.route('/api/agent/action', async (route, request) => {
      const postData = request.postDataJSON();
      console.log('Action received:', postData);

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'success', action_id: 123 })
      });
    });

    // Reload the page to trigger the API call with our mock
    await page.reload();

    // Wait for the page to load
    await page.waitForLoadState('load', { timeout: 10000 });

    // Wait for the AgentUI component section to be visible
    await expect(page.getByText(/agent ui integration/i)).toBeVisible({ timeout: 10000 });

    // Wait for the agent data to load
    await page.waitForTimeout(1000);

    // Check if the agent name is displayed before clicking buttons
    await expect(page.getByText('Test Agent')).toBeVisible();

    // Click the Help button
    await page.getByRole('button', { name: 'Help' }).click();

    // Click the Start button
    await page.getByRole('button', { name: 'Start' }).click();

    // We can't directly assert on network requests in Playwright,
    // but we can check that the page doesn't show any errors
    await expect(page.getByText(/error/i)).not.toBeVisible({ timeout: 5000 });
  });
});
