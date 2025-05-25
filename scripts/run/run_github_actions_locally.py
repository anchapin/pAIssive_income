"""run_github_actions_locally - Module for running GitHub Actions workflows locally."""

from __future__ import annotations

# Standard library imports
import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger("run_github_actions_locally")


def _run_linting_tool(
    executable: str, tool_name: str, args: Optional[list[str]] = None
) -> bool:
    """
    Run a linting tool with the given arguments.

    Args:
        executable: Path to the tool executable
        tool_name: Name of the tool (for logging)
        args: Arguments to pass to the tool (defaults to ["."])

    Returns:
        True if the tool ran successfully, False otherwise

    """
    if args is None:
        args = ["."]

    logger.info("Running %s...", tool_name)
    try:
        # nosec comment below tells security scanners this is safe as we control the input
        subprocess.run([executable, *args], check=True)  # nosec B603 S603
        logger.info("%s checks passed", tool_name)
    except subprocess.CalledProcessError:
        logger.exception("%s checks failed", tool_name)
        return False
    else:
        return True


def run_linting() -> bool:
    """Run linting checks locally."""
    logger.info("Running linting checks...")

    # Ensure ruff is installed
    ruff_executable = _ensure_tool_installed("ruff")
    if not ruff_executable:
        return False

    # Ensure mypy is installed
    mypy_executable = _ensure_tool_installed("mypy")
    if not mypy_executable:
        return False

    # Run linting tools
    if not _run_linting_tool(ruff_executable, "ruff", ["check", "."]):
        return False

    if not _run_linting_tool(mypy_executable, "mypy"):
        return False

    logger.info("All linting checks passed")
    return True


def _install_pytest_with_plugins() -> Optional[str]:
    """
    Install pytest and its plugins.

    Returns:
        Path to pytest executable or None if installation failed

    """
    logger.info("Installing pytest and related packages...")
    try:
        # nosec comment below tells security scanners this is safe as we control the input
        subprocess.run(  # nosec B603 S603
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pytest",
                "pytest-cov",
                "pytest-xdist",
                "pytest-asyncio",
            ],
            check=True,
        )
        pytest_executable = shutil.which("pytest")
        if not pytest_executable:
            logger.exception("Failed to install pytest")
            return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.exception("Failed to install pytest")
        return None
    else:
        return pytest_executable


def run_tests(test_path: Optional[str] = None) -> bool:
    """Run tests locally."""
    logger.info("Running tests...")

    # Check if pytest is installed
    pytest_executable = shutil.which("pytest")
    if not pytest_executable:
        logger.info("Pytest not found in PATH")
        pytest_executable = _install_pytest_with_plugins()
        if not pytest_executable:
            return False

    # Run pytest
    logger.info("Running pytest on %s...", test_path or "all tests")
    cmd = [pytest_executable, "-v"]

    if test_path:
        cmd.append(test_path)

    try:
        # nosec comment below tells security scanners this is safe as we control the input
        subprocess.run(cmd, check=True)  # nosec B603 S603
    except subprocess.CalledProcessError:
        logger.exception("Tests failed")
        return False

    logger.info("Tests passed")
    return True


def _ensure_tool_installed(tool_name: str) -> Optional[str]:
    """
    Ensure a security tool is installed and return its path.

    Args:
        tool_name: Name of the tool to install

    Returns:
        Path to the executable or None if installation failed

    """
    executable = shutil.which(tool_name)
    if executable:
        return executable

    logger.info("%s not found in PATH", tool_name)
    logger.info("Installing %s...", tool_name)

    try:
        # nosec comment below tells security scanners this is safe as we control the input
        subprocess.run([sys.executable, "-m", "pip", "install", tool_name], check=True)  # nosec B603 S603

        executable = shutil.which(tool_name)
        if not executable:
            logger.exception("Failed to install %s", tool_name)
            return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.exception("Failed to install %s", tool_name)
        return None
    else:
        return executable


def _run_safety_check(safety_executable: str, output_dir: Optional[str] = None) -> bool:
    """
    Run safety check.

    Args:
        safety_executable: Path to safety executable
        output_dir: Optional directory for output reports

    Returns:
        True if check completed, False otherwise

    """
    logger.info("Running safety...")
    try:
        cmd = [safety_executable, "check"]
        if output_dir:
            output_file = Path(output_dir) / "safety-results.json"
            cmd.extend(["--output", "json", "--output-file", str(output_file)])

        # nosec comment below tells security scanners this is safe as we control the input
        subprocess.run(cmd, check=False)  # nosec B603 S603
        logger.info("Safety check completed")
    except subprocess.CalledProcessError:
        logger.exception("Safety check failed")
        return False
    else:
        return True


def _run_bandit_scan(bandit_executable: str, output_dir: Optional[str] = None) -> bool:
    """
    Run bandit scan.

    Args:
        bandit_executable: Path to bandit executable
        output_dir: Optional directory for output reports

    Returns:
        True if scan completed, False otherwise

    """
    logger.info("Running bandit...")
    try:
        cmd = [bandit_executable, "-r", ".", "--exclude", ".venv,node_modules,tests"]
        if output_dir:
            output_file = Path(output_dir) / "bandit-results.json"
            cmd.extend(["-f", "json", "-o", str(output_file)])

        # nosec comment below tells security scanners this is safe as we control the input
        subprocess.run(cmd, check=False)  # nosec B603 S603
        logger.info("Bandit scan completed")
    except subprocess.CalledProcessError:
        logger.exception("Bandit scan failed")
        return False
    else:
        return True


def run_security_scan(output_dir: Optional[str] = None) -> bool:
    """Run security scan locally."""
    logger.info("Running security scan...")

    # Ensure tools are installed
    safety_executable = _ensure_tool_installed("safety")
    if not safety_executable:
        return False

    bandit_executable = _ensure_tool_installed("bandit")
    if not bandit_executable:
        return False

    # Create output directory if specified
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Run security checks
    safety_result = _run_safety_check(safety_executable, output_dir)
    bandit_result = _run_bandit_scan(bandit_executable, output_dir)

    logger.info("Security scan completed")
    return safety_result and bandit_result


def run_lint_file(file_path: str) -> int:
    """Run linting on a specific file."""
    logger.info("Running linting on file: %s", file_path)

    # Ensure ruff is installed
    ruff_executable = _ensure_tool_installed("ruff")
    if not ruff_executable:
        return 1

    # Run file-specific linting
    try:
        # nosec comment below tells security scanners this is safe as we control the input
        subprocess.run([ruff_executable, "check", file_path], check=True)  # nosec B603 S603
    except subprocess.CalledProcessError:
        logger.exception("Linting failed for %s", file_path)
        return 1

    logger.info("Linting passed for %s", file_path)
    return 0


def main() -> int:
    """Execute the main workflow for running GitHub Actions locally."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Run GitHub Actions workflows locally")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run linting checks")
    lint_parser.add_argument("--file", help="Specific file to lint")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--path", help="Specific test path to run")

    # Security command
    security_parser = subparsers.add_parser("security", help="Run security scan")
    security_parser.add_argument(
        "--output-dir", help="Directory to output security reports"
    )

    args = parser.parse_args()
    exit_code = 0

    if args.command == "lint":
        exit_code = run_lint_file(args.file) if args.file else 0 if run_linting() else 1
    elif args.command == "test":
        exit_code = 0 if run_tests(args.path) else 1
    elif args.command == "security":
        exit_code = 0 if run_security_scan(args.output_dir) else 1
    else:
        parser.print_help()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
