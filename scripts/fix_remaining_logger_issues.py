#!/usr/bin/env python3
"""
Script to fix remaining LOGGER_INIT_TOO_LATE issues.

This script specifically targets files where logger initialization happens too late
and moves it to immediately after imports.
"""

import logging
import os

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging
logger = logging.getLogger(__name__)


def find_imports_end(lines: list[str]) -> int:
    """Find the line number where imports end."""
    import_end = 0
    docstring_end = 0

    # Check for module docstring
    if lines and (lines[0].strip().startswith('"""') or lines[0].strip().startswith("'''")):
        quote_type = '"""' if '"""' in lines[0] else "'''"
        if lines[0].count(quote_type) >= 2:
            docstring_end = 0
        else:
            for i, line in enumerate(lines[1:], 1):
                if quote_type in line:
                    docstring_end = i
                    break

    # Find end of imports
    for i, line in enumerate(lines):
        if i <= docstring_end:
            continue
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            import_end = max(import_end, i)
        elif stripped and not stripped.startswith("#") and not stripped.startswith('"""') and not stripped.startswith("'''"):
            break

    return import_end


def find_logger_lines(lines: list[str]) -> list[int]:
    """Find all lines that initialize loggers."""
    logger_lines = []
    for i, line in enumerate(lines):
        if "logger = logging.getLogger(__name__)" in line:
            logger_lines.append(i)
    return logger_lines


def fix_logger_init_too_late(file_path: str) -> bool:
    """Fix LOGGER_INIT_TOO_LATE by moving logger initialization."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        import_end = find_imports_end(lines)
        logger_lines = find_logger_lines(lines)

        if not logger_lines:
            return False

        # Check if any logger is initialized too late
        needs_fix = any(line_idx > import_end + 3 for line_idx in logger_lines)

        if not needs_fix:
            return False

        # Remove all existing logger initializations
        for line_idx in reversed(logger_lines):
            # Also remove the comment line before it if it exists
            if line_idx > 0 and "# Configure logging" in lines[line_idx - 1]:
                lines.pop(line_idx - 1)
                line_idx -= 1
            lines.pop(line_idx)

        # Insert logger initialization right after imports
        insert_pos = import_end + 1

        # Add some spacing if needed
        if insert_pos < len(lines) and lines[insert_pos].strip():
            lines.insert(insert_pos, "")
            insert_pos += 1

        lines.insert(insert_pos, "")
        lines.insert(insert_pos + 1, "# Configure logging")
        lines.insert(insert_pos + 2, "logger = logging.getLogger(__name__)")
        lines.insert(insert_pos + 3, "")

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Fixed LOGGER_INIT_TOO_LATE in {file_path}")
        return True

    except Exception as e:
        logger.warning(f"Error fixing {file_path}: {e}")
        return False


def get_files_with_logger_issues() -> list[str]:
    """Get list of files that have LOGGER_INIT_TOO_LATE issues."""
    files_with_issues = [
        "add_logging_import.py",
        "install_crewai_for_tests.py",
        "run_ui.py",
        "common_utils/logging/centralized_logging.py",
        "common_utils/logging/logger.py",
        "common_utils/logging/log_utils.py",
        "common_utils/logging/secure_logging.py",
        "common_utils/logging/__init__.py",
        "scripts/run/run_github_actions_locally.py",
    ]

    # Filter to only existing files
    existing_files = []
    for file_path in files_with_issues:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            logger.warning(f"File not found: {file_path}")

    return existing_files


def main() -> None:
    """Main function to fix remaining logger issues."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    files_to_fix = get_files_with_logger_issues()
    fixed_count = 0

    for file_path in files_to_fix:
        logger.info(f"Processing {file_path}")
        if fix_logger_init_too_late(file_path):
            fixed_count += 1

    logger.info(f"Fixed {fixed_count} files with LOGGER_INIT_TOO_LATE issues")


if __name__ == "__main__":
    main()
