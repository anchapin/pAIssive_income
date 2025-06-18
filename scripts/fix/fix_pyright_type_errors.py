#!/usr/bin/env python3
"""
Fix Pyright type errors.

This script automatically adds type annotations and fixes common type issues.
"""

import argparse
import ast
import logging
import os
import re
import sys
from typing import List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Type annotation templates
TYPE_ANNOTATIONS = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "list": "list",
    "dict": "dict",
    "tuple": "tuple",
    "set": "set",
    "bytes": "bytes",
    "None": "None",
    "Any": "Any",
    "Optional": "Optional",
    "Union": "Union",
    "List": "List",
    "Dict": "Dict",
    "Tuple": "Tuple",
    "Set": "Set",
}

# Common type patterns to match in error messages
TYPE_PATTERNS = {
    r"cannot be assigned to parameter .* of type '(.*)' in function": r"\1",
    r"Type '(.*)' cannot be assigned to type '(.*)'": r"\2",
    r"Cannot assign to '.*' because '.*' is a '(.*)'": r"\1",
    r"Cannot access member '.*' for type '(.*)'": r"\1",
    r"'(.*)' is incompatible with return type '(.*)'": r"\2",
    r"Parameter '.*' requires annotation": "Any",
    r"Function '.*' is missing a return type annotation": "None",
    r"Function is missing a return type annotation": "None",
}

# Path to common Python imports to add
COMMON_IMPORTS = {
    "List": "from typing import List",
    "Dict": "from typing import Dict",
    "Tuple": "from typing import Tuple",
    "Set": "from typing import Set",
    "Optional": "from typing import Optional",
    "Union": "from typing import Union",
    "Any": "from typing import Any",
    "cast": "from typing import cast",
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fix Pyright type errors")

    parser.add_argument(
        "--file", "-f", type=str, help="Path to a specific Python file to fix"
    )

    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=".",
        help="Directory to scan for Python files (default: current directory)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--check",
        "-c",
        action="store_true",
        help="Check mode - don't modify files, just report issues",
    )

    return parser.parse_args()


def extract_type_from_error(error_message: str) -> Optional[str]:
    """Extract a type annotation from a Pyright error message."""
    for pattern, replacement in TYPE_PATTERNS.items():
        match = re.search(pattern, error_message)
        if match:
            extracted_type = replacement
            # If the replacement has a capture group reference
            if r"\1" in replacement:
                extracted_type = match.group(1)
            elif r"\2" in replacement:
                extracted_type = match.group(2)

            # Clean up the extracted type
            return extracted_type.strip("'")

    return None


def add_missing_imports(file_content: str, needed_imports: Set[str]) -> str:
    """Add necessary import statements to the file."""
    if not needed_imports:
        return file_content

    import_statements = []
    for import_type in needed_imports:
        if import_type in COMMON_IMPORTS:
            import_statements.append(COMMON_IMPORTS[import_type])

    # If no imports to add
    if not import_statements:
        return file_content

    # De-duplicate imports
    import_statements = sorted(set(import_statements))
    import_block = "\n".join(import_statements)

    # Try to find a good location to insert imports (after existing imports)
    lines = file_content.split("\n")
    last_import_index = -1

    # Track import sections
    in_import_section = False
    import_section_end = 0

    for i, line in enumerate(lines):
        if line.startswith(("import ", "from ")):
            in_import_section = True
            last_import_index = i
        elif in_import_section and line.strip() and not line.startswith("#"):
            in_import_section = False
            import_section_end = i
            break

    # If we found a position after imports
    if import_section_end > 0:
        lines.insert(import_section_end, import_block)
    # If we found imports but no clear end
    elif last_import_index >= 0:
        lines.insert(last_import_index + 1, import_block)
    # No imports found, insert after docstring if present
    else:
        for i, line in enumerate(lines):
            if i > 3 and line.strip() and not line.startswith("#"):
                lines.insert(i, import_block)
                break
        else:
            # Last resort: insert at the beginning
            lines.insert(0, import_block)

    return "\n".join(lines)


def add_type_annotations(
    file_path: str,
    check_only: bool = False,
) -> Tuple[int, int]:
    """
    Add missing type annotations to the file.

    Args:
        file_path: Path to the Python file
        check_only: Whether to check without modifying

    Returns:
        Tuple of (fixed_errors, total_errors)

    """
    try:
        # Read the file content
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse the file with ast
        tree = ast.parse(content)

        # Collect all functions without return type annotations
        functions_missing_annotations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.returns:
                functions_missing_annotations.append(node)

        if not functions_missing_annotations:
            return 0, 0

        # Add type annotations
        needed_imports = set()

        # TODO: Implement function to add type annotations

        # Add necessary imports
        updated_content = add_missing_imports(content, needed_imports)

        if check_only:
            return 0, len(functions_missing_annotations)

        # Write the modified content back to file
        if updated_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return len(functions_missing_annotations), len(
                functions_missing_annotations
            )

        return 0, len(functions_missing_annotations)

    except Exception as e:
        logger.exception(f"Error processing {file_path}: {e}")
        return 0, 0


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in a directory recursively."""
    python_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def main() -> int:
    """Run the main function."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    fixed_count = 0
    error_count = 0

    if args.file:
        if not os.path.exists(args.file):
            logger.error(f"File does not exist: {args.file}")
            return 1

        if not args.file.endswith(".py"):
            logger.error("Not a Python file")
            return 1

        fixed, errors = add_type_annotations(args.file, args.check)
        fixed_count += fixed
        error_count += errors

        logger.info(f"Fixed {fixed}/{errors} type issues in {args.file}")
    else:
        if not os.path.exists(args.directory):
            logger.error(f"Directory does not exist: {args.directory}")
            return 1

        python_files = find_python_files(args.directory)
        logger.info(f"Found {len(python_files)} Python files to check")

        for file_path in python_files:
            fixed, errors = add_type_annotations(file_path, args.check)
            fixed_count += fixed
            error_count += errors

            if fixed > 0:
                logger.info(f"Fixed {fixed}/{errors} type issues in {file_path}")

    if args.check:
        logger.info(
            f"Found {error_count} type issues in total (check mode, no fixes applied)"
        )
    else:
        logger.info(f"Fixed {fixed_count}/{error_count} type issues in total")

    return 0


if __name__ == "__main__":
    sys.exit(main())
