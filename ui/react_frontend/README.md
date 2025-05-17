# React Frontend

...

## Password Reset ("Forgot Password")

This application supports a secure password reset flow:

- **Forgot Password:** On the login page, click "Forgot password?" to request a password reset link by entering your email address.
- **Reset Link:** If an account exists for that email, a reset link will be sent (simulated in dev).
- **Reset Password:** Follow the link (or visit `/reset-password/:token`) and enter your new password (with confirmation).
- **Navigation:** Both the forgot/reset forms and login page provide links to easily navigate between them.

This flow is fully covered by E2E tests in `tests/e2e/forgot_password.spec.ts`. To run the tests:

```sh
pnpm exec playwright test tests/e2e/forgot_password.spec.ts
```

> **Note:** In development, backend API calls are stubbed/mocked. Integrate with your real backend for production.

...