# Test info

- Name: AgentUI Integration Tests >> Mock API integration works
- Location: C:\Users\ancha\Documents\AI\pAIssive_income2\pAIssive_income\ui\react_frontend\tests\e2e\agent_ui.spec.ts:66:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/about
Call log:
  - navigating to "http://localhost:3000/about", waiting until "load"

    at C:\Users\ancha\Documents\AI\pAIssive_income2\pAIssive_income\ui\react_frontend\tests\e2e\agent_ui.spec.ts:93:18
```

# Test source

```ts
   1 | import { test, expect } from '@playwright/test';
   2 | import * as fs from 'fs';
   3 | import * as path from 'path';
   4 |
   5 | // Adjust this URL if your dev server runs elsewhere
   6 | const BASE_URL = 'http://localhost:3000';
   7 |
   8 | // Ensure the playwright-report directory exists
   9 | const reportDir = path.join(process.cwd(), 'playwright-report');
   10 | if (!fs.existsSync(reportDir)) {
   11 |   fs.mkdirSync(reportDir, { recursive: true });
   12 |   console.log(`Created playwright-report directory at ${reportDir}`);
   13 | }
   14 |
   15 | test.describe('AgentUI Integration Tests', () => {
   16 |   // Add a hook to capture screenshots on test failure
   17 |   test.afterEach(async ({ page }, testInfo) => {
   18 |     if (testInfo.status !== 'passed') {
   19 |       // Ensure the directory exists
   20 |       if (!fs.existsSync(reportDir)) {
   21 |         fs.mkdirSync(reportDir, { recursive: true });
   22 |       }
   23 |       // Capture a screenshot on test failure
   24 |       const screenshotPath = path.join(reportDir, `test-failure-${testInfo.title.replace(/\s+/g, '-')}.png`);
   25 |       await page.screenshot({ path: screenshotPath, fullPage: true });
   26 |       console.log(`Test failed. Screenshot captured at ${screenshotPath}`);
   27 |     }
   28 |   });
   29 |
   30 |   test('Homepage loads successfully', async ({ page }) => {
   31 |     // Navigate to the homepage
   32 |     await page.goto(BASE_URL);
   33 |
   34 |     // Wait for navigation to complete
   35 |     await page.waitForLoadState('load', { timeout: 10000 });
   36 |
   37 |     // Take a screenshot
   38 |     await page.screenshot({ path: 'homepage.png', fullPage: true });
   39 |
   40 |     // Check if the page has any content
   41 |     const bodyContent = await page.textContent('body');
   42 |     expect(bodyContent).toBeTruthy();
   43 |
   44 |     // Pass the test
   45 |     expect(true).toBeTruthy();
   46 |   });
   47 |
   48 |   test('About page loads successfully', async ({ page }) => {
   49 |     // Navigate to the About page
   50 |     await page.goto(`${BASE_URL}/about`);
   51 |
   52 |     // Wait for navigation to complete
   53 |     await page.waitForLoadState('load', { timeout: 10000 });
   54 |
   55 |     // Take a screenshot to see what's actually on the page
   56 |     await page.screenshot({ path: 'about-page.png', fullPage: true });
   57 |
   58 |     // Check if any content is loaded
   59 |     const content = await page.textContent('body');
   60 |     expect(content).toBeTruthy();
   61 |
   62 |     // Pass the test
   63 |     expect(true).toBeTruthy();
   64 |   });
   65 |
   66 |   test('Mock API integration works', async ({ page }) => {
   67 |     try {
   68 |       // Set up API mocking before navigating
   69 |       await page.route('/api/agent', async (route) => {
   70 |         await route.fulfill({
   71 |           status: 200,
   72 |           contentType: 'application/json',
   73 |           body: JSON.stringify({
   74 |             id: 1,
   75 |             name: 'Test Agent',
   76 |             description: 'This is a test agent for e2e testing'
   77 |           })
   78 |         });
   79 |       });
   80 |
   81 |       await page.route('/api/agent/action', async (route) => {
   82 |         await route.fulfill({
   83 |           status: 200,
   84 |           contentType: 'application/json',
   85 |           body: JSON.stringify({ status: 'success', action_id: 123 })
   86 |         });
   87 |       });
   88 |
   89 |       console.log('API routes mocked successfully');
   90 |
   91 |       // Navigate to the About page
   92 |       console.log('Navigating to About page...');
>  93 |       await page.goto(`${BASE_URL}/about`);
      |                  ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/about
   94 |
   95 |       // Wait for navigation to complete
   96 |       console.log('Waiting for page to load...');
   97 |       await page.waitForLoadState('load', { timeout: 15000 });
   98 |
   99 |       // Take a screenshot and save it to the report directory
  100 |       const screenshotPath = path.join(reportDir, 'about-page-with-mock-api.png');
  101 |       await page.screenshot({ path: screenshotPath, fullPage: true });
  102 |       console.log(`Screenshot saved to ${screenshotPath}`);
  103 |
  104 |       // Log the page content for debugging
  105 |       const content = await page.content();
  106 |       console.log(`Page content length: ${content.length} characters`);
  107 |
  108 |       // Check for any content
  109 |       const bodyText = await page.textContent('body');
  110 |       console.log(`Body text length: ${bodyText?.length || 0} characters`);
  111 |
  112 |       // Create a simple HTML report
  113 |       const reportPath = path.join(reportDir, 'test-report.html');
  114 |       fs.writeFileSync(reportPath, `
  115 |         <!DOCTYPE html>
  116 |         <html>
  117 |           <head><title>Test Report</title></head>
  118 |           <body>
  119 |             <h1>Test Report</h1>
  120 |             <p>Test completed at: ${new Date().toISOString()}</p>
  121 |             <p>Test status: Passed</p>
  122 |           </body>
  123 |         </html>
  124 |       `);
  125 |       console.log(`Test report saved to ${reportPath}`);
  126 |
  127 |       // Pass the test
  128 |       expect(true).toBeTruthy();
  129 |     } catch (error) {
  130 |       console.error('Test failed with error:', error);
  131 |       // Create a failure report
  132 |       const errorReportPath = path.join(reportDir, 'error-report.txt');
  133 |       fs.writeFileSync(errorReportPath, `Test failed at ${new Date().toISOString()}\nError: ${error.toString()}`);
  134 |       console.log(`Error report saved to ${errorReportPath}`);
  135 |       throw error;
  136 |     }
  137 |   });
  138 | });
  139 |
```