# pAIssive Income

A comprehensive framework for developing and monetizing niche AI agents to generate passive income through subscription-based software tools powered by local AI models.

## Overview

This project provides a structured approach to creating specialized AI-powered software tools that solve specific problems for targeted user groups. By focusing on niche markets with specific needs, these tools can provide high value to users while generating recurring subscription revenue.

The framework uses a team of specialized AI agents that collaborate to identify profitable niches, develop solutions, create monetization strategies, and market the products to target users.

## Project Structure

- **Agent Team**: A team of specialized AI agents that collaborate on different aspects of the product development and monetization process.
- **Niche Analysis**: Tools and methodologies for identifying profitable niches and user pain points.
- **Tool Templates**: Development templates for creating AI-powered software solutions.
- **Monetization**: Subscription models and pricing strategies for maximizing recurring revenue.
- **Marketing**: Strategies for reaching target users and promoting the AI tools.
- **UI**: Web interface for interacting with the framework components.

## Agent Team

The project is built around a team of specialized AI agents:

1. **Research Agent**: Identifies market opportunities and user needs in specific niches.
2. **Developer Agent**: Creates AI-powered software solutions to address identified needs.
3. **Monetization Agent**: Designs subscription models and pricing strategies.
4. **Marketing Agent**: Develops strategies for reaching and engaging target users.
5. **Feedback Agent**: Gathers and analyzes user feedback for product improvement.

## Key Features

- **Niche Identification**: Sophisticated analysis tools to identify profitable niches with specific user problems that can be solved with AI.
- **Problem Analysis**: Detailed analysis of user problems and pain points to ensure solutions address real needs.
- **Solution Design**: Templates and frameworks for designing AI-powered software solutions.
- **Monetization Strategy**: Subscription models and pricing strategies optimized for recurring revenue.
- **Marketing Plan**: Comprehensive marketing strategies tailored to each niche and target user group.
- **Feedback Loop**: Tools for gathering and analyzing user feedback to continuously improve products.

## Example Niches

The framework has identified several promising niches for AI-powered tools:

1. **YouTube Script Generator**: AI tools to help YouTube creators write engaging scripts faster.
2. **Study Note Generator**: AI tools to help students create comprehensive study notes from lectures.
3. **Freelance Proposal Writer**: AI tools to help freelancers write compelling client proposals.
4. **Property Description Generator**: AI tools to help real estate agents write compelling property descriptions.
5. **Inventory Management for Small E-commerce**: AI tools to help small e-commerce businesses manage inventory efficiently.

## Getting Started

**For full setup, onboarding, and usage instructions, see [docs/getting-started.md](docs/getting-started.md).**

This repository contains a summary of the project and high-level information. The main onboarding guide, including development setup, installation, and usage details, is maintained in the documentation directory for consistency and easier updates.

If you are new to this project, start here:
- [Getting Started Guide](docs/getting-started.md)

For quick reference, the following topics are included in the full guide:
- Development environment setup (Python, Node, etc.)
- Installing dependencies
- Running and developing with the framework
- Using the CLI and web UI
- Pre-commit hooks and code quality
- Linting, syntax fixes, and CI workflows

**Note:** This README is intentionally concise. See the documentation for complete and up-to-date instructions.

---

### Feedback & Documentation Contributions

