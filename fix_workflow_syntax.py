#!/usr/bin/env python3
"""
Fix GitHub Actions workflow syntax errors.

This script fixes the common issue where workflow files have "true:" instead of "on:"
at the beginning, which causes workflow failures.
"""

from pathlib import Path
from typing import Optional


def fix_workflow_file(file_path) -> Optional[bool]:
    """Fix a single workflow file by replacing 'true:' with 'on:' at the beginning."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if the file starts with 'true:' (possibly after name declaration)
        lines = content.split("\n")
        fixed = False

        for i, line in enumerate(lines):
            # Look for lines that are exactly 'true:' or start with 'true:'
            if line.strip() == "true:":
                lines[i] = "on:"
                fixed = True
                break
            if line.startswith("true:"):
                # Handle cases where there might be content after 'true:'
                lines[i] = line.replace("true:", "on:", 1)
                fixed = True
                break

        if fixed:
            # Write the fixed content back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return True
        return False

    except Exception:
        return False


def main() -> None:
    """Main function to fix all workflow files."""
    # Find all YAML files in .github/workflows/
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        return

    yaml_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    if not yaml_files:
        return


    fixed_count = 0
    for yaml_file in yaml_files:
        if fix_workflow_file(yaml_file):
            fixed_count += 1


    if fixed_count > 0:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
