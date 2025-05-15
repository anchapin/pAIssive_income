# Test info

- Name: AgentUI Integration >> AgentUI buttons trigger actions
- Location: C:\Users\ancha\Documents\AI\pAIssive_income2\pAIssive_income\ui\react_frontend\tests\e2e\agent_ui_final.spec.ts:77:7

# Error details

```
Error: Timed out 10000ms waiting for expect(locator).toBeVisible()

Locator: locator('h6:has-text("Agent UI Integration")')
Expected: visible
Received: <element(s) not found>
Call log:
  - expect.toBeVisible with timeout 10000ms
  - waiting for locator('h6:has-text("Agent UI Integration")')

    at C:\Users\ancha\Documents\AI\pAIssive_income2\pAIssive_income\ui\react_frontend\tests\e2e\agent_ui_final.spec.ts:116:71
```

# Page snapshot

```yaml
- iframe
```

# Test source

```ts
   16 |   test.beforeEach(async ({ page }) => {
   17 |     // Check if the app is running before proceeding
   18 |     try {
   19 |       await page.goto(BASE_URL, { timeout: 5000 });
   20 |       console.log('Successfully connected to the React app');
   21 |     } catch (error) {
   22 |       console.error('Could not connect to the React app. Is it running?');
   23 |       console.error('To run the app: pnpm start');
   24 |       test.skip();
   25 |     }
   26 |   });
   27 |
   28 |   test('AgentUI component is visible on the About page', async ({ page }) => {
   29 |     // Navigate to the About page where AgentUI is integrated
   30 |     await page.goto(`${BASE_URL}/about`);
   31 |     
   32 |     // Wait for navigation to complete
   33 |     await page.waitForLoadState('load', { timeout: 10000 });
   34 |     
   35 |     // Check if the About page content is loaded
   36 |     await expect(page.locator('h4:has-text("About pAIssive Income Framework")')).toBeVisible({ timeout: 10000 });
   37 |     
   38 |     // Mock the API response for /api/agent
   39 |     await page.route('/api/agent', async (route) => {
   40 |       await route.fulfill({
   41 |         status: 200,
   42 |         contentType: 'application/json',
   43 |         body: JSON.stringify({
   44 |           id: 1,
   45 |           name: 'Test Agent',
   46 |           description: 'This is a test agent for e2e testing'
   47 |         })
   48 |       });
   49 |     });
   50 |     
   51 |     // Reload the page to trigger the API call with our mock
   52 |     await page.reload();
   53 |     
   54 |     // Wait for the page to load
   55 |     await page.waitForLoadState('load', { timeout: 10000 });
   56 |     
   57 |     // Wait for the AgentUI component section to be visible
   58 |     await expect(page.locator('h6:has-text("Agent UI Integration")')).toBeVisible({ timeout: 10000 });
   59 |     
   60 |     // Wait for the agent data to load
   61 |     await page.waitForTimeout(1000);
   62 |     
   63 |     // Check if the agent name is displayed
   64 |     await expect(page.locator('text="Test Agent"')).toBeVisible({ timeout: 5000 });
   65 |     
   66 |     // Check if the agent description is displayed
   67 |     await expect(page.locator('text="This is a test agent for e2e testing"')).toBeVisible({ timeout: 5000 });
   68 |     
   69 |     // Check if the buttons are present
   70 |     await expect(page.locator('button:has-text("Help")')).toBeVisible({ timeout: 5000 });
   71 |     await expect(page.locator('button:has-text("Start")')).toBeVisible({ timeout: 5000 });
   72 |     
   73 |     // Take a screenshot for visual verification
   74 |     await page.screenshot({ path: 'agent-ui-component.png', fullPage: true });
   75 |   });
   76 |
   77 |   test('AgentUI buttons trigger actions', async ({ page }) => {
   78 |     // Navigate to the About page where AgentUI is integrated
   79 |     await page.goto(`${BASE_URL}/about`);
   80 |     
   81 |     // Wait for navigation to complete
   82 |     await page.waitForLoadState('load', { timeout: 10000 });
   83 |     
   84 |     // Mock the API response for /api/agent
   85 |     await page.route('/api/agent', async (route) => {
   86 |       await route.fulfill({
   87 |         status: 200,
   88 |         contentType: 'application/json',
   89 |         body: JSON.stringify({
   90 |           id: 1,
   91 |           name: 'Test Agent',
   92 |           description: 'This is a test agent for e2e testing'
   93 |         })
   94 |       });
   95 |     });
   96 |     
   97 |     // Mock the API response for /api/agent/action
   98 |     await page.route('/api/agent/action', async (route, request) => {
   99 |       const postData = request.postDataJSON();
  100 |       console.log('Action received:', postData);
  101 |       
  102 |       await route.fulfill({
  103 |         status: 200,
  104 |         contentType: 'application/json',
  105 |         body: JSON.stringify({ status: 'success', action_id: 123 })
  106 |       });
  107 |     });
  108 |     
  109 |     // Reload the page to trigger the API call with our mock
  110 |     await page.reload();
  111 |     
  112 |     // Wait for the page to load
  113 |     await page.waitForLoadState('load', { timeout: 10000 });
  114 |     
  115 |     // Wait for the AgentUI component section to be visible
> 116 |     await expect(page.locator('h6:has-text("Agent UI Integration")')).toBeVisible({ timeout: 10000 });
      |                                                                       ^ Error: Timed out 10000ms waiting for expect(locator).toBeVisible()
  117 |     
  118 |     // Wait for the agent data to load
  119 |     await page.waitForTimeout(1000);
  120 |     
  121 |     // Check if the agent name is displayed before clicking buttons
  122 |     await expect(page.locator('text="Test Agent"')).toBeVisible({ timeout: 5000 });
  123 |     
  124 |     // Click the Help button
  125 |     await page.locator('button:has-text("Help")').click();
  126 |     
  127 |     // Click the Start button
  128 |     await page.locator('button:has-text("Start")').click();
  129 |     
  130 |     // We can't directly assert on network requests in Playwright,
  131 |     // but we can check that the page doesn't show any errors
  132 |     await expect(page.locator('text="Error"')).not.toBeVisible({ timeout: 5000 });
  133 |   });
  134 | });
  135 |
```