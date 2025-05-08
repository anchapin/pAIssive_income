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
- pip (Python package manager)

### Setting Up the Development Environment

1. Fork the repository on GitHub.
2. Clone your fork to your local machine:

```bash
git clone https://github.com/your-username/pAIssive_income.git
cd pAIssive_income
```

3. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. Set up pre-commit hooks:

```bash
# On Windows
setup_pre_commit.bat

# On Unix/Linux
python setup_pre_commit.py

# Or manually
pip install pre-commit
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

## Feedback and Documentation Updates

If you have suggestions for improving documentation, please open an issue with the "documentation" label or contact the maintainer (see [documentation-guide.md](documentation-guide.md) for details).

## Code Style

We follow the PEP 8 style guide for Python code. We use pre-commit hooks with flake8, black, isort, ruff, and mypy for code linting, formatting, and type checking:

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

# Format code
black .

# Sort imports
isort .

# Comprehensive linting with ruff
ruff check .

# Type checking
mypy .
```

## License

By contributing to the pAIssive Income Framework, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).
