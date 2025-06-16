# React Frontend

This directory contains the React-based frontend for the project.

## Features

### Password Reset ("Forgot Password")

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

### CopilotKit + CrewAI Integration

We have integrated [CopilotKit + CrewAI](https://v0-crew-land.vercel.app/) to enable multi-agent AI features, agentic chat, and human-in-the-loop workflows in the UI.
A demo Copilot agent chat is now available in the main app view.

---

## Getting Started

### 1. Install dependencies

If using **npm**:
```sh
npm install
```

Or, if using **pnpm** (recommended, since `pnpm-lock.yaml` is present):
```sh
pnpm install
```

### 2. Start the React app

If using **npm**:
```sh
npm start
```

Or, if using **pnpm**:
```sh
pnpm start
```

---

You should see the CopilotKit + CrewAI chat demo in the browser.

## Learn More

- [CopilotKit + CrewAI Docs](https://docs.copilotkit.ai/crewai-crews)
- [Integration Guide](./CopilotKit_CrewAI.md)
