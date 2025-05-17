import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('Authentication E2E', () => {
  test('User can register and login via UI', async ({ page }) => {
    // Go to register page
    await page.goto(`${BASE_URL}/register`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Fill out registration form
    await page.getByLabelText(/username/i).fill('e2euser');
    await page.getByLabelText(/email/i).fill('e2euser@example.com');
    await page.getByLabelText(/full name|name/i).fill('E2E User');
    await page.getByLabelText(/password|credential/i).first().fill('E2eUserPass123!');
    await page.getByLabelText(/confirm/i).fill('E2eUserPass123!');

    // Submit registration
    await page.getByRole('button', { name: /register/i }).click();

    // Assert success notification or redirect to dashboard/home/login
    const successMsg = await page.getByText(/registration successful|welcome|dashboard|login/i, { exact: false, timeout: 10000 }).catch(() => null);
    expect(successMsg).not.toBeNull();

    // Go to login page
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Fill out login form
    await page.getByLabelText(/username/i).fill('e2euser');
    await page.getByLabelText(/password|credential/i).first().fill('E2eUserPass123!');

    // Submit login
    await page.getByRole('button', { name: /login|sign in/i }).click();

    // Assert success notification or landing page
    const loginSuccess = await page.getByText(/login successful|dashboard|welcome/i, { exact: false, timeout: 10000 }).catch(() => null);
    expect(loginSuccess).not.toBeNull();
  });

  test('Shows error on login with bad credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('load', { timeout: 10000 });

    await page.getByLabelText(/username/i).fill('fakeuser');
    await page.getByLabelText(/password|credential/i).first().fill('wrongpassword');

    await page.getByRole('button', { name: /login|sign in/i }).click();

    // Assert error message appears
    const errorMsg = await page.getByText(/invalid|failed|incorrect|error/i, { exact: false, timeout: 10000 }).catch(() => null);
    expect(errorMsg).not.toBeNull();
  });

  test('Protected route redirects to login if not authenticated', async ({ page }) => {
    // Visit a protected dashboard or user page
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Should land on login page or see login prompt
    const loginPrompt = await page.getByText(/login|sign in|please authenticate/i, { exact: false, timeout: 10000 }).catch(() => null);
    expect(loginPrompt).not.toBeNull();
  });
});