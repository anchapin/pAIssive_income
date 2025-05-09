"""
check_documentation_updated.py

This script is designed to be used as part of a GitHub Actions workflow.
It ensures that whenever code or non-documentation files are changed in a pull request or push,
at least one documentation file is also updated. If not, the script exits with a nonzero status,
causing the workflow to fail.

Documentation files are defined as:
- Any Markdown (*.md) file at the repository root
- Any file (of any type) within the 'docs/' or 'docs_source/' directories

Usage (inside a GitHub Action):
    python .github/scripts/check_documentation_updated.py

Exit codes:
    0 - Success (documentation updated, or only documentation files were changed)
    1 - Failure (non-documentation files changed without documentation update)
"""

import os
import subprocess
import sys
from pathlib import Path

def get_changed_files():
    """
    Returns a list of files changed in the current PR or commit range.
    In a GitHub Actions PR context, compares against the base branch.
    Otherwise, compares HEAD^..HEAD.
    """
    github_event_name = os.getenv("GITHUB_EVENT_NAME")
    github_base_ref = os.getenv("GITHUB_BASE_REF")
    github_head_ref = os.getenv("GITHUB_HEAD_REF")

    # In pull_request event, compare against base branch
    if github_event_name == "pull_request" and github_base_ref and github_head_ref:
        # Fetch base branch to ensure it's available locally
        subprocess.run(["git", "fetch", "origin", github_base_ref], check=True)
        diff_range = f"origin/{github_base_ref}...HEAD"
    else:
        # Fallback: compare last commit to current (may not catch all changes in large pushes)
        diff_range = "HEAD^..HEAD"

    result = subprocess.run(
        ["git", "diff", "--name-only", diff_range],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return files

def is_doc_file(path):
    """
    Returns True if the given path is considered a documentation file.
    - Any Markdown file (*.md) at the repository root
    - Any file under 'docs/' or 'docs_source/' directories
    """
    p = Path(path)
    # Any Markdown file at repo root (e.g., README.md)
    if p.suffix.lower() == ".md" and len(p.parts) == 1:
        return True
    # Any file in docs/ or docs_source/
    if len(p.parts) > 1 and p.parts[0] in {"docs", "docs_source"}:
        return True
    return False

def main():
    """
    Main routine:
    - Gets the list of changed files for the current PR/commit.
    - Checks if any non-documentation files were modified.
    - If so, ensures at least one documentation file was also updated.
    - Exits with code 1 and prints details if the check fails.
    """
    changed_files = get_changed_files()
    if not changed_files:
        print("No files changed.")
        sys.exit(0)

    doc_files = [f for f in changed_files if is_doc_file(f)]
    non_doc_files = [f for f in changed_files if not is_doc_file(f)]

    if non_doc_files and not doc_files:
        print("❌ Documentation not updated! The following files were changed without any documentation update:")
        for f in non_doc_files:
            print(f"  - {f}")
        print(
            "\nTo fix: Update the documentation (e.g., in docs/ or a root-level .md file) "
            "to reflect your code changes and include it in your pull request."
        )
        sys.exit(1)
    else:
        print("✅ Documentation check passed.")

if __name__ == "__main__":
    main()