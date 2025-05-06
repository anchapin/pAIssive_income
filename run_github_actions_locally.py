"""Run GitHub Actions workflows locally.

A script for running Github Actions workflows locally for the pAIssive Income project.
"""

import argparse
import os
import subprocess
import sys


def ensure_sarif_tools():
    """Install and verify sarif-tools installation."""
    print("Verifying sarif-tools installation...")
    try:
        # Force reinstall sarif-tools to ensure we have the latest version
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--user",
                "sarif-tools",
                "--force-reinstall",
            ],
            check=True,
        )

        # Try to run sarif-tools to verify installation
        result = subprocess.run(
            ["sarif-tools", "--help"], capture_output=True, text=True
        )
        if result.returncode != 0:
            # Try with full path if direct command fails
            home_dir = os.path.expanduser("~")
            local_bin = os.path.join(home_dir, ".local", "bin")
            sarif_path = os.path.join(local_bin, "sarif-tools")

            if os.path.exists(sarif_path):
                print(f"sarif-tools found at: {sarif_path}")
                # Add to PATH for future use
                os.environ["PATH"] = f"{local_bin}{os.pathsep}{os.environ['PATH']}"
                return True
            else:
                print("sarif-tools not found in ~/.local/bin. Trying to locate...")
                # Try to find where pip installed it
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", "sarif-tools"],
                    capture_output=True,
                    text=True,
                )
                print(f"Pip show sarif-tools: {result.stdout}")
                return False
        return True
    except Exception as e:
        print(f"Error installing or verifying sarif-tools: {e}")
        return False


def run_bandit_scan(output_dir):
    """Run Bandit security scanner and convert results to SARIF format."""
    print("Running Bandit security scanner...")
    os.makedirs(output_dir, exist_ok=True)

    # Run Bandit scan
    bandit_output = os.path.join(output_dir, "bandit-results.json")
    try:
        subprocess.run(
            ["bandit", "-r", ".", "-f", "json", "-o", bandit_output], check=True
        )
        print(f"Bandit scan completed. Results saved to {bandit_output}")
    except subprocess.CalledProcessError:
        print("Bandit scan completed with warnings or errors.")
        if not os.path.exists(bandit_output) or os.path.getsize(bandit_output) == 0:
            print("No Bandit results generated.")
            return False

    # Convert Bandit results to SARIF format
    sarif_output = os.path.join(output_dir, "bandit-results.sarif")
    print("Converting Bandit results to SARIF format...")

    # Try multiple methods to convert to SARIF
    try:
        # Try direct sarif-tools command
        subprocess.run(
            ["sarif-tools", "convert", bandit_output, "-o", sarif_output], check=True
        )
    except subprocess.CalledProcessError:
        try:
            # Try with python module
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sarif_tools",
                    "convert",
                    bandit_output,
                    "-o",
                    sarif_output,
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            try:
                # Try with full path
                home_dir = os.path.expanduser("~")
                sarif_path = os.path.join(home_dir, ".local", "bin", "sarif-tools")
                if os.path.exists(sarif_path):
                    subprocess.run(
                        [sarif_path, "convert", bandit_output, "-o", sarif_output],
                        check=True,
                    )
                else:
                    print("Failed to locate sarif-tools executable.")
                    print("Creating empty SARIF file as fallback...")
                    with open(sarif_output, "w") as f:
                        f.write('{"version":"2.1.0","runs":[]}')
                    return False
            except subprocess.CalledProcessError:
                print("All attempts to convert Bandit results to SARIF failed.")
                print("Creating empty SARIF file as fallback...")
                with open(sarif_output, "w") as f:
                    f.write('{"version":"2.1.0","runs":[]}')
                return False

    print(f"Successfully converted Bandit results to SARIF format at {sarif_output}")
    return True


