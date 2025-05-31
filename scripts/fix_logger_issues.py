#!/usr/bin/env python3


"""
Script to fix common logger initialization issues.

This script addresses the most common logger issues found by check_logger_initialization.py:
1. LOGGER_INIT_TOO_LATE - Move logger initialization immediately after imports
2. Duplicate logger initializations
3. Missing logger initialization when logging is imported
"""

import logging
import os
import re

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging
logger = logging.getLogger(__name__)


def fix_logger_init_too_late(file_path: str) -> bool:
    """Fix LOGGER_INIT_TOO_LATE issues by moving logger initialization."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")

        # Find import section end
        import_end = 0
        docstring_end = 0

        # Check for module docstring
        if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
            in_docstring = True
            quote_type = '"""' if lines[0].startswith('"""') else "'''"
            if lines[0].count(quote_type) >= 2:
                docstring_end = 0
                in_docstring = False
            else:
                for i, line in enumerate(lines[1:], 1):
                    if quote_type in line:
                        docstring_end = i
                        in_docstring = False
                        break

        # Find end of imports
        for i, line in enumerate(lines):
            if i <= docstring_end:
                continue
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                import_end = max(import_end, i)
            elif stripped and not stripped.startswith("#"):
                break

        # Find existing logger initializations
        logger_lines = []
        for i, line in enumerate(lines):
                logger_lines.append(i)

        if not logger_lines:
            return False

        # Remove duplicate logger initializations
        if len(logger_lines) > 1:
            # Keep the first one, remove others
            for line_idx in reversed(logger_lines[1:]):
                lines.pop(line_idx)

        # Move logger initialization to right after imports
        logger_line_idx = logger_lines[0] if logger_lines else -1
        if logger_line_idx > import_end + 2:  # Allow some spacing
            # Remove current logger line
            logger_line = lines.pop(logger_line_idx)

            # Insert after imports
            insert_pos = import_end + 1

            # Add some spacing if needed
            if insert_pos < len(lines) and lines[insert_pos].strip():
                lines.insert(insert_pos, "")
                insert_pos += 1

            lines.insert(insert_pos, "")
            lines.insert(insert_pos + 1, "# Configure logging")
            lines.insert(insert_pos + 2, logger_line)
            lines.insert(insert_pos + 3, "")

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            return True

        return False

    except Exception as e:
        logger.warning(f"Error fixing {file_path}: {e}")
        return False


def fix_missing_logger(file_path: str) -> bool:
    """Fix MISSING_LOGGER issues by adding logger initialization."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if logging is imported but no logger initialized
        if "import logging" not in content:
            return False

            return False

        lines = content.split("\n")

        # Find end of imports
        import_end = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                import_end = max(import_end, i)

        # Insert logger initialization
        insert_pos = import_end + 1

        # Add spacing if needed
        if insert_pos < len(lines) and lines[insert_pos].strip():
            lines.insert(insert_pos, "")
            insert_pos += 1

        lines.insert(insert_pos, "")
        lines.insert(insert_pos + 1, "# Configure logging")
        lines.insert(insert_pos + 3, "")

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return True

    except Exception as e:
        logger.warning(f"Error fixing {file_path}: {e}")
        return False


def get_python_files(directory: str, exclude_patterns: list[str] = None) -> list[str]:
    """Get all Python files in directory, excluding test files and common exclusions."""
    if exclude_patterns is None:
        exclude_patterns = [
            r".*test.*\.py$",
            r".*_test\.py$",
            r"test_.*\.py$",
            r".*conftest\.py$",
            r".*__pycache__.*",
            r".*\.git.*",
            r".*venv.*",
            r".*env.*",
        ]

    python_files = []

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(re.match(pattern, d) for pattern in exclude_patterns)]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # Skip excluded files
                if any(re.match(pattern, file_path) for pattern in exclude_patterns):
                    continue

                python_files.append(file_path)

    return python_files


def main():
    """Main function to fix logger issues."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Get all Python files
    python_files = get_python_files(".")

    fixed_files = []

    for file_path in python_files:
        logger.info(f"Processing {file_path}")

        fixed = False

        # Try to fix LOGGER_INIT_TOO_LATE
        if fix_logger_init_too_late(file_path):
            logger.info(f"Fixed LOGGER_INIT_TOO_LATE in {file_path}")
            fixed = True

        # Try to fix MISSING_LOGGER
        if fix_missing_logger(file_path):
            logger.info(f"Fixed MISSING_LOGGER in {file_path}")
            fixed = True

        if fixed:
            fixed_files.append(file_path)

    logger.info(f"Fixed {len(fixed_files)} files:")
    for file_path in fixed_files:
        logger.info(f"  - {file_path}")


if __name__ == "__main__":
    main()
