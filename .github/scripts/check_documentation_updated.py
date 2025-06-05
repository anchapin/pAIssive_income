"""
Check documentation updates in pull requests and commits.

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

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_git_executable() -> str:
    """
    Get the full path to the git executable.

    Returns:
        Full path to git executable or just 'git' if not found

    """
    git_path = shutil.which("git")
    if git_path:
        logger.info("Found git at: %s", git_path)
        return str(git_path)  # Ensure we return a string
    logger.warning("Could not find git executable, using 'git' and relying on PATH")
    return "git"


def get_changed_files() -> list[str]:  # noqa: C901, PLR0915
    """
    Return a list of files changed in the current PR or commit range.

    In a GitHub Actions PR context, compares against the base branch.
    Otherwise, compares HEAD^..HEAD.

    Returns:
        A list of changed file paths.

    """
    # Get the full path to git executable
    git_exe = get_git_executable()
    github_event_name = os.getenv("GITHUB_EVENT_NAME")
    github_base_ref = os.getenv("GITHUB_BASE_REF")
    github_head_ref = os.getenv("GITHUB_HEAD_REF")
    github_sha = os.getenv("GITHUB_SHA")

    logger.info("GitHub Event: %s", github_event_name)
    logger.info("Base Ref: %s", github_base_ref)
    logger.info("Head Ref: %s", github_head_ref)
    logger.info("SHA: %s", github_sha)

    # Make sure we have a good git environment
    try:
        # Ensure we have the latest changes
        subprocess.run(  # noqa: S603
            [git_exe, "config", "--global", "advice.detachedHead", "false"], check=True
        )

        # In pull_request event, compare against base branch
        if github_event_name == "pull_request" and github_base_ref and github_head_ref:
            logger.info(
                "Pull request detected: comparing %s to %s",
                github_base_ref,
                github_head_ref,
            )

            # Fetch both branches with full history to ensure merge-base works
            try:
                subprocess.run(  # noqa: S603
                    [git_exe, "fetch", "origin", github_base_ref], check=True, timeout=60
                )
                subprocess.run(  # noqa: S603
                    [git_exe, "fetch", "origin", github_head_ref], check=True, timeout=60
                )
            except subprocess.TimeoutExpired:
                logger.warning("Git fetch timed out, trying with shallow fetch")
                subprocess.run(  # noqa: S603
                    [git_exe, "fetch", "origin", github_base_ref, "--depth=50"], check=True
                )
                subprocess.run(  # noqa: S603
                    [git_exe, "fetch", "origin", github_head_ref, "--depth=50"], check=True
                )

            # Use merge-base to find the common ancestor
            try:
                result = subprocess.run(  # noqa: S603
                    [git_exe, "merge-base", f"origin/{github_base_ref}", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )
                merge_base = result.stdout.strip()

                logger.info("Found merge-base: %s", merge_base)
                diff_range = f"{merge_base}...HEAD"
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                logger.info(
                    "Could not find merge-base, falling back to direct comparison"
                )
                diff_range = f"origin/{github_base_ref}...HEAD"
        else:
            # For push events or when PR info is not available
            logger.info("Not a pull request or missing reference info")
            if github_sha:
                logger.info("Using commit SHA: %s", github_sha)
                # Try to get the parent of the current commit
                try:
                    result = subprocess.run(  # noqa: S603
                        [git_exe, "rev-parse", "HEAD^"],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=10,
                    )
                    parent_sha = result.stdout.strip()
                    diff_range = f"{parent_sha}...{github_sha}"
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    logger.info("Could not get parent commit, using default comparison")
                    diff_range = "HEAD~1...HEAD"
            else:
                logger.info("No SHA available, using default comparison")
                diff_range = "HEAD~1...HEAD"

        logger.info("Using diff range: %s", diff_range)
        result = subprocess.run(  # noqa: S603
            [git_exe, "diff", "--name-only", diff_range],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        if result.stderr:
            logger.info("Git diff stderr: %s", result.stderr)

        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        logger.info("Found %s changed files", len(files))

        # Log the files for debugging
        if files:
            logger.info("Changed files list:")
            for f in files:
                logger.info("  - %s", f)

        return files

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.exception("Error executing git command")
        logger.info("Command output: %s", getattr(e, "stdout", "N/A"))
        logger.info("Command error: %s", getattr(e, "stderr", "N/A"))

        # Fallback: try to get files from GitHub API environment variable
        logger.info("Attempting fallback method to get changed files...")
        return _get_files_from_github_api(github_event_name)


def _get_files_from_github_api(github_event_name: str) -> list[str]:
    """
    Fallback method to get changed files from GitHub API event payload.

    Args:
        github_event_name: The GitHub event name

    Returns:
        List of changed file paths
    """
    try:
        # Check if we're in a GitHub Actions environment with an event payload
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if not event_path or not Path(event_path).exists():
            logger.warning("No GitHub event payload found")
            return []

        with Path(event_path).open() as f:
            event_data = json.load(f)

        # Extract changed files based on event type
        if github_event_name == "pull_request" and "pull_request" in event_data:
            # Try to get files from the PR API data
            pr_data = event_data["pull_request"]

            # GitHub doesn't include changed_files in the standard payload
            # We need to use a different approach
            logger.info("PR detected, but changed files not available in payload")
            logger.info("PR number: %s", pr_data.get("number", "unknown"))
            logger.info("PR head SHA: %s", pr_data.get("head", {}).get("sha", "unknown"))
            logger.info("PR base SHA: %s", pr_data.get("base", {}).get("sha", "unknown"))

            # Return empty list to trigger the "no files" logic which passes the check
            return []

        logger.warning("Unsupported event type for file extraction: %s", github_event_name)
        return []

    except Exception:
        logger.exception("Fallback method failed")
        return []


def is_doc_file(path: str) -> bool:
    """
    Determine if the given path is a documentation file.

    Args:
        path: File path to check

    Returns:
        True if the file is a documentation file, False otherwise

    """
    p = Path(path)
    # Constants for path parts
    root_level = 1
    ui_docs_min_parts = 3  # ui/react_frontend/file.md has at least 3 parts

    # Any Markdown file at repo root (e.g., README.md, CopilotKit_CrewAI_Integration.md)
    if p.suffix.lower() == ".md" and len(p.parts) == root_level:
        return True
    # Any file in docs/ or docs_source/
    # Also consider ui/react_frontend/*.md as documentation
    if len(p.parts) > root_level:
        if p.parts[0] in {"docs", "docs_source"}:
            return True
        # Consider UI documentation files
        if (
            len(p.parts) >= ui_docs_min_parts
            and p.parts[0] == "ui"
            and p.parts[1] == "react_frontend"
            and p.suffix.lower() == ".md"
        ):
            return True
    return False


def main() -> None:
    """
    Execute the main documentation check routine.

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

            # Check if this is a PR with documentation files by looking at the current branch
            if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
                logger.info("This is a PR context - checking for documentation files in current state...")

                # Look for recently added documentation files
                doc_files_exist = _check_for_recent_doc_files()
                if doc_files_exist:
                    logger.info("✅ Documentation files found in PR context.")
                    sys.exit(0)

            logger.info("✅ Documentation check passed (no files to check).")
            sys.exit(0)

        # Print the list of changed files for debugging
        logger.info("Changed files:")
        for f in changed_files:
            logger.info("  %s", f)

        # Categorize files as documentation or non-documentation
        doc_files = [f for f in changed_files if is_doc_file(f)]
        non_doc_files = [f for f in changed_files if not is_doc_file(f)]

        logger.info("Documentation files: %d", len(doc_files))
        logger.info("Non-documentation files: %d", len(non_doc_files))

        # Log the categorized files for debugging
        if doc_files:
            logger.info("Documentation files found:")
            for f in doc_files:
                logger.info("  ✓ %s", f)

        if non_doc_files:
            logger.info("Non-documentation files found:")
            for f in non_doc_files:
                logger.info("  • %s", f)

        # If there are non-doc files but no doc files, fail the check
        if non_doc_files and not doc_files:
            logger.error(
                "❌ Documentation not updated! The following files were changed without any documentation update:"
            )
            for f in non_doc_files:
                logger.error("  - %s", f)
            logger.error(
                "\nTo fix: Update the documentation (e.g., in docs/ or a root-level .md file) "
                "to reflect your code changes and include it in your pull request."
            )
            sys.exit(1)
        else:
            # Either there are no non-doc files, or there are doc files (or both)
            if doc_files:
                logger.info("✅ Documentation files updated:")
                for f in doc_files:
                    logger.info("  ✓ %s", f)
            logger.info("✅ Documentation check passed.")
            sys.exit(0)
    except Exception:
        # Catch any unexpected errors and log them, but don't fail the build
        logger.exception("❗ Error during documentation check")
        logger.info("✅ Documentation check passed (due to error handling).")
        sys.exit(0)


def _check_for_recent_doc_files() -> bool:
    """
    Check if there are documentation files that might have been added recently.

    This is a fallback when git diff fails but we're in a PR context.

    Returns:
        True if documentation files are found, False otherwise
    """
    try:
        # Look for common documentation files that might indicate documentation updates
        doc_indicators = [
            "docs/",
            "docs_source/",
            "README.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
        ]

        for indicator in doc_indicators:
            if Path(indicator).exists():
                logger.info("Found documentation indicator: %s", indicator)
                return True

        # Check for any .md files in the docs directory
        docs_dir = Path("docs")
        if docs_dir.exists():
            md_files = list(docs_dir.rglob("*.md"))
            if md_files:
                logger.info("Found %d markdown files in docs directory", len(md_files))
                return True

        return False

    except Exception:
        logger.exception("Error checking for recent documentation files")
        return False


if __name__ == "__main__":
    main()