To suggest improvements or report issues in the documentation, please:
- [Open an issue](https://github.com/anchapin/pAIssive_income/issues) with the label `documentation`
- Or email the maintainer: a.n.chapin@gmail.com

For documentation contribution standards and process, see [docs/documentation-guide.md](docs/documentation-guide.md).

See [Getting Started Guide](docs/getting-started.md) for full setup and onboarding instructions.

## Documentation Structure

- **Quickstart & Setup:** [docs/getting-started.md](docs/getting-started.md)
- **Framework Overview & Architecture:** [docs/overview.md](docs/overview.md), [docs/architecture/](docs/architecture/)
- **Project Structure:** [docs/project-structure.md](docs/project-structure.md)
- **Agent Team Details:** [docs/agent-team.md](docs/agent-team.md)
- **Niche Analysis:** [docs/niche-analysis.md](docs/niche-analysis.md)
- **AI Models:** [docs/ai-models.md](docs/ai-models.md)
- **Monetization:** [docs/monetization.md](docs/monetization.md)
- **Marketing:** [docs/marketing.md](docs/marketing.md)
- **UI/Web Interface:** [docs/ui.md](docs/ui.md)
- **Tool Templates:** [docs/tool-templates.md](docs/tool-templates.md)
- **API Reference:** [docs/api-reference.md](docs/api-reference.md)
- **DevOps & CI/CD:** [docs/devops-workflow.md](docs/devops-workflow.md)
- **Troubleshooting & FAQ:** [docs/troubleshooting.md](docs/troubleshooting.md), [docs/faq.md](docs/faq.md)
- **Contributing:** [docs/contributing.md](docs/contributing.md)
- **Documentation Guide:** [docs/documentation-guide.md](docs/documentation-guide.md)

## Feedback and Documentation Updates

We welcome feedback and suggestions for improving documentation!
- **For general suggestions or corrections:** Open a GitHub issue with the "documentation" label.
- **For urgent changes or errors:** Contact the project maintainer via [email](mailto:a.n.chapin@gmail.com).

For more on documentation standards and structure, see [docs/documentation-guide.md](docs/documentation-guide.md).

## Example Output

Running the main script generates a complete project plan including:

- Niche analysis with opportunity scores
- Detailed user problem analysis
- Solution design with features and architecture
- Monetization strategy with subscription tiers and revenue projections
- Marketing plan with user personas and channel strategies

## Requirements

- Python 3.8+
- Node.js 14.0+ (for modern UI)
- Dependencies listed in each module's README

## Code Style and Formatting

The project enforces consistent code style and formatting through pre-commit hooks and automated tools. Here are the key formatting guidelines and tools:

### Common Formatting Issues to Watch For

- Trailing whitespace at the end of lines
- Missing newline at end of files
- Inconsistent indentation (use 4 spaces, not tabs)
- Type annotation issues caught by MyPy
- Ruff linting violations (see .ruff.toml for rules)

### Using Pre-commit Hooks

The project uses pre-commit hooks to automatically check and fix common issues. The hooks are installed automatically when setting up the development environment, but you can also install them manually:

```bash
pip install pre-commit
pre-commit install
```

To run all pre-commit hooks manually on all files:

```bash
# Using the provided scripts (recommended)
# On Windows
run_pre_commit.bat

# On Unix/Linux
./run_pre_commit.sh

# Or manually
pre-commit run --all-files
```

To run specific hooks:

```bash
pre-commit run trailing-whitespace --all-files
pre-commit run ruff --all-files
```

### Local Linting Commands

Use these commands to check and fix linting issues:

1. Check for issues without fixing:

```bash
scripts\lint_check.bat  # Windows
./scripts/lint_check.sh  # Unix/Linux
```

1. Fix issues automatically:

```bash
python fix_all_issues_final.py
```

1. Run specific checks:

```bash
scripts\lint_check.bat --ruff  # Run only Ruff
scripts\lint_check.bat --mypy  # Run only MyPy
```

### Code Formatter Configuration

- **Ruff**: The project uses Ruff for both linting and formatting. Configuration is in `.ruff.toml`
- **MyPy**: Type checking configuration is in `mypy.ini`
- **Pre-commit**: Hook configuration is in `.pre-commit-config.yaml`

All configuration files are version controlled to ensure consistent formatting across the project.

## Claude Agentic Coding Best Practices

This project follows [Claude Agentic Coding Best Practices](claude_coding_best_practices.md) for safe, reliable, and auditable automation. All contributors are expected to review and adhere to these standards.

Key principles include:
- Explicit state and input/output handling
- Modular, testable decomposition
- Strong input validation
- Deterministic, auditable steps
- Idempotency and recovery
- Human oversight and review
- Comprehensive documentation
- Unit/integration testing (including edge/failure modes)
- Security and permissions best practices

See [claude_coding_best_practices.md](claude_coding_best_practices.md) for the full checklist and details. Please review this document before submitting changes or pull requests.

## Documentation

The project includes comprehensive API documentation that can be built from source:

1. Navigate to the docs_source directory:

   ```bash
   cd docs_source
   ```

2. Generate the API documentation from source code:

   ```bash
   python generate_api_docs.py
   ```

3. Build the HTML documentation:

   ```bash
   make html
   ```

   On Windows, use:

   ```bash
   make.bat html
   ```

4. The generated documentation will be available in `docs_source/build/html/`

You can view the documentation by opening `docs_source/build/html/index.html` in your web browser.

## Troubleshooting

### CI Workflow Issues

If you encounter issues with the CI workflow, try the following steps:

1. **Syntax and Formatting Issues**: Use the comprehensive fix script to identify and fix issues:

   ```bash
   # Check for issues without fixing
   python fix_all_issues_final.py --check path/to/file.py

   # Fix all issues
   python fix_all_issues_final.py path/to/file.py

   # Or use the batch file
   fix_all_issues.bat path/to/file.py
   ```

2. **Run GitHub Actions Workflow Locally**: Use the dedicated workflow to fix issues:

   ```bash
   # Install act (GitHub Actions local runner)
   # See: https://github.com/nektos/act

   # Run the fix-all-issues workflow
   act -j fix-issues -W .github/workflows/fix-all-issues.yml
   ```

3. **Linting Issues**: Run the linting checks locally to identify and fix issues:

   ```bash
   scripts\lint_check.bat --file path/to/file.py
   ```

4. **Virtual Environment Issues**: If you encounter issues with the virtual environment, recreate it:

   ```bash
   scripts\recreate_venv.bat
   ```

5. **Pre-commit Hook Issues**: If pre-commit hooks are not working correctly, reinstall them:

   ```bash
   # Using the provided script (recommended)
   # On Windows
   setup_pre_commit.bat

   # On Unix/Linux
   ./setup_pre_commit.sh

   # Or manually
   pre-commit uninstall
   pre-commit install
   ```

## License

[MIT License](LICENSE)
