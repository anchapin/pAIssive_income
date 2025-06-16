import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('Forgot/Reset Password E2E', () => {
  test('User can request a password reset', async ({ page }) => {
    await page.goto(`${BASE_URL}/forgot-password`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Fill out and submit the forgot password form
    await page.getByLabelText(/email/i).fill('e2euser@example.com');
    await page.getByRole('button', { name: /send reset link/i }).click();

    // Assert confirmation message is shown
    const confirmMsg = await page.getByText(/reset link has been sent|email exists/i, { exact: false, timeout: 5000 }).catch(() => null);
    expect(confirmMsg).not.toBeNull();
  });

  test('User can reset password with valid token', async ({ page }) => {
    // Simulate visiting the reset-password page with a valid token
    const testToken = 'e2e-mock-token';
    await page.goto(`${BASE_URL}/reset-password/${testToken}`);
    await page.waitForLoadState('load', { timeout: 10000 });

    // Fill out and submit the reset password form
    await page.getByLabelText(/new password/i).fill('E2eNewPass123!');
    await page.getByLabelText(/confirm password/i).fill('E2eNewPass123!');
    await page.getByRole('button', { name: /reset password/i }).click();

    // Assert success message is shown
    const successMsg = await page.getByText(/password has been reset/i, { exact: false, timeout: 5000 }).catch(() => null);
    expect(successMsg).not.toBeNull();
  });

  test('Shows error if passwords do not match', async ({ page }) => {
    const testToken = 'e2e-mock-token';
    await page.goto(`${BASE_URL}/reset-password/${testToken}`);
    await page.waitForLoadState('load', { timeout: 10000 });

    await page.getByLabelText(/new password/i).fill('E2eNewPass123!');
    await page.getByLabelText(/confirm password/i).fill('DifferentPass456!');
    await page.getByRole('button', { name: /reset password/i }).click();

    // Assert error message is shown
    const errorMsg = await page.getByText(/do not match|error/i, { exact: false, timeout: 3000 }).catch(() => null);
    expect(errorMsg).not.toBeNull();
  });

  test('Shows error if password is too short', async ({ page }) => {
    const testToken = 'e2e-mock-token';
    await page.goto(`${BASE_URL}/reset-password/${testToken}`);
    await page.waitForLoadState('load', { timeout: 10000 });

    await page.getByLabelText(/new password/i).fill('short');
    await page.getByLabelText(/confirm password/i).fill('short');
    await page.getByRole('button', { name: /reset password/i }).click();

    // Assert error message about password length
    const errorMsg = await page.getByText(/at least 8/i, { exact: false, timeout: 3000 }).catch(() => null);
    expect(errorMsg).not.toBeNull();
  });
});