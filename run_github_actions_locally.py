"""
Script to run GitHub Actions locally using Act.
"""

import sys
import subprocess
import argparse

def main():
    """Run GitHub Actions locally using Act."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run GitHub Actions locally using Act.")
    parser.add_argument("--workflow", default=".github/workflows/local-test.yml", help="Path to the workflow file")
    parser.add_argument("--job", default="test", help="Job to run")
    parser.add_argument("--platform", default="ubuntu-latest=node:16-buster", help="Platform to use")
    args = parser.parse_args()
    
    # Build the command
    cmd = ["act", "-j", args.job, "-W", args.workflow]
    
    if args.platform:
        cmd.extend(["-P", args.platform])
    
    # Run Act
    print(f"Running Act: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        check=False,
    )
    
    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
