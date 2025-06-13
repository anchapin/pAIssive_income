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

  test('AgentUI component is visible and renders agent info on the About page', async ({ page }) => {
    // Mock the API response for /api/agent before navigating
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

    // Navigate to the About page where AgentUI is integrated
    await page.goto(`${BASE_URL}/about`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Screenshot for debugging
    await page.screenshot({ path: 'about-page-after-reload.png', fullPage: true });

    // Assert agent name and description are visible
    const agentName = await page.getByText(/test agent/i, { exact: false });
    await expect(agentName).toBeVisible();
    const agentDesc = await page.getByText(/test agent for e2e testing/i, { exact: false });
    await expect(agentDesc).toBeVisible();

    // Accessibility: heading and main are present
    const h1 = await page.$('h1');
    expect(h1).not.toBeNull();
    const main = await page.$('main, [role=main]');
    expect(main).not.toBeNull();

    // Accessibility: agent card is a region with label
    const region = await page.$('[role=region][aria-label*="agent"], [aria-labelledby*="agent"]');
    expect(region).not.toBeNull();

    // At least one button is present
    const buttonCount = await page.locator('button').count();
    expect(buttonCount).toBeGreaterThan(0);
  });

  test('AgentUI buttons trigger actions and show result', async ({ page }) => {
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

    // Navigate to the About page where AgentUI is integrated
    await page.goto(`${BASE_URL}/about`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Screenshot after reload
    await page.screenshot({ path: 'about-page-buttons-after-reload.png', fullPage: true });

    // Find and click a button that triggers agent action
    const actionButton = await page.getByRole('button', { name: /run|trigger|start|action/i }).catch(() => null);
    expect(actionButton).not.toBeNull();
    if (actionButton) {
      await actionButton.click();
      // Assert that a success/result message appears
      const actionResult = await page.getByText(/success|completed|action received/i, { exact: false, timeout: 10000 });
      await expect(actionResult).toBeVisible();

      // Accessibility: action result is a status or alert
      const statusEl = await page.$('[role=status], [role=alert]');
      expect(statusEl).not.toBeNull();
    }
  });
});
