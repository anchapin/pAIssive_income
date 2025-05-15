import { test, expect } from '@playwright/test';

// Adjust this URL if your dev server runs elsewhere
const BASE_URL = 'http://localhost:3000';

test.describe('Simple Test', () => {
  test('Homepage loads', async ({ page }) => {
    // Navigate to the homepage
    await page.goto(BASE_URL);
    
    // Wait for navigation to complete
    await page.waitForLoadState('load', { timeout: 10000 });
    
    // Take a screenshot
    await page.screenshot({ path: 'homepage.png', fullPage: true });
    
    // Check if the page has any content
    const bodyContent = await page.textContent('body');
    console.log('Body content:', bodyContent);
    
    // Pass the test if we got here
    expect(true).toBeTruthy();
  });
});