def run_security_scan(output_dir=None):
    """Run security scan similar to the GitHub Actions workflow."""
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "security-reports")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Verify sarif-tools installation
    if not ensure_sarif_tools():
        print("WARNING: sarif-tools installation verification failed.")
        print("Attempting to continue with security scan...")

    # Step 2: Run Bandit scan
    if not run_bandit_scan(output_dir):
        print("Bandit scan had issues but will continue with other checks.")

    # Step 3: Run safety check
    print("Running safety check...")
    try:
        safety_output = os.path.join(output_dir, "safety-results.json")
        subprocess.run(
            ["safety", "check", "--json"], stdout=open(safety_output, "w"), check=True
        )
        print(f"Safety check completed. Results saved to {safety_output}")
    except subprocess.CalledProcessError:
        print("Safety check completed with warnings.")
    except FileNotFoundError:
        print(
            "Safety command not found. Make sure to install it with: pip install safety"
        )

    # Step 4: Run pip-audit
    print("Running pip-audit...")
    try:
        pip_audit_output = os.path.join(output_dir, "pip-audit-results.json")
        subprocess.run(
            ["pip-audit", "--format", "json"],
            stdout=open(pip_audit_output, "w"),
            check=True,
        )
        print(f"pip-audit completed. Results saved to {pip_audit_output}")
    except subprocess.CalledProcessError:
        print("pip-audit completed with warnings.")
    except FileNotFoundError:
        print(
            """pip-audit command not found.
            Make sure to install it with: pip install pip-audit
            """
        )

    print(f"\nSecurity scan completed! Results are available in: {output_dir}")
    return 0


def run_linting(specific_file=None):
    """Run linting checks similar to GitHub Actions workflow."""
    print("Running linting checks...")

    commands = []
    if specific_file:
        print(f"Linting specific file: {specific_file}")
        commands = [
            ["ruff", "check", specific_file],
            ["ruff", "format", "--check", specific_file],
            [
                "mypy",
                specific_file,
                "--ignore-missing-imports",
                "--install-types",
                "--non-interactive",
                "--explicit-package-bases",
            ],
            ["pyright", specific_file],
        ]
    else:
        print("Linting all files")
        commands = [
            ["ruff", "check", "."],
            ["ruff", "format", "--check", "."],
            [
                "mypy",
                ".",
                "--ignore-missing-imports",
                "--install-types",
                "--non-interactive",
                "--explicit-package-bases",
            ],
            ["pyright", "."],
        ]

    success = True
    for cmd in commands:
        try:
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print(f"Command failed: {' '.join(cmd)}")
            success = False
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}. Make sure it's installed.")
            success = False

    return 0 if success else 1


def run_tests(test_path=None):
    """Run tests similar to GitHub Actions workflow."""
    print("Running tests...")

    cmd = ["pytest"]
    if test_path:
        print(f"Testing path: {test_path}")
        cmd.append(test_path)
    else:
        print("Running all tests")
        cmd.append("tests")

    cmd.extend(
        [
            "-n",
            "auto",
            "-v",
            "--import-mode=importlib",
            "--cov=.",
            "--cov-report=xml",
            "--cov-report=term-missing",
            "--junitxml=junit/test-results.xml",
        ]
    )

    try:
        os.makedirs("junit", exist_ok=True)
        subprocess.run(cmd, check=True)
        print("\nTests completed successfully!")
        return 0
    except subprocess.CalledProcessError:
        print("\nSome tests failed.")
        return 1


def main():
    """Initialize the module."""
    parser = argparse.ArgumentParser(
        description="""
            Run GitHub Actions workflows locally
            for the pAIssive Income project
            """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Security scan command
    security_parser = subparsers.add_parser("security", help="Run security scan")
    security_parser.add_argument(
        "--output-dir",
        default="./security-reports",
        help="Directory to store security reports",
    )

    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run linting checks")
    lint_parser.add_argument("--file", help="Specific file to lint")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--path", help="Specific test path to run")

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, show help and exit
    if not args.command:
        parser.print_help()
        return 0

    # Run the specified command
    if args.command == "security":
        return run_security_scan(args.output_dir)
    elif args.command == "lint":
        return run_linting(args.file)
    elif args.command == "test":
        return run_tests(args.path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
