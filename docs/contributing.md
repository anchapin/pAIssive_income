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

- Python 3.8 or higher
- Git
- `uv` (Python package installer and resolver). Install via `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- `pip` (Python package manager, may be needed to install `uv` itself if not using the curl script)
- **pnpm (Node.js package manager for frontend dependencies)**

> **Note:**
> The project now uses [pnpm](https://pnpm.io/) instead of npm for all frontend (JavaScript/TypeScript) dependencies and scripts.
> Please make sure you have pnpm installed. The recommended way is to use Corepack, which is included with Node.js v16.10+ (and v14.19+).
>
> Enable Corepack (if not already enabled):
> ```bash
> corepack enable
> ```
> This will automatically make `pnpm` available.
>
> If you are using an older Node.js version or Corepack is not available, you can install pnpm globally using npm:
> ```bash
> npm install -g pnpm
> ```
>
> Use `pnpm install` instead of `npm install` in all frontend directories.
> For running scripts, use `pnpm exec ...` instead of `npx ...`.

### Setting Up the Development Environment

1. Fork the repository on GitHub.
2. Clone your fork to your local machine:

```bash
git clone https://github.com/your-username/pAIssive_income.git
cd pAIssive_income
```

3. Set up the development environment (one command):

```bash
# On Windows
enhanced_setup_dev_environment.bat

# On Unix/Linux
./enhanced_setup_dev_environment.sh
# Or if running the Python script directly:
# python enhanced_setup_dev_environment.py
```

This script will use `uv` to:
- Create a virtual environment (`.venv`) using `uv venv`
- Install dependencies from `requirements.txt` and `requirements-dev.txt` using `uv pip install`
- Install the project in editable mode (`-e .`) using `uv pip install`
- Set up pre-commit hooks (installing `pre-commit` via `uv pip install`)
- Configure IDE settings for VS Code and PyCharm
- Create .editorconfig for editor-agnostic settings

Or manually (using `uv`):

```bash
# Create virtual environment (e.g., with Python 3.12)
uv venv .venv --python 3.12 
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
# Install dependencies
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt  # Development dependencies
uv pip install -e .
# Install pre-commit and hooks
uv pip install pre-commit
pre-commit install
```

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

We follow the PEP 8 style guide for Python code. We use pre-commit hooks with flake8, ruff, and mypy for code linting, formatting, and type checking:

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
# Check code style
flake8

# Format code with Ruff
ruff format .


# Comprehensive linting with ruff
ruff check .

# Type checking
mypy .
```

## License

By contributing to the pAIssive Income Framework, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).
