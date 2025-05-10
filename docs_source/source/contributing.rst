.. _contributing:

Contributing
===========

Thank you for considering contributing to pAIssive_income! This guide will help you get started with development and explain how to contribute effectively.

Setting Up Development Environment
--------------------------------

1. Clone the repository:

   .. code-block: bash

      git clone https://github.com/username/pAIssive_income.git
      cd pAIssive_income

2. Create a virtual environment:

   .. code-block: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install development dependencies:

   .. code-block: bash

      uv pip install -e ".[dev]"

Code Standards
------------

We follow these coding standards:

- PEP 8 style guide
- Type hints for all function parameters and return values
- Docstrings in Google format for all public functions and classes
- Maximum line length of 100 characters
- Tests for all new functionality

To check your code:

.. code-block: bash

   # Run linting checks
   flake8 .

   # Run type checking
   mypy .

   # Run tests
   pytest

Pull Request Process
------------------

1. Create a feature branch:

   .. code-block: bash

      git checkout -b feature/your-feature-name

2. Make your changes and commit with descriptive messages:

   .. code-block: bash

      git commit -m "Add feature X"

3. Push your branch:

   .. code-block: bash

      git push origin feature/your-feature-name

4. Create a Pull Request on GitHub.

5. Ensure all tests pass and your code meets the standards.

6. Wait for a maintainer to review your PR.

Documentation Guidelines
----------------------

When writing documentation:

- Use clear, concise language
- Provide examples for complex features
- Update docstrings and in-line comments
- Add to the relevant documentation files in the `docs_source` directory

To build documentation locally:

.. code-block: bash

   cd docs_source
   make html
   # Documentation will be available in docs_source/build/html/

Adding New Modules
----------------

When adding new modules:

1. Follow the existing module structure
2. Create appropriate interfaces in the `interfaces` package
3. Add unit tests for all functionality
4. Update documentation
5. Add example usage

Releasing
--------

The maintainers will handle releases using the following process:

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a new git tag
4. Build and publish to PyPI

Questions?
---------

If you have any questions, feel free to:

- Open an issue on GitHub
- Contact the maintainers directly
- Join our community forum/chat
