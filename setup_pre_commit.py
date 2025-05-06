"""Script to set up pre-commit hooks for the project."""

import subprocess
import sys


def run_command(command):
    """Run a command and return its output."""
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def main():
    """Set up pre-commit hooks."""
    # Check if we're in a git repository:
    try:
        run_command(["git", "rev-parse", "--git-dir"])
    except subprocess.CalledProcessError:
        print("Error: Not a git repository. Please initialize git first.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Git executable not found. Please install git and try again.")
        sys.exit(1)

    # Install pre-commit if not already installed:
    print("Installing pre-commit...")
    run_command([sys.executable, "-m", "pip", "install", "pre-commit"])

    # Install the pre-commit hooks
    print("Installing pre-commit hooks...")
    run_command(["pre-commit", "install"])

    # Update all hooks to latest versions
    print("Updating pre-commit hooks...")
    run_command(["pre-commit", "autoupdate"])

    print("\nPre-commit has been set up successfully!")
    print("The hooks will now run automatically on git commit.")
    print("You can also run them manually with: pre-commit run --all-files")


if __name__ == "__main__":
    main()
