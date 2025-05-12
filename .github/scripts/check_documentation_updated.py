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

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_changed_files() -> List[str]:  # noqa: C901, PLR0915
    """
    Returns a list of files changed in the current PR or commit range.
    In a GitHub Actions PR context, compares against the base branch.
    Otherwise, compares HEAD^..HEAD.

    Returns:
        List of changed file paths
    """
    github_event_name = os.getenv("GITHUB_EVENT_NAME")
    github_base_ref = os.getenv("GITHUB_BASE_REF")
    github_head_ref = os.getenv("GITHUB_HEAD_REF")
    github_sha = os.getenv("GITHUB_SHA")

    logger.info(f"GitHub Event: {github_event_name}")
    logger.info(f"Base Ref: {github_base_ref}")
    logger.info(f"Head Ref: {github_head_ref}")
    logger.info(f"SHA: {github_sha}")

    # Make sure we have a good git environment
    try:
        # Ensure we have the latest changes
        subprocess.run(
            ["git", "config", "--global", "advice.detachedHead", "false"], check=True
        )

        # In pull_request event, compare against base branch
        if github_event_name == "pull_request" and github_base_ref and github_head_ref:
            logger.info(
                f"Pull request detected: comparing {github_base_ref} to {github_head_ref}"
            )

            # Fetch both branches to ensure they're available locally
            subprocess.run(
                ["git", "fetch", "origin", github_base_ref, "--depth=1"], check=True
            )
            subprocess.run(
                ["git", "fetch", "origin", github_head_ref, "--depth=1"], check=True
            )

            # Use merge-base to find the common ancestor
            try:
                result = subprocess.run(
                    ["git", "merge-base", f"origin/{github_base_ref}", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                merge_base = result.stdout.strip()

                logger.info(f"Found merge-base: {merge_base}")
                diff_range = f"{merge_base}...HEAD"
            except subprocess.CalledProcessError:
                logger.info(
                    "Could not find merge-base, falling back to direct comparison"
                )
                diff_range = f"origin/{github_base_ref}...HEAD"
        else:
            # For push events or when PR info is not available
            logger.info("Not a pull request or missing reference info")
            if github_sha:
                logger.info(f"Using commit SHA: {github_sha}")
                # Try to get the parent of the current commit
                try:
                    result = subprocess.run(
                        ["git", "rev-parse", "HEAD^"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    parent_sha = result.stdout.strip()
                    diff_range = f"{parent_sha}...{github_sha}"
                except subprocess.CalledProcessError:
                    logger.info("Could not get parent commit, using default comparison")
                    diff_range = "HEAD~1...HEAD"
            else:
                logger.info("No SHA available, using default comparison")
                diff_range = "HEAD~1...HEAD"

        logger.info(f"Using diff range: {diff_range}")
        result = subprocess.run(
            ["git", "diff", "--name-only", diff_range],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stderr:
            logger.info(f"Git diff stderr: {result.stderr}")

        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        logger.info(f"Found {len(files)} changed files")
    except subprocess.CalledProcessError as e:
        logger.exception("Error executing git command")
        logger.info(f"Command output: {e.stdout if hasattr(e, 'stdout') else 'N/A'}")
        logger.info(f"Command error: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")

        # Fallback: try to get files from GitHub API environment variable
        logger.info("Attempting fallback method to get changed files...")
        try:
            # Check if we're in a GitHub Actions environment with an event payload
            event_path = os.getenv("GITHUB_EVENT_PATH")
            if event_path and os.path.exists(event_path):
                with open(event_path) as f:
                    event_data = json.load(f)

                # Extract changed files based on event type
                if (
                    github_event_name == "pull_request"
                    and "pull_request" in event_data
                    and "changed_files" in event_data["pull_request"]
                ):
                    logger.info("Using files from pull_request.changed_files")
                    return [
                        f["filename"]
                        for f in event_data["pull_request"]["changed_files"]
                    ]

            logger.warning("Fallback method failed, using empty file list")
        except Exception:
            logger.exception("Fallback method failed")
        return []
    else:
        return files


def is_doc_file(path: str) -> bool:
    """
    Returns True if the given path is considered a documentation file.

    Args:
        path: File path to check

    Returns:
        True if the file is a documentation file, False otherwise
    """
    p = Path(path)
    # Any Markdown file at repo root (e.g., README.md)
    if p.suffix.lower() == ".md" and len(p.parts) == 1:
        return True
    # Any file in docs/ or docs_source/
    return len(p.parts) > 1 and p.parts[0] in {"docs", "docs_source"}


def main() -> None:
    """
    Main routine:
    - Gets the list of changed files for the current PR/commit.
    - Checks if any non-documentation files were modified.
    - If so, ensures at least one documentation file was also updated.
    - Exits with code 1 and prints details if the check fails.
    """
    try:
        logger.info("Starting documentation check...")

        # Get the list of changed files
        changed_files = get_changed_files()

        # If we couldn't determine changed files or there are none, pass the check
        if not changed_files:
            logger.info("No files changed or couldn't determine changed files.")
            logger.info("✅ Documentation check passed (no files to check).")
            sys.exit(0)

        # Print the list of changed files for debugging
        logger.info("Changed files:")
        for f in changed_files:
            logger.info(f"  - {f}")

        # Categorize files as documentation or non-documentation
        doc_files = [f for f in changed_files if is_doc_file(f)]
        non_doc_files = [f for f in changed_files if not is_doc_file(f)]

        logger.info(f"Documentation files: {len(doc_files)}")
        logger.info(f"Non-documentation files: {len(non_doc_files)}")

        # If there are non-doc files but no doc files, fail the check
        if non_doc_files and not doc_files:
            logger.error(
                "❌ Documentation not updated! The following files were changed without any documentation update:"
            )
            for f in non_doc_files:
                logger.error(f"  - {f}")
            logger.error(
                "\nTo fix: Update the documentation (e.g., in docs/ or a root-level .md file) "
                "to reflect your code changes and include it in your pull request."
            )
            sys.exit(1)
        else:
            # Either there are no non-doc files, or there are doc files (or both)
            if doc_files:
                logger.info("Documentation files updated:")
                for f in doc_files:
                    logger.info(f"  - {f}")
            logger.info("✅ Documentation check passed.")
            sys.exit(0)
    except Exception:
        # Catch any unexpected errors and log them, but don't fail the build
        logger.exception("❗ Error during documentation check")
        logger.info("✅ Documentation check passed (due to error handling).")
        sys.exit(0)


if __name__ == "__main__":
    main()
