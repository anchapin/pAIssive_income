#!/usr/bin/env python3
"""
Logger initialization checker script.

Validates Python files for proper logger setup patterns.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


class LoggerChecker(ast.NodeVisitor):
    """AST visitor to check for proper logger initialization patterns."""

    def __init__(self, filename: str) -> None:
        """
        Initialize the logger checker.

        Args:
            filename: Path to the file being checked

        """
        self.filename = filename
        self.issues: list[tuple[str, int, str]] = []
        self.has_logging_import = False
        self.has_logger_init = False
        self.has_exception_handling = False
        self.has_logger_exception = False
        self.has_third_party_imports = False
        self.has_try_except_imports = False
        self.logger_init_line = None
        self.first_import_line = None
        self.last_import_line = None

    def visit_import(self, node: ast.Import) -> None:
        """Visit Import nodes to check for logging and third-party imports."""
        if self.first_import_line is None:
            self.first_import_line = node.lineno
        self.last_import_line = node.lineno

        for alias in node.names:
            if alias.name == "logging":
                self.has_logging_import = True
            elif (
                not alias.name.startswith(".")
                and "." not in alias.name
                and alias.name
                not in [
                    "os",
                    "sys",
                    "json",
                    "time",
                    "datetime",
                    "re",
                    "math",
                    "random",
                    "collections",
                    "itertools",
                    "functools",
                    "typing",
                ]
            ):
                # Check for third-party imports (simplified heuristic)
                self.has_third_party_imports = True
        self.generic_visit(node)

    def visit_import_from(self, node: ast.ImportFrom) -> None:
        """Visit ImportFrom nodes to check for logging and third-party imports."""
        if self.first_import_line is None:
            self.first_import_line = node.lineno
        self.last_import_line = node.lineno

        if node.module == "logging":
            self.has_logging_import = True
        elif (
            node.module
            and not node.module.startswith(".")
            and node.module.split(".")[0]
            not in [
                "os",
                "sys",
                "json",
                "time",
                "datetime",
                "re",
                "math",
                "random",
                "collections",
                "itertools",
                "functools",
                "typing",
            ]
        ):
            # Check for third-party imports
            self.has_third_party_imports = True
        self.generic_visit(node)

    def visit_assign(self, node: ast.Assign) -> None:
        """Check for logger initialization patterns."""
        # Check for logger initialization patterns
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "logging"
            and node.value.func.attr == "getLogger"
        ):
            self.has_logger_init = True
            self.logger_init_line = node.lineno
        self.generic_visit(node)

    def visit_try(self, node: ast.Try) -> None:
        """Check for exception handling patterns."""
        self.has_exception_handling = True

        # Check if this is around imports
        if (
            self.first_import_line
            and self.last_import_line
            and node.lineno <= self.last_import_line + 5
        ):
            self.has_try_except_imports = True

        # Check for logger.exception usage in except blocks
        for handler in node.handlers:
            for stmt in handler.body:
                if (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and stmt.value.func.attr == "exception"
                ):
                    self.has_logger_exception = True
        self.generic_visit(node)

    def check_issues(self) -> None:
        """Check for logger initialization issues."""
        # Check if logger is initialized too late
        if (
            self.has_logger_init
            and self.logger_init_line
            and self.last_import_line
            and self.logger_init_line > self.last_import_line + 3
        ):
            self.issues.append(
                (
                    "LOGGER_INIT_TOO_LATE",
                    self.logger_init_line,
                    "Logger should be initialized immediately after imports",
                )
            )

        # Check if logging is imported but no logger is initialized
        if self.has_logging_import and not self.has_logger_init:
            self.issues.append(
                (
                    "MISSING_LOGGER",
                    1,
                    "Logging module imported but no logger initialized",
                )
            )

        # Check if there's exception handling but no logger.exception usage
        if (
            self.has_exception_handling
            and self.has_logging_import
            and not self.has_logger_exception
        ):
            self.issues.append(
                (
                    "NO_LOGGER_EXCEPTION",
                    1,
                    "Module has exception handling but doesn't use logger.exception()",
                )
            )

        # Check if third-party imports should use try/except
        if self.has_third_party_imports and not self.has_try_except_imports:
            self.issues.append(
                (
                    "NO_TRY_EXCEPT_IMPORT",
                    1,
                    "Consider using try/except blocks around third-party imports",
                )
            )


def check_file(filepath: Path) -> list[tuple[str, int, str]]:
    """Check a single Python file for logger initialization issues."""
    try:
        with filepath.open(encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(filepath))
        checker = LoggerChecker(str(filepath))
        checker.visit(tree)
        checker.check_issues()
    except (SyntaxError, UnicodeDecodeError) as e:
        return [("PARSE_ERROR", 1, f"Failed to parse file: {e}")]
    else:
        return checker.issues


def main() -> None:
    """Check all Python files in the repository for logger initialization issues."""
    root_dir = Path()
    python_files = list(root_dir.rglob("*.py"))

    # Filter out common directories to ignore
    ignore_patterns = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        ".venv_new",
        "site-packages",
        "dist",
        "build",
        ".tox",
    }
    python_files = [
        f for f in python_files if not any(part in ignore_patterns for part in f.parts)
    ]

    total_issues = 0
    files_with_issues = 0

    for filepath in python_files:
        issues = check_file(filepath)
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            print(f"\n{filepath}:")
            for issue_type, line_no, message in issues:
                print(f"  Line {line_no}: {issue_type} - {message}")

    print(f"\nSummary: Found {total_issues} issues in {files_with_issues} files")

    # Exit with error code if issues found (for CI/CD)
    if total_issues > 0:
        sys.exit(1)
    else:
        print("All files passed logger initialization checks!")
        sys.exit(0)


if __name__ == "__main__":
    main()
