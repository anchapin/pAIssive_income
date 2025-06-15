[1mdiff --cc README.md[m
[1mindex 6a641e95,2ad89864..00000000[m
[1m--- a/README.md[m
[1m+++ b/README.md[m
[36m@@@ -1,96 -1,631 +1,114 @@@[m
[31m -# Project Environment & Dependency Management[m
[32m +# Speeding Up Python Tests[m
  [m
[31m -## Python[m
[32m +This project is configured for fast test runs. Here are some tips:[m
  [m
[32m++<<<<<<< HEAD[m
[32m +## 1. Install Dev Dependencies (including pytest-xdist)[m
[32m++=======[m
[32m+ > **Note:** Documentation for this project has been centralized. Please see the [docs/](docs/) directory for additional onboarding,
development,
deployment,
security,
contribution information,
and UI architecture ([docs/ui-architecture.md](docs/ui-architecture.md)).[m
[32m++>>>>>>> origin/main[m
  [m
[31m ----[m
[32m +To enable parallel test execution and all developer/testing features,
install the dev dependencies using [uv](https://github.com/astral-sh/uv):[m
  [m
[31m -## TL;DR Quickstart[m
[32m +```sh[m
[32m +uv pip install -e .[dev][m
[32m +```[m
[32m +This will install `pytest`,
`pytest-xdist`,
and all plugins required for advanced testing.[m
  [m
[31m -> **Tooling Requirement:**[m
[31m -> - **Python:** Use [`uv`](https://github.com/astral-sh/uv) for all dependency/environment management.[m
[31m -> - **Node.js:** Use [`pnpm`](https://pnpm.io/) for all JavaScript/TypeScript dependencies and scripts.[m
[31m -> - Do **NOT** use `pip`,
`venv`,
`npm`,
or `yarn` for development,
testing,
or CI.[m
[32m +## 2. Run Tests in Parallel (recommended)[m
  [m
[31m -1. **Clone the repo and enter it:**[m
[32m +We use [pytest-xdist](https://pypi.org/project/pytest-xdist/) to run tests in parallel across all available CPU cores:[m
  [m
[31m -   ```bash[m
[31m -   git clone https://github.com/anchapin/pAIssive_income.git[m
[31m -   cd pAIssive_income[m
[31m -   ```[m
[32m +```sh[m
[32m +pytest -n auto[m
[32m +```[m
[32m +By default,
`-n auto` uses all available CPU cores. You can override with e.g. `pytest -n 4` to use 4 workers.[m
  [m
[31m -2. **Install `uv` (if not already installed):**[m
[31m -   `uv` is a fast Python package installer and resolver, written in Rust.[m
[32m +## 3. Skip Slow Tests During Development[m
  [m
[31m -   ```bash[m
[31m -   # Recommended (Linux/macOS/Windows with curl)[m
[31m -   curl -LsSf https://astral.sh/uv/install.sh | sh[m
[32m +Tests that take a long time to run are marked with `@pytest.mark.slow`. You can skip these tests during development to speed up your test runs:[m
  [m
[31m -   # If curl is unavailable, you may use pip ONLY for this step:[m
[31m -   pip install uv[m
[31m -   ```[m
[32m +```sh[m
[32m +pytest -m "not slow"[m
[32m +```[m
  [m
[31m -   Ensure `uv` is in your PATH.[m
[32m +To run only the slow tests:[m
  [m
[31m -3. **Set up development environment (Python,
dependencies,
pre-commit hooks,
IDE config):**[m
[31m -   (Requires Python 3.8+ and `uv`)[m
[32m +```sh[m
[32m +pytest -m "slow"[m
[32m +```[m
  [m
[31m -   ```bash[m
[31m -   # On Windows[m
[31m -   enhanced_setup_dev_environment.bat[m
[32m +See `tests/examples/test_slow_test_example.py` for examples of how to mark slow tests.[m
  [m
[31m -   # On Unix/Linux[m
[31m -   ./enhanced_setup_dev_environment.sh[m
[31m -   # Or, to run the Python script directly:[m
[31m -   # python enhanced_setup_dev_environment.py[m
[31m -   ```[m
[32m +## 4. Profile Slow Tests[m
  [m
[31m -   This script uses `uv` to:[m
[31m -   - Create a virtual environment (`.venv`)[m
[31m -   - Install dependencies from `requirements.txt` and `requirements-dev.txt`[m
[31m -   - Install the project in editable mode (`-e .`)[m
[31m -   - Set up pre-commit hooks (installing `pre-commit` via `uv`)[m
[31m -   - Configure IDE settings for VS Code and PyCharm[m
[31m -   - Create .editorconfig for editor-agnostic settings[m
[32m +Find the slowest tests to identify candidates for optimization or marking as slow:[m
  [m
[31m -   For manual setup using `uv`:[m
[32m +```sh[m
[32m +pytest --durations=10[m
[32m +```[m
  [m
[31m -   ```bash[m
[31m -   # Create virtual environment (specify your Python interpreter if needed)[m
[31m -   uv venv .venv --python python3.12[m
[31m -   # Activate virtual environment[m
[31m -   source .venv/bin/activate  # Or: .venv\Scripts\activate (Windows)[m
[31m -   # Install dependencies[m
[31m -   uv pip install -r requirements.txt[m
[31m -   uv pip install -r requirements-dev.txt[m
[31m -   uv pip install -e .[m
[31m -   # Install pre-commit and hooks[m
[31m -   uv pip install pre-commit[m
[31m -   pre-commit install[m
[31m -   ```[m
[32m +## 5. Only Collect Tests from `tests/`[m
  [m
[32m++<<<<<<< HEAD[m
[32m +Test collection is limited to the `tests/` directory for speed.[m
[32m++=======[m
[32m+ 4. **Start PostgreSQL database,
application,
and frontend with Docker Compose:**[m
[32m+    ```bash[m
[32m+    # Using Docker Compose plugin[m
[32m+    docker compose up --build[m
[32m+ [m
[32m+    # Or using standalone Docker Compose[m
[32m+    docker-compose up --build[m
[32m+    ```[m
[32m+    This will launch the Flask backend,
React frontend with ag-ui integration,
and PostgreSQL database.[m
[32m+ [m
[32m+    For more details on the Docker Compose integration,
see [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md).[m
[32m++>>>>>>> origin/main[m
  [m
[31m -5. **Initialize the database (first time only):**[m
[31m -   Open a new terminal and run:[m
[31m -   ```bash[m
[31m -   # Activate your virtualenv if not already active[m
[31m -   flask db upgrade[m
[31m -   ```[m
[31m -   This will apply all database migrations and create the necessary tables.[m
[31m -[m
[31m -6. **Set up and start the modern web UI (requires Node.js 16.10+ and pnpm):**[m
[31m -[m
[31m -   > **Frontend dependencies are managed with [pnpm](https://pnpm.io/).**[m
[31m -   >[m
[31m -   > **Install `pnpm` (recommended):**[m
[31m -   > ```bash[m
[31m -   > corepack enable[m
[31m -   > ```[m
[31m -   > If Corepack is not available,
you may bootstrap pnpm with npm (for this step only):[m
[31m -   > ```bash[m
[31m -   > npm install -g pnpm[m
[31m -   > ```[m
[31m -[m
[31m -   ```bash[m
[31m -   cd ui/[m
[31m -   pnpm install[m
[31m -   pnpm start[m
[31m -   ```[m
[31m -[m
[31m -   If your browser doesn't open,
visit [http://localhost:3000](http://localhost:3000).[m
[31m -[m
[31m -7. **Run all tests (unit, integration, frontend):**[m
[31m -   See the "Running Tests" section below.[m
[31m -[m
[31m ----[m
[31m -[m
[31m -## Database Setup and Migration[m
[31m -[m
[31m -This project now uses PostgreSQL as the main database,
managed via Docker Compose.[m
[32m +## 6. Mock External Calls for Speed[m
  [m
[31m -- The backend Flask app is preconfigured to connect to the database using the environment variable `DATABASE_URL`.[m
[31m -- The default configuration is:[m
[31m -  ```[m
[31m -  postgresql://myuser:mypassword@db:5432/mydb[m
[31m -  ```[m
[31m -- You can customize these credentials via the `docker-compose.yml` file or by setting your own `DATABASE_URL` environment variable.[m
[31m -[m
[31m -### Managing Database Migrations[m
[31m -[m
[31m -Database schema migrations are managed with [Flask-Migrate](https://flask-migrate.readthedocs.io/):[m
[31m -[m
[31m -1. **Initialize migration support (first time only):**[m
[31m -   ```bash[m
[31m -   flask db init[m
[31m -   ```[m
[31m -2. **Create a migration after changing models:**[m
[31m -   ```bash[m
[31m -   flask db migrate -m "Describe your change"[m
[31m -   ```[m
[31m -3. **Apply migrations to the database:**[m
[31m -   ```bash[m
[31m -   flask db upgrade[m
[31m -   ```[m
[31m -[m
[31m -### Example Models and Usage[m
[31m -[m
[31m -ORM models are provided for **User**,
**Team**,
and **Agent** entities in `flask/models.py`. You can now persist and query these entities using SQLAlchemy:[m
[32m +Mock out network/database/API calls in your tests to keep them fast and reliable. This avoids actual external calls during testing,
which can significantly speed up your test suite.[m
  [m
[32m +Example:[m
  ```python[m
[31m -from flask import current_app[m
[31m -from flask.models import db, User, Team, Agent[m
[31m -[m
[31m -# Create a team[m
[31m -team = Team(name="AI Research", description="Research team for AI agents")[m
[31m -db.session.add(team)[m
[31m -db.session.commit()[m
[31m -[m
[31m -# Add an agent to the team[m
[31m -agent = Agent(name="Alice", role="researcher", team=team)[m
[31m -db.session.add(agent)[m
[31m -db.session.commit()[m
[31m -[m
[31m -# Query teams and agents[m
[31m -teams = Team.query.all()[m
[31m -agents = Agent.query.filter_by(team_id=team.id).all()[m
[31m -```[m
[31m -[m
[31m -See [docs/getting-started.md](docs/getting-started.md) for more detailed instructions.[m
[31m -[m
[31m ----[m
[31m -[m
[31m -## Overview[m
[31m -[m
[31m -- **Dependency Locking (Python):**[m
[31m -  This project uses a `requirements.lock` file to ensure reproducible environments. After updating dependencies,
**install both `requirements.txt` and `requirements-dev.txt`** using `uv`,
then regenerate the lockfile:[m
[31m -  ```sh[m
[31m -  uv pip install -r requirements.txt[m
[31m -  uv pip install -r requirements-dev.txt[m
[31m -  # Regenerate lockfile (see scripts/regenerate_venv.py or .sh for details)[m
[31m -  ```[m
[31m -[m
[31m -- **Development dependencies** are managed with `requirements-dev.txt`.[m
[31m -[m
[31m -## Node.js[m
[31m -[m
[31m -- **Install dependencies**:[m
[31m -  ```sh[m
[31m -  pnpm install[m
[31m -  ```[m
[31m -- Dependencies are pinned via `pnpm-lock.yaml`.[m
[31m -- **Security scanning**: `pnpm audit` is run automatically in CI to detect vulnerabilities.[m
[31m -[m
[31m -## Automated Dependency Updates[m
[31m -[m
[31m -- [Dependabot](https://docs.github.com/en/code-security/dependabot) is enabled for Python,
Node.js,
Docker,
and GitHub Actions dependencies. Update PRs are created automatically,
including for the Python lockfile (`requirements.lock`).[m
[31m -[m
[31m -## Vulnerability Scanning[m
[31m -[m
[31m -- Security scanning runs automatically on pushes and pull requests:[m
[31m -  - Python: `pip-audit`, `safety`[m
[31m -  - Node.js: `npm audit`[m
[31m -  - Static analysis: `bandit`, `semgrep`, `pylint`[m
[31m -  - Container: `trivy`[m
[31m -  - Secret scanning: `gitleaks`[m
[31m -[m
[31m -## GitHub Actions Secrets[m
[31m -[m
[31m -The following secrets are used by GitHub Actions workflows:[m
[31m -[m
[31m -- `DOCKERHUB_USERNAME`: Your Docker Hub username[m
[31m -- `DOCKERHUB_TOKEN`: Your Docker Hub access token (not your password)[m
[31m -[m
[31m -These secrets are used for Docker Hub authentication to avoid rate limits when pulling images. Set these in your repository settings under Settings > Secrets and variables > Actions.[m
[31m -[m
[31m -## Best Practices[m
[31m -[m
[31m -- Regularly review and address Dependabot and security scan PRs.[m
[31m -- Regenerate the Python lockfile after any dependency updates.[m
[31m -- See `.github/workflows/security_scan.yml` for the full list of automated checks.[m
[31m -[m
[31m -## Keeping Dependencies Healthy[m
[31m -[m
[31m -- When adding or removing Python dependencies,
update both `requirements.txt`/`requirements-dev.txt` and **regenerate `requirements.lock`** using `uv`.[m
[31m -- For Node.js,
always use `pnpm install` for installation and let Dependabot update `pnpm-lock.yaml`.[m
[31m -- Review and merge Dependabot PRs and address security alerts promptly.[m
[31m -[m
[31m -## Dependency Upgrade and Removal Workflow[m
[31m -[m
[31m -This repository contains a summary of the project and high-level information. The main onboarding guide,
including development setup,
installation,
and usage details,
is maintained in the documentation directory for consistency and easier updates.[m
[31m -[m
[31m -If you are new to this project, start here:[m
[31m -[m
[31m -- [Getting Started Guide](docs/getting-started.md)[m
[31m -[m
[31m -For quick reference, the following topics are included in the full guide:[m
[31m -[m
[31m -- Development environment setup (Python, Node, etc.)[m
[31m -- Installing dependencies[m
[31m -- Running and developing with the framework[m
[31m -- Using the CLI and web UI[m
[31m -- Pre-commit hooks and code quality[m
[31m -- Linting, syntax fixes, and CI workflows[m
[31m -[m
[31m -**Note:** This README is intentionally concise. See the documentation for complete and up-to-date instructions.[m
[31m -[m
[31m ----[m
[31m -[m
[31m -> **Summary:**[m
[31m -> - Use **`uv`** for all Python dependency and environment management.[m
[31m -> - Use **`pnpm`** for all Node.js/JavaScript/TypeScript dependencies and scripts.[m
[31m -> - Do **not** use `pip`,
`venv`,
`npm`,
or `yarn` for any development or CI/CD steps.[m
[31m -> - For any questions, see the top of this document or ask a maintainer.[m
[31m -[m
[31m ----[m
[31m -[m
[31m -## Running Tests[m
[31m -[m
[31m -The project includes Python and JavaScript/TypeScript tests.[m
[31m -[m
[31m -### Python Unit/Integration Tests[m
[31m -[m
[31m -From the repo root, after environment setup:[m
[31m -[m
[31m -```bash[m
[31m -pytest[m
[31m -# or[m
[31m -python -m pytest[m
[31m -```[m
[31m -[m
[31m -### Frontend End-to-End (E2E) Tests[m
[31m -[m
[31m -> **Requires:** Node.js 16.10+ and [pnpm](https://pnpm.io/),
and the UI dev server running at `http://localhost:3000`[m
[31m -[m
[31m -1. Install Playwright and its browsers (first time only):[m
[31m -[m
[31m -   ```bash[m
[31m -   cd ui/react_frontend[m
[31m -   pnpm install[m
[31m -   pnpm exec playwright install[m
[31m -   ```[m
[31m -[m
[31m -2. Run all E2E tests:[m
[31m -[m
[31m -   ```bash[m
[31m -   pnpm exec playwright test[m
[31m -   ```[m
[31m -[m
[31m -3. See `ui/react_frontend/tests/e2e/` for sample E2E tests.[m
[31m -   To run a specific test:[m
[31m -[m
[31m -   ```bash[m
[31m -   pnpm exec playwright test tests/e2e/niche_analysis.spec.ts[m
[31m -   ```[m
[31m -[m
[31m -Test output and screenshots will appear in the Playwright reports directory.[m
[31m -[m
[31m ----[m
[31m -[m
[31m -## Example Output[m
[31m -[m
[31m -Running the main script generates a complete project plan including:[m
[31m -[m
[31m -- Niche analysis with opportunity scores[m
[31m -- Detailed user problem analysis[m
[31m -- Solution design with features and architecture[m
[31m -- Monetization strategy with subscription tiers and revenue projections[m
[31m -- Marketing plan with user personas and channel strategies[m
[31m -[m
[31m -## Requirements[m
[31m -[m
[31m -- Python 3.8+[m
[31m -- [`uv`](https://github.com/astral-sh/uv) (Python package installer and resolver; **required for all Python environments/dependencies**)[m
[31m -  - Install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`[m
[31m -  - If `curl` is unavailable,
you may use `pip install uv` ONLY for initial installation.[m
[31m -- Node.js 16.10+ (**required for modern UI and frontend tests**)[m
[31m -- [`pnpm`](https://pnpm.io/) (**required for all Node.js/JavaScript/TypeScript dependencies**)[m
[31m -  - To install pnpm,
use [Corepack](https://nodejs.org/api/corepack.html) (recommended; included with Node.js v16.10+):[m
[31m -    ```bash[m
[31m -    corepack enable[m
[31m -    ```[m
[31m -  - If Corepack is not available, you can bootstrap pnpm with npm:[m
[31m -    ```bash[m
[31m -    npm install -g pnpm[m
[31m -    ```[m
[31m -    > **Note:** Use npm only for this initial installation of pnpm. For all other package management tasks,
use pnpm.[m
[31m -    > Refer to the [Corepack documentation](https://nodejs.org/api/corepack.html) for more details on managing package managers in Node.js.[m
[31m -[m
[31m -- PostgreSQL 15+ (for database)[m
[31m -  The project uses PostgreSQL as the database backend. See [DATABASE.md](DATABASE.md) for setup and migration instructions.[m
[31m -[m
[31m -- Dependencies listed in each module's README[m
[31m -[m
[31m -## Code Style and Formatting[m
[31m -[m
[31m -The project enforces consistent code style and formatting through pre-commit hooks and automated tools. Here are the key formatting guidelines and tools:[m
[31m -[m
[31m -### IDE Setup[m
[31m -[m
[31m -We recommend configuring your IDE or editor to use Ruff as the primary formatter for a smooth development experience. Configuration files are provided for VS Code,
PyCharm,
and other editors.[m
[31m -[m
[31m -See the [IDE Setup Guide](docs/ide_setup.md) for detailed instructions on configuring your development environment.[m
[31m -[m
[31m -### Common Formatting Issues to Watch For[m
[31m -[m
[31m -- Trailing whitespace at the end of lines[m
[31m -- Missing newline at end of files[m
[31m -- Inconsistent indentation (use 4 spaces, not tabs)[m
[31m -- Type annotation issues caught by MyPy[m
[31m -- Ruff linting violations (see .ruff.toml for rules)[m
[31m -[m
[31m -### Ruff Linting[m
[31m -[m
[31m -To ensure consistent code formatting and prevent CI pipeline failures:[m
[31m -[m
[31m -1. Before committing changes, run Ruff locally to fix any formatting issues:[m
[31m -[m
[31m -   ```bash[m
[31m -   ruff check . --fix[m
[31m -   ```[m
[31m -[m
[31m -2. The CI pipeline has been configured to:[m
[31m -   - Automatically fix and commit Ruff formatting issues[m
[31m -   - Continue execution even if Ruff check-only mode finds issues[m
[31m -[m
[31m -This helps maintain code quality while preventing pipeline failures due to formatting issues.[m
[31m -[m
[31m -### Using Pre-commit Hooks[m
[31m -[m
[31m -The project uses pre-commit hooks to automatically check and fix common issues. The hooks are installed automatically when setting up the development environment,
but you can also install them manually:[m
[31m -[m
[31m -```bash[m
[31m -uv pip install pre-commit[m
[31m -pre-commit install[m
[31m -```[m
[31m -[m
[31m -To run all pre-commit hooks manually on all files:[m
[31m -[m
[31m -```bash[m
[31m -# Using the provided scripts (recommended)[m
[31m -# On Windows[m
[31m -run_pre_commit.bat[m
[31m -[m
[31m -# On Unix/Linux[m
[31m -./run_pre_commit.sh[m
[31m -[m
[31m -# Or manually[m
[31m -pre-commit run --all-files[m
[32m +@patch("requests.get")[m
[32m +def test_api_call(mock_get):[m
[32m +    # Configure the mock[m
[32m +    mock_response = MagicMock()[m
[32m +    mock_response.json.return_value = {"data": "test"}[m
[32m +    mock_get.return_value = mock_response[m
[32m +[m
[32m +    # Test your function that uses requests.get[m
[32m +    result = my_function()[m
[32m +    assert result == expected_result[m
  ```[m
  [m
[31m -To run specific hooks:[m
[32m +See `tests/examples/test_mocking_example.py` for more detailed examples of mocking.[m
  [m
[31m -```bash[m
[31m -pre-commit run trailing-whitespace --all-files[m
[31m -pre-commit run ruff --all-files[m
[31m -```[m
[32m +## 7. Using Test Markers Effectively[m
  [m
[31m -### Unified Workflow (Recommended)[m
[32m +The project uses various pytest markers to categorize tests:[m
  [m
[31m -We now provide a **unified entrypoint** for all code quality,
linting,
formatting,
syntax,
docstring,
and security tasks.[m
[32m +- `@pytest.mark.unit`: Unit tests for individual components[m
[32m +- `@pytest.mark.integration`: Tests for interactions between components[m
[32m +- `@pytest.mark.slow`: Tests that take more than 1 second to run[m
[32m +- `@pytest.mark.api`: Tests related to API functionality[m
[32m +- `@pytest.mark.webhook`: Tests related to webhook functionality[m
[32m +- `@pytest.mark.security`: Tests related to security features[m
[32m +- `@pytest.mark.model`: Tests related to AI model functionality[m
[32m +- `@pytest.mark.performance`: Performance-sensitive tests[m
  [m
[31m -**Use the Makefile for common developer tasks:**[m
[32m +Run tests with specific markers:[m
  [m
[31