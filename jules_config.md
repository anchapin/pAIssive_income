# Jules Configuration Guide for pAIssive_income

This document provides instructions for setting up a development environment for the `anchapin/pAIssive_income` repository, specifically tailored for use by Jules at jules.google.com. The goal is to help Jules check updates, run tests, and interact with the codebase effectively.

The repository will be cloned automatically into your environment.

## Environment Setup

The recommended way to set up the development environment is by using the project's provided setup scripts.

1.  **Run the Setup Script:**
    *   For Linux/macOS: `bash setup.sh`
    *   For Windows: `setup.bat`
    These scripts will:
    *   Set up the Python environment using `uv` by executing `python3 scripts/setup/enhanced_setup_dev_environment.py --full`. This typically creates a virtual environment in `.venv/`.
    *   Install Node.js dependencies using `pnpm install`.

2.  **Activate Python Virtual Environment:**
    After the setup script completes, activate the Python virtual environment:
    ```bash
    source .venv/bin/activate
    ```

3.  **Configure Environment Variables:**
    *   The project uses an `.env` file for configuration. A template is provided as `.env.example`.
    *   The `setup.sh` script should copy `.env.example` to `.env` if `.env` doesn't exist.
    *   **Action required by Jules:** Review and update the `.env` file with any necessary API keys, database configurations, or other specific settings required for your tasks.

4.  **Initialize the Database:**
    Once the `.env` file is correctly configured, initialize the database:
    ```bash
    python init_db.py
    ```

5.  **Note on Specific Tool Versions (for OpenHands-like environments):**
    If Jules operates in an environment similar to OpenHands or requires specific pinned versions, the `.openhands/setup.sh` script indicates the use of:
    *   Node.js 18.x
    *   pnpm 8.6.0
    *   uv 0.4.30
    While the main `setup.sh` should handle general setup, these versions are noted as potentially ideal for maximum compatibility if manual tool installation is necessary.

## Checking for Updates

To ensure you have the latest version of the code, pull changes from the `main` branch (assuming `main` is the primary development branch):

```bash
git pull origin main
```

## Running Tests

The project has separate test suites for Python and JavaScript code.

### Python Tests

*   Run Python tests (using pytest) and generate a coverage report with:
    ```bash
    python scripts/run/run_tests.py --with-coverage
    ```
*   A minimum of 90% code coverage is typically required.

### JavaScript Tests

*   Install Node.js dependencies first if not already done by the main setup script (though `pnpm install` during setup should cover this):
    ```bash
    pnpm install
    ```
*   Run JavaScript tests (using Mocha) and check coverage with:
    ```bash
    pnpm test
    ```
    (This command might need to be run from the root directory or specifically within `ui/react_frontend/` if that's where the primary `package.json` for UI testing resides. Assume root for now unless specified otherwise by project structure).
*   A minimum of 80% code coverage is typically required for JavaScript tests.

## Linting and Formatting (Python)

The project uses Ruff for Python linting and formatting.

*   To check for linting issues and apply fixes:
    ```bash
    python scripts/fix/fix_linting_issues.py
    ```
*   To automatically format the code:
    ```bash
    python scripts/fix/fix_formatting.py
    ```
*   Pre-commit hooks are also configured to enforce these standards.

## Interacting with the Code & Running the Application

*   **Recommended IDE:** VS Code.
*   **Project Structure:** The repository is organized into several key directories such as `ai_models/`, `agent_team/`, `api/`, `common_utils/`, `ui/react_frontend/`, etc.
*   **Running the Main Application:**
    *   The application can typically be started using:
        ```bash
        python app.py
        ```
    *   Alternatively, if Docker is set up and configured in your environment, you can use Docker Compose:
        ```bash
        docker compose up --build
        ```
    Ensure your `.env` file is properly configured before running the application.

Please refer to the extensive documentation in the `docs/` directory for more in-depth information on specific modules and workflows.
