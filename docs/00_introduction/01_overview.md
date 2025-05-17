# Project Overview

Welcome to the pAIssive Income project!  
This document provides a high-level overview of the project, its mission, vision, core features, a getting started guide, and a description of the project structure.

---

## Mission

To empower users and developers with modular, efficient, and secure AI-driven tools for content generation, market analysis, monetization, and more.

## Vision

Provide a collaborative, extensible platform for AI automation, market research, and revenue optimization, with a focus on transparency, security, and developer experience.

## Core Features

- Modular AI model management
- Comprehensive API for all core services
- Advanced agent orchestration and automation
- Security by default, with robust compliance practices
- Developer-friendly workflows and documentation

---

## Getting Started

Follow these steps to get up and running:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/pAIssive_income.git
    cd pAIssive_income
    ```

2. **Install dependencies:**

    - **Python:**  
      Use [`uv`](https://github.com/astral-sh/uv) to manage environments and dependencies:
      ```bash
      uv venv
      uv pip install -r requirements.txt
      ```

    - **Node.js:**  
      Use [`pnpm`](https://pnpm.io/) for all JavaScript/TypeScript dependencies:
      ```bash
      pnpm install
      ```

3. **Set up environment variables:**  
   Copy `.env.example` to `.env` and fill in required values.

4. **Initialize the database (if needed):**
    ```bash
    python init_db.py
    ```

5. **Run the application:**
    ```bash
    python main.py
    # or start specific modules as needed
    ```

6. **Run tests:**  
    ```bash
    python run_tests.py --with-coverage
    ```

7. **Lint and format:**  
    ```bash
    python fix_linting_issues.py
    python fix_formatting.py
    ```

For advanced usage, see the [Developer Guide](../02_developer_guide/).

---

## Project Structure

Here are the major directories and their roles:

- `ai_models/` — Modular AI model management core
- `agent_team/` — Multi-agent orchestration and CrewAI integration
- `api/` — RESTful API server and endpoints
- `niche_analysis/`, `monetization/`, `marketing/`, `users/` — Domain modules
- `common_utils/` — Shared utilities and security
- `tests/` — All tests (unit, integration, E2E)
- `docs/` — Project documentation (see below)
- `scripts/`, `dev_tools/` — Developer scripts and helpers

See the [Developer Guide](../02_developer_guide/) for deeper architectural and module deep-dive documentation.

---

For user instructions, developer workflow, and security/compliance details, see the rest of the [../](../) documentation directory.
