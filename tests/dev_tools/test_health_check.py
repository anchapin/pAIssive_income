"""test_health_check - Module for tests/dev_tools.test_health_check."""

# Standard library imports
import logging
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Local imports
from dev_tools.health_check import (
    run,
    check_gitignore,
    lint,
    type_check,
    security,
    deps,
    docs,
    usage,
    main,
)


class TestHealthCheck(unittest.TestCase):
    """Test suite for health_check module."""

    @patch("dev_tools.health_check.subprocess.run")
    @patch("dev_tools.health_check.logging.info")
    @patch("dev_tools.health_check.logging.error")
    @patch("dev_tools.health_check.sys.exit")
    def test_run_success(self, mock_exit, mock_error, mock_info, mock_subprocess_run):
        """Test run function with successful command."""
        # Arrange
        mock_subprocess_run.return_value.returncode = 0
        cmd = "echo 'test'"
        desc = "Test command"

        # Act
        run(cmd, desc)

        # Assert
        mock_subprocess_run.assert_called_once_with(cmd.split(), shell=False, check=False)
        mock_info.assert_has_calls([
            call(f"\n==> {desc}"),
            call(f"PASSED: {desc}")
        ])
        mock_error.assert_not_called()
        mock_exit.assert_not_called()

    @patch("dev_tools.health_check.subprocess.run")
    @patch("dev_tools.health_check.logging.info")
    @patch("dev_tools.health_check.logging.error")
    @patch("dev_tools.health_check.sys.exit")
    def test_run_failure(self, mock_exit, mock_error, mock_info, mock_subprocess_run):
        """Test run function with failed command."""
        # Arrange
        mock_subprocess_run.return_value.returncode = 1
        cmd = "invalid_command"
        desc = "Invalid command"

        # Act
        run(cmd, desc)

        # Assert
        mock_subprocess_run.assert_called_once_with(cmd.split(), shell=False, check=False)
        mock_info.assert_called_once_with(f"\n==> {desc}")
        mock_error.assert_called_once_with(f"FAILED: {desc}")
        mock_exit.assert_called_once_with(1)

    def test_check_gitignore(self):
        """Test check_gitignore function."""
        # Act
        result = check_gitignore("/path/to/file")

        # Assert
        self.assertTrue(result)

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_lint_with_ruff(self, mock_warning, mock_run, mock_which):
        """Test lint function with ruff available."""
        # Arrange
        mock_which.return_value = "/path/to/ruff"

        # Act
        lint()

        # Assert
        mock_which.assert_called_once_with("ruff")
        mock_run.assert_has_calls([
            call("ruff check .", "Ruff linting"),
            call("ruff format --check .", "Ruff formatting check")
        ])
        mock_warning.assert_not_called()

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_lint_without_ruff(self, mock_warning, mock_run, mock_which):
        """Test lint function without ruff available."""
        # Arrange
        mock_which.return_value = None

        # Act
        lint()

        # Assert
        mock_which.assert_called_once_with("ruff")
        mock_run.assert_not_called()
        mock_warning.assert_called_once_with("ruff not found, skipping linting and formatting checks.")

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_type_check_with_mypy(self, mock_warning, mock_run, mock_which):
        """Test type_check function with mypy available."""
        # Arrange
        mock_which.return_value = "/path/to/mypy"

        # Act
        type_check()

        # Assert
        mock_which.assert_called_once_with("mypy")
        mock_run.assert_called_once_with("mypy .", "Mypy static type checking")
        mock_warning.assert_not_called()

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_type_check_without_mypy(self, mock_warning, mock_run, mock_which):
        """Test type_check function without mypy available."""
        # Arrange
        mock_which.return_value = None

        # Act
        type_check()

        # Assert
        mock_which.assert_called_once_with("mypy")
        mock_run.assert_not_called()
        mock_warning.assert_called_once_with("mypy not found, skipping type checks.")

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_security_with_bandit(self, mock_warning, mock_run, mock_which):
        """Test security function with bandit available."""
        # Arrange
        mock_which.return_value = "/path/to/bandit"

        # Act
        security()

        # Assert
        mock_which.assert_called_once_with("bandit")
        mock_run.assert_called_once_with("bandit -r . -x tests", "Bandit security scan")
        mock_warning.assert_not_called()

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_security_without_bandit(self, mock_warning, mock_run, mock_which):
        """Test security function without bandit available."""
        # Arrange
        mock_which.return_value = None

        # Act
        security()

        # Assert
        mock_which.assert_called_once_with("bandit")
        mock_run.assert_not_called()
        mock_warning.assert_called_once_with("bandit not found, skipping security checks.")

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_deps_with_uv(self, mock_warning, mock_run, mock_which):
        """Test deps function with uv available."""
        # Arrange
        mock_which.return_value = "/path/to/uv"

        # Act
        deps()

        # Assert
        mock_which.assert_called_once_with("uv")
        mock_run.assert_called_once_with("uv pip audit", "Python dependency audit")
        mock_warning.assert_not_called()

    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_deps_without_uv(self, mock_warning, mock_run, mock_which):
        """Test deps function without uv available."""
        # Arrange
        mock_which.return_value = None

        # Act
        deps()

        # Assert
        mock_which.assert_called_once_with("uv")
        mock_run.assert_not_called()
        mock_warning.assert_called_once_with("uv not found, skipping dependency audit.")

    @patch("dev_tools.health_check.os.path.isdir")
    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_docs_with_sphinx(self, mock_warning, mock_run, mock_which, mock_isdir):
        """Test docs function with sphinx available."""
        # Arrange
        mock_isdir.return_value = True
        mock_which.return_value = "/path/to/sphinx-build"

        # Act
        docs()

        # Assert
        mock_isdir.assert_called_once_with("docs_source")
        mock_which.assert_called_once_with("sphinx-build")
        mock_run.assert_called_once_with(
            "sphinx-build docs_source docs/_build",
            "Sphinx documentation build",
        )
        mock_warning.assert_not_called()

    @patch("dev_tools.health_check.os.path.isdir")
    @patch("dev_tools.health_check.shutil.which")
    @patch("dev_tools.health_check.run")
    @patch("dev_tools.health_check.logging.warning")
    def test_docs_without_sphinx(self, mock_warning, mock_run, mock_which, mock_isdir):
        """Test docs function without sphinx available."""
        # Arrange
        mock_isdir.return_value = True
        mock_which.return_value = None

        # Act
        docs()

        # Assert
        mock_isdir.assert_called_once_with("docs_source")
        mock_which.assert_called_once_with("sphinx-build")
        mock_run.assert_not_called()
        mock_warning.assert_called_once_with("Sphinx not configured or not found, skipping docs build.")

    @patch("dev_tools.health_check.os.path.isdir")
    @patch("dev_tools.health_check.logging.warning")
    def test_docs_without_docs_source(self, mock_warning, mock_isdir):
        """Test docs function without docs_source directory."""
        # Arrange
        mock_isdir.return_value = False

        # Act
        docs()

        # Assert
        mock_isdir.assert_called_once_with("docs_source")
        mock_warning.assert_called_once_with("Sphinx not configured or not found, skipping docs build.")

    @patch("dev_tools.health_check.logging.info")
    def test_usage(self, mock_info):
        """Test usage function."""
        # Act
        usage()

        # Assert
        mock_info.assert_called_once()

    @patch("dev_tools.health_check.sys.argv", ["health_check.py"])
    @patch("dev_tools.health_check.lint")
    @patch("dev_tools.health_check.type_check")
    @patch("dev_tools.health_check.security")
    @patch("dev_tools.health_check.deps")
    @patch("dev_tools.health_check.docs")
    def test_main_no_args(self, mock_docs, mock_deps, mock_security, mock_type_check, mock_lint):
        """Test main function with no arguments."""
        # Act
        main()

        # Assert
        mock_lint.assert_called_once()
        mock_type_check.assert_called_once()
        mock_security.assert_called_once()
        mock_deps.assert_called_once()
        mock_docs.assert_called_once()

    @patch("dev_tools.health_check.sys.argv", ["health_check.py", "--all"])
    @patch("dev_tools.health_check.lint")
    @patch("dev_tools.health_check.type_check")
    @patch("dev_tools.health_check.security")
    @patch("dev_tools.health_check.deps")
    @patch("dev_tools.health_check.docs")
    def test_main_all_arg(self, mock_docs, mock_deps, mock_security, mock_type_check, mock_lint):
        """Test main function with --all argument."""
        # Act
        main()

        # Assert
        mock_lint.assert_called_once()
        mock_type_check.assert_called_once()
        mock_security.assert_called_once()
        mock_deps.assert_called_once()
        mock_docs.assert_called_once()

    @patch("dev_tools.health_check.sys.argv", ["health_check.py", "--lint", "--security"])
    @patch("dev_tools.health_check.lint")
    @patch("dev_tools.health_check.type_check")
    @patch("dev_tools.health_check.security")
    @patch("dev_tools.health_check.deps")
    @patch("dev_tools.health_check.docs")
    def test_main_specific_args(self, mock_docs, mock_deps, mock_security, mock_type_check, mock_lint):
        """Test main function with specific arguments."""
        # Act
        main()

        # Assert
        mock_lint.assert_called_once()
        mock_type_check.assert_not_called()
        mock_security.assert_called_once()
        mock_deps.assert_not_called()
        mock_docs.assert_not_called()

    @patch("dev_tools.health_check.sys.argv", ["health_check.py", "--help"])
    @patch("dev_tools.health_check.usage")
    @patch("dev_tools.health_check.lint")
    @patch("dev_tools.health_check.type_check")
    @patch("dev_tools.health_check.security")
    @patch("dev_tools.health_check.deps")
    @patch("dev_tools.health_check.docs")
    def test_main_help_arg(self, mock_docs, mock_deps, mock_security, mock_type_check, mock_lint, mock_usage):
        """Test main function with --help argument."""
        # Act
        main()

        # Assert
        mock_usage.assert_called_once()
        mock_lint.assert_not_called()
        mock_type_check.assert_not_called()
        mock_security.assert_not_called()
        mock_deps.assert_not_called()
        mock_docs.assert_not_called()
