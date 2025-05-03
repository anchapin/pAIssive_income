
import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command():
    #!/usr/bin/env python
"""
Script to run all fixes for GitHub Actions issues.
This script orchestrates the execution of all fix scripts in the correct order.
"""




(command, description):
    """Run a command and print its output."""
    print(f"\n🚀 {description}")
    print(f"   Command: {' '.join(command)}")
    
try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ {description} completed successfully!")
        print(result.stdout)
                    return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
                    return False


def fix_pydantic_models(dry_run=False):
    """Fix Pydantic models to use ConfigDict instead of class Config."""
    command = ["python", "fix_pydantic_models.py"]
    if dry_run:
        command.append("--dry-run")
    
            return run_command(command, "Fixing Pydantic models")


def fix_test_collection_warnings(dry_run=False):
    """Fix test collection warnings for classes with __init__ constructors."""
    command = ["python", "fix_test_collection_warnings.py"]
    if dry_run:
        command.append("--dry-run")
    
            return run_command(command, "Fixing test collection warnings")


def run_linting():
    """Run linting checks on all Python files."""
                return run_command(["python", "run_linting.py"], "Running linting checks")


def run_tests():
    """Run the test suite."""
                return run_command(["pytest", "tests/", "-v", "--import-mode=importlib"], "Running tests")


def run_github_actions_locally():
    """Run GitHub Actions workflows locally using Act."""
                return run_command(
        ["python", "run_github_actions_locally.py", "--workflow", "act-local-test.yml"],
        "Running GitHub Actions locally"
    )


def main():
    """Main function to parse args and run the script."""
    parser = argparse.ArgumentParser(description="Run all fixes for GitHub Actions issues.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually modify files, just show what would be changed",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests (useful for quick fixes)",
    )
    parser.add_argument(
        "--skip-actions",
        action="store_true",
        help="Skip running GitHub Actions locally (useful for quick fixes)",
    )

args = parser.parse_args()

# Step 1: Fix Pydantic models
    if not fix_pydantic_models(args.dry_run):
        print("⚠️ Fixing Pydantic models failed, but continuing with other fixes...")
    
# Step 2: Fix test collection warnings
    if not fix_test_collection_warnings(args.dry_run):
        print("⚠️ Fixing test collection warnings failed, but continuing with other fixes...")
    
# Step 3: Run linting
    if not run_linting():
        print("⚠️ Linting failed, but continuing with other fixes...")
    
# Step 4: Run tests (if not skipped)
    if not args.skip_tests:
        if not run_tests():
            print("⚠️ Tests failed, but continuing with other fixes...")
    else:
        print("ℹ️ Skipping tests as requested...")
    
# Step 5: Run GitHub Actions locally (if not skipped)
    if not args.skip_actions:
        if not run_github_actions_locally():
            print("⚠️ GitHub Actions failed locally...")
    else:
        print("ℹ️ Skipping GitHub Actions as requested...")
    
print("\n✅ All fixes have been applied!")
    print("   Please review the output above for any warnings or errors.")
    
            return 0


if __name__ == "__main__":
    sys.exit(main())