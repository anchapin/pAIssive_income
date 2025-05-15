# Test info

- Name: AgentUI Integration >> AgentUI component is visible on the About page
- Location: C:\Users\ancha\Documents\AI\pAIssive_income2\pAIssive_income\ui\react_frontend\tests\e2e\agent_ui.spec.ts:59:7

# Error details

```
Error: expect(received).toBeGreaterThan(expected)

Expected: > 0
Received:   0
    at C:\Users\ancha\Documents\AI\pAIssive_income2\pAIssive_income\ui\react_frontend\tests\e2e\agent_ui.spec.ts:115:79
```

# Page snapshot

```yaml
- iframe
```

# Test source

```ts
   15 |         description: 'This is a test agent for e2e testing'
   16 |       })
   17 |     });
   18 |   });
   19 | }
   20 |
   21 | // Helper function to mock the agent action API
   22 | async function mockAgentActionApi(page) {
   23 |   await page.route('/api/agent/action', async (route, request) => {
   24 |     const postData = request.postDataJSON();
   25 |     if (process.env.DEBUG === 'true') {
   26 |       console.log('Action received:', postData);
   27 |     }
   28 |
   29 |     await route.fulfill({
   30 |       status: 200,
   31 |       contentType: 'application/json',
   32 |       body: JSON.stringify({ status: 'success', action_id: 123 })
   33 |     });
   34 |   });
   35 | }
   36 |
   37 | test.describe('AgentUI Integration', () => {
   38 |   // Add a hook to capture screenshots on test failure
   39 |   test.afterEach(async ({ page }, testInfo) => {
   40 |     if (testInfo.status !== 'passed') {
   41 |       // Capture a screenshot on test failure
   42 |       await page.screenshot({ path: `test-failure-${testInfo.title.replace(/\s+/g, '-')}.png`, fullPage: true });
   43 |       console.log('Test failed. Screenshot captured.');
   44 |     }
   45 |   });
   46 |
   47 |   test.beforeEach(async ({ page }) => {
   48 |     // Check if the app is running before proceeding
   49 |     try {
   50 |       await page.goto(BASE_URL, { timeout: 5000 });
   51 |       console.log('Successfully connected to the React app');
   52 |     } catch (error) {
   53 |       console.error('Could not connect to the React app. Is it running?');
   54 |       console.error('To run the app: pnpm start');
   55 |       test.skip();
   56 |     }
   57 |   });
   58 |
   59 |   test('AgentUI component is visible on the About page', async ({ page }) => {
   60 |     // Navigate to the About page where AgentUI is integrated
   61 |     await page.goto(`${BASE_URL}/about`);
   62 |
   63 |     // Wait for navigation to complete
   64 |     await page.waitForLoadState('load', { timeout: 10000 });
   65 |
   66 |     // Take a screenshot to see what's actually on the page
   67 |     await page.screenshot({ path: 'about-page-initial.png', fullPage: true });
   68 |
   69 |     // Log the page content for debugging
   70 |     const content = await page.content();
   71 |     console.log('Page content length:', content.length);
   72 |
   73 |     // Check for any heading element
   74 |     const headings = await page.locator('h1, h2, h3, h4, h5, h6').count();
   75 |     console.log('Number of headings found:', headings);
   76 |
   77 |     // Mock the API response for /api/agent using the helper function
   78 |     await mockAgentApi(page);
   79 |
   80 |     // Reload the page to trigger the API call with our mock
   81 |     await page.reload();
   82 |
   83 |     // Wait for navigation to complete
   84 |     await page.waitForLoadState('load', { timeout: 10000 });
   85 |
   86 |     // Take a screenshot after reload
   87 |     await page.screenshot({ path: 'about-page-after-reload.png', fullPage: true });
   88 |
   89 |     // Try to find the Agent UI Integration section
   90 |     const agentUiSection = await page.locator('h6:has-text("Agent UI Integration")').count();
   91 |     console.log('Agent UI Integration section found:', agentUiSection > 0);
   92 |
   93 |     // Check for buttons
   94 |     const buttons = await page.locator('button').count();
   95 |     console.log('Number of buttons found:', buttons);
   96 |
   97 |     // Look for the agent name and description
   98 |     const agentNameVisible = await page.locator('text="Test Agent"').count();
   99 |     console.log('Agent name visible:', agentNameVisible > 0);
  100 |
  101 |     const agentDescriptionVisible = await page.locator('text="This is a test agent for e2e testing"').count();
  102 |     console.log('Agent description visible:', agentDescriptionVisible > 0);
  103 |
  104 |     // Check if the buttons are present
  105 |     const helpButtonVisible = await page.locator('button:has-text("Help")').count();
  106 |     console.log('Help button visible:', helpButtonVisible > 0);
  107 |
  108 |     const startButtonVisible = await page.locator('button:has-text("Start")').count();
  109 |     console.log('Start button visible:', startButtonVisible > 0);
  110 |
  111 |     // Take a screenshot for visual verification
  112 |     await page.screenshot({ path: 'agent-ui-component.png', fullPage: true });
  113 |
  114 |     // Assert that the "Agent UI Integration" section is present
> 115 |     expect(await page.locator('h6:has-text("Agent UI Integration")').count()).toBeGreaterThan(0);
      |                                                                               ^ Error: expect(received).toBeGreaterThan(expected)
  116 |
  117 |     // Assert that the agent's name and description are visible
  118 |     expect(await page.locator('text="Test Agent"').count()).toBeGreaterThan(0);
  119 |     expect(await page.locator('text="This is a test agent for e2e testing"').count()).toBeGreaterThan(0);
  120 |
  121 |     // Assert that the "Help" and "Start" buttons are present
  122 |     expect(await page.locator('button:has-text("Help")').count()).toBeGreaterThan(0);
  123 |     expect(await page.locator('button:has-text("Start")').count()).toBeGreaterThan(0);
  124 |   });
  125 |
  126 |   test('AgentUI buttons trigger actions', async ({ page }) => {
  127 |     // Navigate to the About page where AgentUI is integrated
  128 |     await page.goto(`${BASE_URL}/about`);
  129 |
  130 |     // Wait for navigation to complete
  131 |     await page.waitForLoadState('load', { timeout: 10000 });
  132 |
  133 |     // Take a screenshot to see what's actually on the page
  134 |     await page.screenshot({ path: 'about-page-buttons-test.png', fullPage: true });
  135 |
  136 |     // Mock the API responses using helper functions
  137 |     await mockAgentApi(page);
  138 |     await mockAgentActionApi(page);
  139 |
  140 |     // Reload the page to trigger the API call with our mock
  141 |     await page.reload();
  142 |
  143 |     // Wait for navigation to complete
  144 |     await page.waitForLoadState('load', { timeout: 10000 });
  145 |
  146 |     // Take another screenshot after reload
  147 |     await page.screenshot({ path: 'about-page-buttons-after-reload.png', fullPage: true });
  148 |
  149 |     // Try to find and click any buttons on the page
  150 |     const buttons = await page.locator('button').all();
  151 |     console.log('Found', buttons.length, 'buttons on the page');
  152 |
  153 |     // Click each button if any are found
  154 |     for (let i = 0; i < Math.min(buttons.length, 2); i++) {
  155 |       try {
  156 |         const buttonText = await buttons[i].textContent();
  157 |         console.log(`Clicking button ${i}: ${buttonText}`);
  158 |         await buttons[i].click();
  159 |       } catch (error) {
  160 |         console.log(`Error clicking button ${i}:`, error);
  161 |       }
  162 |     }
  163 |
  164 |     // Assert that the "Agent UI Integration" section is present
  165 |     expect(await page.locator('h6:has-text("Agent UI Integration")').count()).toBeGreaterThan(0);
  166 |
  167 |     // Assert that the agent's name and description are visible
  168 |     expect(await page.locator('text="Test Agent"').count()).toBeGreaterThan(0);
  169 |     expect(await page.locator('text="This is a test agent for e2e testing"').count()).toBeGreaterThan(0);
  170 |
  171 |     // Assert that the "Help" and "Start" buttons are present
  172 |     expect(await page.locator('button:has-text("Help")').count()).toBeGreaterThan(0);
  173 |     expect(await page.locator('button:has-text("Start")').count()).toBeGreaterThan(0);
  174 |   });
  175 | });
  176 |
```