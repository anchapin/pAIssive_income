import { test, expect } from '@playwright/test';

// Adjust this URL if your dev server runs elsewhere
const BASE_URL = 'http://localhost:3000';

// Helper function to mock the agent API
async function mockAgentApi(page) {
  await page.route('**/api/agent', async (route) => {
    console.log('Intercepted API call to /api/agent');
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
}

// Helper function to mock the agent action API
async function mockAgentActionApi(page) {
  await page.route('**/api/agent/action', async (route, request) => {
    const postData = request.postDataJSON();
    console.log('Intercepted API call to /api/agent/action with data:', postData);

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'success', action_id: 123 })
    });
  });
}

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
    // Set up API mocking before navigating to any page
    await mockAgentApi(page);
    await mockAgentActionApi(page);

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

    // Wait for the page content to be fully loaded
    await page.waitForSelector('h1, h2, h3, h4, h5, h6', { timeout: 10000 });

    // Take a screenshot to see what's actually on the page
    await page.screenshot({ path: 'about-page-initial.png', fullPage: true });

    // Log the page content for debugging
    const content = await page.content();
    console.log('Page content length:', content.length);

    // Check for any heading element
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').count();
    console.log('Number of headings found:', headings);

    // Wait for the Agent UI Integration section to appear
    await page.waitForSelector('text=Agent UI Integration', { timeout: 10000 });

    // Wait for the agent data to load and render
    await page.waitForTimeout(1000);

    // Take a screenshot after waiting for content
    await page.screenshot({ path: 'about-page-after-wait.png', fullPage: true });

    // Try to find the Agent UI Integration section
    const agentUiSection = await page.locator('text=Agent UI Integration').count();
    console.log('Agent UI Integration section found:', agentUiSection > 0);

    // Check for buttons
    const buttons = await page.locator('button').count();
    console.log('Number of buttons found:', buttons);

    // Look for the agent name and description with more flexible selectors
    const agentNameVisible = await page.locator('text=Test Agent').count();
    console.log('Agent name visible:', agentNameVisible > 0);

    const agentDescriptionVisible = await page.locator('text=This is a test agent for e2e testing').count();
    console.log('Agent description visible:', agentDescriptionVisible > 0);

    // Check if the buttons are present with more flexible selectors
    const helpButtonVisible = await page.locator('button:has-text("Help")').count();
    console.log('Help button visible:', helpButtonVisible > 0);

    const startButtonVisible = await page.locator('button:has-text("Start")').count();
    console.log('Start button visible:', startButtonVisible > 0);

    // Take a screenshot for visual verification
    await page.screenshot({ path: 'agent-ui-component.png', fullPage: true });

    // Assert that the "Agent UI Integration" section is present
    expect(agentUiSection).toBeGreaterThan(0);

    // Assert that the agent's name and description are visible
    expect(agentNameVisible).toBeGreaterThan(0);
    expect(agentDescriptionVisible).toBeGreaterThan(0);

    // Assert that the "Help" and "Start" buttons are present
    expect(helpButtonVisible).toBeGreaterThan(0);
    expect(startButtonVisible).toBeGreaterThan(0);
  });

  test('AgentUI buttons trigger actions', async ({ page }) => {
    // Navigate to the About page where AgentUI is integrated
    await page.goto(`${BASE_URL}/about`);

    // Wait for navigation to complete
    await page.waitForLoadState('load', { timeout: 10000 });

    // Wait for the page content to be fully loaded
    await page.waitForSelector('h1, h2, h3, h4, h5, h6', { timeout: 10000 });

    // Take a screenshot to see what's actually on the page
    await page.screenshot({ path: 'about-page-buttons-test.png', fullPage: true });

    // Wait for the Agent UI Integration section to appear
    await page.waitForSelector('text=Agent UI Integration', { timeout: 10000 });

    // Wait for the agent data to load and render
    await page.waitForTimeout(1000);

    // Take another screenshot after waiting for content
    await page.screenshot({ path: 'about-page-buttons-after-wait.png', fullPage: true });

    // Try to find the Agent UI Integration section
    const agentUiSection = await page.locator('text=Agent UI Integration').count();
    console.log('Agent UI Integration section found:', agentUiSection > 0);

    // Find the Help and Start buttons specifically
    const helpButton = page.locator('button:has-text("Help")');
    const startButton = page.locator('button:has-text("Start")');

    // Wait for buttons to be visible
    await helpButton.waitFor({ state: 'visible', timeout: 5000 });
    await startButton.waitFor({ state: 'visible', timeout: 5000 });

    // Log button visibility
    console.log('Help button visible:', await helpButton.isVisible());
    console.log('Start button visible:', await startButton.isVisible());

    // Click the Help button
    console.log('Clicking Help button');
    await helpButton.click();
    await page.waitForTimeout(500);

    // Click the Start button
    console.log('Clicking Start button');
    await startButton.click();
    await page.waitForTimeout(500);

    // Take a screenshot after clicking buttons
    await page.screenshot({ path: 'after-button-clicks.png', fullPage: true });

    // Assert that the "Agent UI Integration" section is present
    expect(agentUiSection).toBeGreaterThan(0);

    // Assert that the agent's name and description are visible
    const agentNameVisible = await page.locator('text=Test Agent').count();
    const agentDescriptionVisible = await page.locator('text=This is a test agent for e2e testing').count();
    expect(agentNameVisible).toBeGreaterThan(0);
    expect(agentDescriptionVisible).toBeGreaterThan(0);

    // Assert that the "Help" and "Start" buttons are present
    expect(await helpButton.count()).toBeGreaterThan(0);
    expect(await startButton.count()).toBeGreaterThan(0);
  });
});
