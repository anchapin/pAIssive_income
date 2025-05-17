"""run_github_actions_locally - Module for running GitHub Actions workflows locally."""

# Standard library imports
import os
import sys
import argparse
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_github_actions_locally")

def run_linting():
    """Run linting checks locally."""
    logger.info("Running linting checks...")

    # Check if ruff is installed
    try:
        subprocess.run(["ruff", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Installing ruff...")
        subprocess.run([sys.executable, "-m", "pip", "install", "ruff"], check=True)

    # Run ruff
    logger.info("Running ruff...")
    try:
        subprocess.run(["ruff", "check", "."], check=True)
        logger.info("Ruff checks passed")
    except subprocess.CalledProcessError:
        logger.exception("Ruff checks failed")
        return False

    # Check if mypy is installed
    try:
        subprocess.run(["mypy", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Installing mypy...")
        subprocess.run([sys.executable, "-m", "pip", "install", "mypy"], check=True)

    # Run mypy
    logger.info("Running mypy...")
    try:
        subprocess.run(["mypy", "."], check=True)
        logger.info("Mypy checks passed")
    except subprocess.CalledProcessError:
        logger.exception("Mypy checks failed")
        return False

    logger.info("All linting checks passed")
    return True

def run_tests(test_path=None):
    """Run tests locally."""
    logger.info("Running tests...")

    # Check if pytest is installed
    try:
        subprocess.run(["pytest", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Installing pytest and related packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov", "pytest-xdist", "pytest-asyncio"], check=True)

    # Run pytest
    logger.info(f"Running pytest on {test_path or 'all tests'}...")
    cmd = ["pytest", "-v"]

    if test_path:
        cmd.append(test_path)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        logger.exception("Tests failed")
        return False

    logger.info("Tests passed")
    return True

def run_security_scan(output_dir=None):
    """Run security scan locally."""
    logger.info("Running security scan...")

    # Check if safety is installed
    try:
        subprocess.run(["safety", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Installing safety...")
        subprocess.run([sys.executable, "-m", "pip", "install", "safety"], check=True)

    # Check if bandit is installed
    try:
        subprocess.run(["bandit", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Installing bandit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "bandit"], check=True)

    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Run safety
    logger.info("Running safety...")
    try:
        cmd = ["safety", "check"]
        if output_dir:
            cmd.extend(["--output", "json", "--output-file", os.path.join(output_dir, "safety-results.json")])
        subprocess.run(cmd, check=False)
        logger.info("Safety check completed")
    except subprocess.CalledProcessError:
        logger.exception("Safety check failed")

    # Run bandit
    logger.info("Running bandit...")
    try:
        cmd = ["bandit", "-r", ".", "--exclude", ".venv,node_modules,tests"]
        if output_dir:
            cmd.extend(["-f", "json", "-o", os.path.join(output_dir, "bandit-results.json")])
        subprocess.run(cmd, check=False)
        logger.info("Bandit scan completed")
    except subprocess.CalledProcessError:
        logger.exception("Bandit scan failed")

    logger.info("Security scan completed")
    return True

def main():
    """Main function."""
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
    security_parser.add_argument("--output-dir", help="Directory to output security reports")

    args = parser.parse_args()

    if args.command == "lint":
        if args.file:
            logger.info(f"Running linting on file: {args.file}")
            # Run file-specific linting
            try:
                subprocess.run(["ruff", "check", args.file], check=True)
            except subprocess.CalledProcessError:
                logger.exception(f"Linting failed for {args.file}")
                return 1

            logger.info(f"Linting passed for {args.file}")
            return 0
        return 0 if run_linting() else 1

    elif args.command == "test":
        return 0 if run_tests(args.path) else 1

    elif args.command == "security":
        return 0 if run_security_scan(args.output_dir) else 1

    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
