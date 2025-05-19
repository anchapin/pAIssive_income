# Contributing to pAIssive Income Framework

Thank you for your interest in contributing to the pAIssive Income Framework! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a positive and inclusive environment for everyone.

## How to Contribute

There are many ways to contribute to the pAIssive Income Framework:

1. **Report bugs**: If you find a bug, please report it by creating an issue in the GitHub repository.
2. **Suggest features**: If you have an idea for a new feature or improvement, please create an issue to discuss it.
3. **Improve documentation**: Help us improve the documentation by fixing typos, adding examples, or clarifying explanations.
4. **Write code**: Contribute code by fixing bugs, implementing features, or improving existing code.

## Getting Started

### Prerequisites

**You must use _only_ the following tools for all local development and CI:**

- **Python:** [`uv`](https://github.com/astral-sh/uv) (for all Python dependency management and virtual environment tasks)
- **Node.js:** [`pnpm`](https://pnpm.io/) (for all Node.js/JavaScript/TypeScript dependency management—frontend and scripts)
- **Do _not_ use:** `pip`, `venv`, `npm`, or `yarn` directly for development, testing, or CI. Contributions using unsupported tools will not be accepted.

> **Install `uv`:**
> - Preferred: `curl -LsSf https://astral.sh/uv/install.sh | sh`
> - If curl is unavailable: `pip install uv` (only for initial installation)

> **Install `pnpm`:**
> - Preferred (with Node.js v16.10+):
>   ```bash
>   corepack enable
>   ```
>   This will make `pnpm` available.
> - If Corepack is unavailable:
>   ```bash
>   npm install -g pnpm
>   ```
>   (Only for bootstrapping; do not use `npm` for anything else.)

> **All code and documentation assumes you are using `uv` and `pnpm` exclusively.**

### Setting Up the Development Environment

1. Fork the repository on GitHub.
2. Clone your fork to your local machine:

```bash
git clone https://github.com/your-username/pAIssive_income.git
cd pAIssive_income
```

3. **Set up the Python environment (choose one):**

- **Recommended:**
  ```bash
  # On Windows
  enhanced_setup_dev_environment.bat

  # On Unix/Linux
  ./enhanced_setup_dev_environment.sh
  # Or if running the Python script directly:
  # python enhanced_setup_dev_environment.py
  ```

- **Manually (using uv):**
  ```bash
  uv venv .venv --python 3.12
  # Activate virtual environment
  source .venv/bin/activate      # On Windows: .venv\Scripts\activate
  # Install dependencies
  uv pip install -r requirements.txt
  uv pip install -r requirements-dev.txt
  uv pip install -e .
  # Install pre-commit and hooks
  uv pip install pre-commit
  pre-commit install
  ```

4. **Set up Node.js dependencies (frontend/scripts):**

  ```bash
  # In any frontend or Node.js project directory (e.g., ./ui/, ./sdk/)
  pnpm install
  ```

**All subsequent development, testing, and dependency management must use `uv` for Python and `pnpm` for Node.js.**

### Development Workflow

1. Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them with a descriptive commit message:

```bash
git add .
git commit -m "Add feature: your feature description"
```

3. Push your changes to your fork:

```bash
git push origin feature/your-feature-name
```

4. Create a pull request from your fork to the main repository.

## Pull Request Guidelines

- Follow the coding style and conventions used in the project.
- Write clear, descriptive commit messages.
- Include tests for new features or bug fixes.
- Update documentation as needed.
- Make sure all tests pass before submitting a pull request.
- Keep pull requests focused on a single topic.

## Testing

We use pytest for testing. To run the tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=.
```

## Documentation

We use Markdown for documentation. Please follow these guidelines when writing documentation:

- Use clear, concise language.
- Include examples where appropriate.
- Follow the existing documentation structure (see [documentation-guide.md](documentation-guide.md)).
- Use proper Markdown formatting.
- **All new features and code changes must include relevant documentation updates in the appropriate `docs/` file(s) as part of the pull request.**

## Feedback and Documentation Updates

If you have suggestions for improving documentation, please open an issue with the "documentation" label or contact the maintainer (see [documentation-guide.md](documentation-guide.md) for details).

## IDE Setup

To ensure consistent code formatting and a smooth development experience, we recommend configuring your IDE or editor to use Ruff as the primary formatter. We provide configuration files and detailed setup instructions for popular IDEs:

- **VS Code**: Configuration is provided in `.vscode/settings.json`
- **PyCharm**: Configuration is provided in `.idea/ruff.xml`
- **Other Editors**: Basic formatting settings are provided in `.editorconfig`

For detailed setup instructions, please see the [IDE Setup Guide](ide_setup.md).

## Code Style

We follow the PEP 8 style guide for Python code. We use pre-commit hooks with ruff (for linting and formatting) and pyrefly for type checking:

> **Important Note:**
> This project uses **Ruff** as the primary code formatter, not Black. Please configure your IDE accordingly (see the [IDE Setup Guide](ide_setup.md) for instructions).

**Best Practices:**
> All contributors are expected to review and adhere to the [Claude Agentic Coding Best Practices](../claude_coding_best_practices.md) for safe, reliable, and auditable automation. These include principles like explicit state and input/output handling, modular design, input validation, deterministic steps, and comprehensive documentation and testing.

## Coding Best Practices

All contributors should review and follow the [Claude Agentic Coding Best Practices](../claude_coding_best_practices.md) for safe, reliable, and auditable automation. These include explicit state handling, modular/testable design, strong validation, deterministic steps, idempotency, human oversight, comprehensive documentation, and robust testing. Please see the checklist in that document before submitting changes or pull requests.

```bash
# Run pre-commit hooks on all files
pre-commit run --all-files

# Run pre-commit hooks on staged files
pre-commit run

# Update pre-commit hooks to the latest versions
pre-commit autoupdate
```

You can also run individual tools manually:

```bash
# Check code style and format code with Ruff
ruff check .
ruff format .

# Type checking
pyrefly .

# Run Node.js/unit tests for frontend (if applicable)
pnpm test
```

## License

By contributing to the pAIssive Income Framework, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).

---

> **Summary:**
> - Use **`uv`** for all Python dependency and environment management.
> - Use **`pnpm`** for all Node.js/JavaScript/TypeScript dependencies and scripts.
> - Do **not** use `pip`, `venv`, `npm`, or `yarn` for any development or CI/CD steps.
> - For any questions, see the top of this document or ask a maintainer.

```

By contributing to the pAIssive Income Framework, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).
