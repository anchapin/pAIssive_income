#!/usr/bin/env python3
"""
Tests for setup scripts validation.

These tests validate that the setup scripts have proper structure,
error handling, and contain expected functionality.
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestSetupScripts:
    """Test suite for setup scripts."""

    def test_setup_sh_exists(self) -> None:
        """Test that setup.sh exists and is executable."""
        setup_sh = PROJECT_ROOT / "setup.sh"
        assert setup_sh.exists(), "setup.sh should exist in project root"
        assert setup_sh.is_file(), "setup.sh should be a regular file"

        # Check if it's executable (on Unix systems)
        if os.name != "nt":  # Not Windows
            assert os.access(setup_sh, os.X_OK), "setup.sh should be executable"

    def test_setup_bat_exists(self) -> None:
        """Test that setup.bat exists."""
        setup_bat = PROJECT_ROOT / "setup.bat"
        assert setup_bat.exists(), "setup.bat should exist in project root"
        assert setup_bat.is_file(), "setup.bat should be a regular file"

    def test_setup_sh_syntax(self) -> None:
        """Test that setup.sh has valid bash syntax."""
        setup_sh = PROJECT_ROOT / "setup.sh"

        # Use bash -n to check syntax without executing
        result = subprocess.run(
            ["bash", "-n", str(setup_sh)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        assert result.returncode == 0, f"setup.sh has syntax errors: {result.stderr}"

    def test_setup_sh_contains_required_steps(self) -> None:
        """Test that setup.sh contains all required setup steps."""
        setup_sh = PROJECT_ROOT / "setup.sh"
        content = setup_sh.read_text(encoding="utf-8")

        # Required steps/patterns to check for
        required_patterns = [
            "enhanced_setup_dev_environment.py",  # Python setup script
            "pnpm install",  # Node.js dependencies
            ".env.example",  # Environment file setup
            "init_db.py",  # Database initialization
            "set -e",  # Exit on error
        ]

        for pattern in required_patterns:
            assert pattern in content, f"setup.sh should contain '{pattern}'"

    def test_setup_bat_contains_required_steps(self) -> None:
        """Test that setup.bat contains all required setup steps."""
        setup_bat = PROJECT_ROOT / "setup.bat"
        content = setup_bat.read_text(encoding="utf-8")

        # Required steps/patterns to check for
        required_patterns = [
            "enhanced_setup_dev_environment.py",  # Python setup script
            "pnpm install",  # Node.js dependencies
            ".env.example",  # Environment file setup
            "init_db.py",  # Database initialization
            "ERRORLEVEL",  # Error checking
        ]

        for pattern in required_patterns:
            assert pattern in content, f"setup.bat should contain '{pattern}'"

    def test_setup_scripts_have_error_handling(self) -> None:
        """Test that both setup scripts have proper error handling."""
        setup_sh = PROJECT_ROOT / "setup.sh"
        setup_bat = PROJECT_ROOT / "setup.bat"

        sh_content = setup_sh.read_text(encoding="utf-8")
        bat_content = setup_bat.read_text(encoding="utf-8")

        # Check bash error handling
        assert "set -e" in sh_content, (
            "setup.sh should have 'set -e' for error handling"
        )
        assert "exit 1" in sh_content, "setup.sh should have explicit error exits"

        # Check batch error handling
        assert "ERRORLEVEL" in bat_content, "setup.bat should check ERRORLEVEL"
        assert "exit /b 1" in bat_content, "setup.bat should have explicit error exits"

    def test_setup_scripts_have_project_name_consistency(self) -> None:
        """Test that setup scripts use consistent project naming."""
        setup_sh = PROJECT_ROOT / "setup.sh"
        setup_bat = PROJECT_ROOT / "setup.bat"

        sh_content = setup_sh.read_text(encoding="utf-8")
        bat_content = setup_bat.read_text(encoding="utf-8")

        # Should contain correct project name
        assert "pAIssive Income" in sh_content, (
            "setup.sh should use 'pAIssive Income' project name"
        )
        assert "pAIssive Income" in bat_content, (
            "setup.bat should use 'pAIssive Income' project name"
        )

        # Should not contain old references
        assert "jules.google.com" not in sh_content, (
            "setup.sh should not contain 'jules.google.com'"
        )
        assert "jules.google.com" not in bat_content, (
            "setup.bat should not contain 'jules.google.com'"
        )

    def test_setup_scripts_have_working_directory_robustness(self) -> None:
        """Test that setup scripts handle working directory properly."""
        setup_sh = PROJECT_ROOT / "setup.sh"
        setup_bat = PROJECT_ROOT / "setup.bat"

        sh_content = setup_sh.read_text(encoding="utf-8")
        bat_content = setup_bat.read_text(encoding="utf-8")

        # Bash script should change to script directory
        assert "SCRIPT_DIR=" in sh_content, "setup.sh should determine script directory"
        assert "cd " in sh_content, "setup.sh should change to script directory"

        # Batch script should use pushd/popd
        assert "pushd" in bat_content, (
            "setup.bat should use pushd for directory management"
        )
        assert "popd" in bat_content, (
            "setup.bat should use popd for directory restoration"
        )

    def test_python_setup_script_exists(self) -> None:
        """Test that the referenced Python setup script exists."""
        python_script = (
            PROJECT_ROOT / "scripts" / "setup" / "enhanced_setup_dev_environment.py"
        )
        assert python_script.exists(), "enhanced_setup_dev_environment.py should exist"
        assert python_script.is_file(), (
            "enhanced_setup_dev_environment.py should be a regular file"
        )

    @pytest.mark.integration
    def test_setup_sh_dry_run(self) -> None:
        """Test setup.sh with a dry run approach (check initial steps only)."""
        if os.name == "nt":  # Skip on Windows
            pytest.skip("Skipping bash test on Windows")

        setup_sh = PROJECT_ROOT / "setup.sh"

        # Create a temporary directory to test from
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the setup script to temp directory
            temp_setup = Path(temp_dir) / "setup.sh"
            temp_setup.write_text(setup_sh.read_text())
            temp_setup.chmod(0o755)

            # Run just the syntax and initial checks
            # Note: This would require modifications to the script for proper testing
            # For now, we just verify the script can be parsed
            result = subprocess.run(
                ["bash", "-n", str(temp_setup)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            assert result.returncode == 0, (
                f"setup.sh failed syntax check: {result.stderr}"
            )

    def test_setup_scripts_have_informative_output(self) -> None:
        """Test that setup scripts provide informative output messages."""
        setup_sh = PROJECT_ROOT / "setup.sh"
        setup_bat = PROJECT_ROOT / "setup.bat"

        sh_content = setup_sh.read_text(encoding="utf-8")
        bat_content = setup_bat.read_text(encoding="utf-8")

        # Should have step indicators
        for content in [sh_content, bat_content]:
            assert "STEP 1" in content, "Scripts should have numbered steps"
            assert "STEP 2" in content, "Scripts should have numbered steps"
            assert "echo" in content, "Scripts should provide user feedback"
            assert "WARNING:" in content, (
                "Scripts should provide warnings when appropriate"
            )
            assert "ERROR:" in content, "Scripts should provide error messages"


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    pytest.main([__file__, "-v"])
