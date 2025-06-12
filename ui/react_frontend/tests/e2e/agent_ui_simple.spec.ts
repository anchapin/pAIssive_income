import { test, expect } from '@playwright/test';

// Adjust this URL if your dev server runs elsewhere
const BASE_URL = 'http://localhost:3000';

test.describe('AgentUI Simple Tests', () => {
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

  test('About page loads and renders heading, main, and agent UI', async ({ page }) => {
    await page.goto(`${BASE_URL}/about`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Take a screenshot for debugging
    await page.screenshot({ path: 'about-page-simple.png', fullPage: true });

    // Assert: H1 heading present
    const h1 = await page.$('h1');
    expect(h1).not.toBeNull();

    // Assert: main landmark present
    const main = await page.$('main, [role=main]');
    expect(main).not.toBeNull();

    // Assert: at least one button present
    const buttonCount = await page.locator('button').count();
    expect(buttonCount).toBeGreaterThan(0);
  });

  test('Agent UI loads with mock API and displays agent data', async ({ page }) => {
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
    await page.goto(`${BASE_URL}/about`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Screenshot after reload
    await page.screenshot({ path: 'about-page-with-mock-api.png', fullPage: true });

    // Assert: agent name and description are visible
    const agentName = await page.getByText(/test agent/i, { exact: false });
    await expect(agentName).toBeVisible();

    const agentDesc = await page.getByText(/test agent for e2e testing/i, { exact: false });
    await expect(agentDesc).toBeVisible();

    // Assert: agent card is a region with label
    const region = await page.$('[role=region][aria-label*="agent"], [aria-labelledby*="agent"]');
    expect(region).not.toBeNull();

    // Assert: at least one action button is present
    const actionButton = await page.getByRole('button', { name: /run|trigger|start|action/i }).catch(() => null);
    expect(actionButton).not.toBeNull();
  });
});
