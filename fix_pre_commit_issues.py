"""fix_pre_commit_issues - Module for fixing pre-commit hook issues.

This module provides functionality to fix common pre-commit hook issues in files,
such as trailing whitespace and missing newlines at the end of files.
"""

# Standard library imports
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_files_to_fix(file_paths: Optional[List[str]] = None) -> List[Path]:
    """Get the list of files to fix.

    Args:
        file_paths: Optional list of file paths to fix. If not provided,
            uses a default list of files.

    Returns:
        List of Path objects for files to fix.
    """
    if file_paths:
        return [Path(file_path) for file_path in file_paths]

    # Default list of files to fix
    default_files = [
        "docs/getting-started.md",
        "docs/faq.md",
        "docs/README.md",
        "dev_tools/build_docs.sh",
        "dev_tools/quick_lint.sh",
        "dev_tools/type_check.sh",
        "dev_tools/deps_audit.sh",
        "docs/documentation-guide.md",
        "dev_tools/security_audit.sh",
        "dev_tools/__init__.py",
        "dev_tools/health_check.py",
    ]
    return [Path(file_path) for file_path in default_files]


def fix_file(file_path: Path, verbose: bool = False) -> bool:
    """Fix common pre-commit issues in a file.

    Args:
        file_path: Path to the file to fix.
        verbose: Whether to print verbose output.

    Returns:
        True if the file was fixed successfully, False otherwise.
    """
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return False

    try:
        # Read the file content
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Fix trailing whitespace
        original_content = content
        content = "\n".join(line.rstrip() for line in content.splitlines())

        # Ensure file ends with a newline
        if content and not content.endswith("\n"):
            content += "\n"

        # Write the content back if it changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            if verbose:
                logger.info(f"Fixed: {file_path}")
            return True
        else:
            if verbose:
                logger.info(f"No issues found in: {file_path}")
            return True
    except Exception:
        # Use logging.exception to automatically include the traceback
        logger.exception(f"Error fixing {file_path}")
        return False


def main() -> int:
    """Main entry point for the script.

    Returns:
        0 if successful, 1 otherwise.
    """
    parser = argparse.ArgumentParser(
        description="Fix common pre-commit hook issues in files."
    )
    parser.add_argument("files", nargs="*", help="Specific files to fix (optional)")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    # Get the list of files to fix
    files_to_fix = get_files_to_fix(args.files)
    if not files_to_fix:
        logger.warning("No files to fix.")
        return 0

    # Fix each file
    success = True
    fixed_count = 0
    for file_path in files_to_fix:
        if fix_file(file_path, args.verbose):
            fixed_count += 1
        else:
            success = False

    # Print summary
    logger.info(f"Fixed {fixed_count} out of {len(files_to_fix)} files.")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
