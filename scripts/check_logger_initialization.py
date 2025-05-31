#!/usr/bin/env python
"""
Script to check for proper logger initialization in Python files.

This script scans Python files in the specified directories and checks for common
logger initialization issues, such as:
- Using logging before initializing a logger
- Not initializing a logger at the top of the module
- Using the root logger directly instead of a module-specific logger

The script automatically excludes:
- All directories starting with '.' (e.g., .git, .venv, .pytest_cache)
- Common build and cache directories (node_modules, __pycache__, build, dist, etc.)
- Test files (files matching *_test.py or test_*.py patterns)

Usage:
    python scripts/check_logger_initialization.py [--fix] [--verbose] [path1 path2 ...]

Arguments:
    --fix       Attempt to fix issues automatically
    --verbose   Show detailed output
    path1, path2, ... Paths to scan (default: current directory)

"""

import argparse
import ast
import logging
import os
import re
import sys

# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging


# Configure logging
logger = logging.getLogger(__name__)
# logging.basicConfig will be moved to the main() function

# Default directories to exclude
# Note: All directories starting with '.' are automatically excluded in scan_directory()
DEFAULT_EXCLUDE_DIRS = {
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
    "site-packages",
    "htmlcov",
    "coverage",
    "playwright-report",
    "ci-reports",
    "security-reports",
}

# Default files to exclude
DEFAULT_EXCLUDE_FILES = {
    "setup.py",
    "conftest.py",
}

# Default file patterns to exclude
DEFAULT_EXCLUDE_PATTERNS = [
    r".*_test\.py$",
    r"test_.*\.py$",
]


class LoggerIssue:
    """Class representing a logger initialization issue."""

    def __init__(
        self,
        file_path: str,
        issue_type: str,
        line_number: int,
        message: str,
        fixable: bool = False,
    ):
        """
        Initialize a logger issue.

        Args:
            file_path: Path to the file with the issue
            issue_type: Type of issue (e.g., "MISSING_LOGGER", "ROOT_LOGGER")
            line_number: Line number where the issue was found
            message: Description of the issue
            fixable: Whether the issue can be fixed automatically

        """
        self.file_path = file_path
        self.issue_type = issue_type
        self.line_number = line_number
        self.message = message
        self.fixable = fixable

    def __str__(self) -> str:
        """Return a string representation of the issue."""
        return f"{self.file_path}:{self.line_number}: {self.issue_type}: {self.message}"


class LoggerChecker(ast.NodeVisitor):
    """AST visitor to check for logger initialization issues."""

    def __init__(self, file_path: str):
        """
        Initialize the logger checker.

        Args:
            file_path: Path to the file being checked

        """
        self.file_path = file_path
        self.issues: list[LoggerIssue] = []
        self.logger_initialized = False
        self.logger_name = None
        self.logging_imported = False
        self.logging_used_before_init = False
        self.root_logger_used = False
        self.imports_end_line = 0
        self.docstring_end_line = 0
        self.first_logging_use_line = 0
        self.logging_basicConfig_used = False
        self.string_concat_in_logging = False
        self.string_concat_line = 0
        self.has_try_except_import = False

    def visit_Import(self, node: ast.Import) -> None:
        """
        Visit an import node.

        Args:
            node: The AST node being visited

        """
        for name in node.names:
            if name.name == "logging":
                self.logging_imported = True
                self.imports_end_line = max(self.imports_end_line, node.end_lineno or 0)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visit an import from node.

        Args:
            node: The AST node being visited

        """
        if node.module == "logging":
            self.logging_imported = True
        self.imports_end_line = max(self.imports_end_line, node.end_lineno or 0)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        Visit an assignment node.

        Args:
            node: The AST node being visited

        """
        # Check for logger initialization
        if isinstance(node.value, ast.Call):
            if (
                isinstance(node.value.func, ast.Attribute)
                and isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == "logging"
                and node.value.func.attr == "getLogger"
            ):
                self.logger_initialized = True
                self.logger_name = (
                    node.targets[0].id
                    if isinstance(node.targets[0], ast.Name)
                    else None
                )

                # Check if logger is initialized after it's used
                if self.logging_used_before_init:
                    self.issues.append(
                        LoggerIssue(
                            self.file_path,
                            "LATE_LOGGER_INIT",
                            node.lineno,
                            f"Logger initialized after it's used (first use at line {self.first_logging_use_line})",
                            fixable=True,
                        )
                    )

                # Check if logger is initialized too late in the file
                if node.lineno > self.imports_end_line + 5:
                    self.issues.append(
                        LoggerIssue(
                            self.file_path,
                            "LOGGER_INIT_TOO_LATE",
                            node.lineno,
                            "Logger should be initialized immediately after imports",
                            fixable=True,
                        )
                    )
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """
        Visit an expression node.

        Args:
            node: The AST node being visited

        """
        # Check for module docstring
        if (
            isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and node.lineno <= 3
        ):
            self.docstring_end_line = node.end_lineno or 0
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """
        Visit a function call node.

        Args:
            node: The AST node being visited

        """
        # Check for direct use of logging module
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logging"
            and node.func.attr
            in ["debug", "info", "warning", "error", "critical", "exception"]
        ):
            self.root_logger_used = True
            if not self.first_logging_use_line:
                self.first_logging_use_line = node.lineno

            if not self.logger_initialized:
                self.logging_used_before_init = True

            self.issues.append(
                LoggerIssue(
                    self.file_path,
                    "ROOT_LOGGER_USED",
                    node.lineno,
                    f"Using root logger directly: logging.{node.func.attr}()",
                    fixable=True,
                )
            )

            # Check for string concatenation in logging calls
            if (
                node.args
                and isinstance(node.args[0], ast.BinOp)
                and isinstance(node.args[0].op, ast.Add)
            ):
                self.string_concat_in_logging = True
                self.string_concat_line = node.lineno
                self.issues.append(
                    LoggerIssue(
                        self.file_path,
                        "STRING_CONCAT_IN_LOGGING",
                        node.lineno,
                        "Using string concatenation in logging call instead of formatting",
                        fixable=True,
                    )
                )

        # Check for logging.basicConfig usage
        elif (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logging"
            and node.func.attr == "basicConfig"
        ):
            self.logging_basicConfig_used = True

            # 'node' is ast.Call. Its parent should be ast.Expr. Parent of ast.Expr is the scope-defining node.
            parent_expr = getattr(
                node, "parent", None
            )  # Parent of Call node (should be ast.Expr)
            scope_defining_node = (
                getattr(parent_expr, "parent", None) if parent_expr else None
            )  # Parent of Expr node

            is_in_function = isinstance(
                scope_defining_node, (ast.FunctionDef, ast.AsyncFunctionDef)
            )
            is_in_main_guard = False

            if isinstance(scope_defining_node, ast.If):
                # Check if this 'If' node is 'if __name__ == "__main__":'
                # and this 'If' node itself is at the module level (its parent is ast.Module).
                if_node_is_top_level = isinstance(
                    getattr(scope_defining_node, "parent", None), ast.Module
                )

                if if_node_is_top_level:
                    test_expr = scope_defining_node.test
                    if (
                        isinstance(test_expr, ast.Compare)
                        and isinstance(test_expr.left, ast.Name)
                        and test_expr.left.id == "__name__"
                        and isinstance(test_expr.ops[0], ast.Eq)
                        and len(test_expr.comparators) == 1
                        and isinstance(test_expr.comparators[0], ast.Constant)
                        and test_expr.comparators[0].value == "__main__"
                    ):
                        # Check if the parent_expr (which contains basicConfig call) is directly in the body of this If node
                        if parent_expr in scope_defining_node.body:
                            is_in_main_guard = True

            # If not in a function and not in a recognized main guard, then it's considered global/problematic.
            if not is_in_function and not is_in_main_guard:
                self.issues.append(
                    LoggerIssue(
                        self.file_path,
                        "GLOBAL_BASICCONFIG",
                        node.lineno,
                        "logging.basicConfig should be used in a main guard or function, not in global scope",
                        fixable=False,
                    )
                )

        # Check for string concatenation in logger calls
        elif (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logger"
            and node.func.attr
            in ["debug", "info", "warning", "error", "critical", "exception"]
            and node.args
            and isinstance(node.args[0], ast.BinOp)
            and isinstance(node.args[0].op, ast.Add)
        ):
            self.string_concat_in_logging = True
            self.string_concat_line = node.lineno
            self.issues.append(
                LoggerIssue(
                    self.file_path,
                    "STRING_CONCAT_IN_LOGGING",
                    node.lineno,
                    "Using string concatenation in logging call instead of formatting",
                    fixable=True,
                )
            )

        self.generic_visit(node)

    def get_parents(self, node: ast.AST) -> list[ast.AST]:
        """
        Get the parent nodes of a node.

        Args:
            node: The AST node to get parents for

        Returns:
            List of parent nodes

        """
        parents = []
        with open(self.file_path, encoding="utf-8") as f:
            file_content = f.read()
            for parent in ast.walk(ast.parse(file_content)):
                for child in ast.iter_child_nodes(parent):
                    if child == node:
                        parents.append(parent)
        return parents

    def visit_Try(self, node: ast.Try) -> None:
        """
        Visit a try/except node.

        Args:
            node: The AST node being visited

        """
        # Check for try/except blocks around imports
        for stmt in node.body:
            if isinstance(stmt, ast.Import) or isinstance(stmt, ast.ImportFrom):
                self.has_try_except_import = True
                break

        self.generic_visit(node)

    def check(self) -> list[LoggerIssue]:
        """
        Check for logger initialization issues.

        Returns:
            List of logger issues found

        """
        if self.logging_imported and not self.logger_initialized:
            self.issues.append(
                LoggerIssue(
                    self.file_path,
                    "MISSING_LOGGER",
                    self.imports_end_line,
                    "Logging module imported but no logger initialized",
                    fixable=True,
                )
            )

        # Check if the module has imports but no try/except blocks around them
        if self.logging_imported and not self.has_try_except_import:
            # Only suggest try/except for third-party imports
            with open(self.file_path, encoding="utf-8") as f:
                content = f.read()
                if "import " in content and not content.count(
                    "import"
                ) == content.count("import logging"):
                    self.issues.append(
                        LoggerIssue(
                            self.file_path,
                            "NO_TRY_EXCEPT_IMPORT",
                            self.imports_end_line,
                            "Consider using try/except blocks around third-party imports",
                            fixable=False,
                        )
                    )

        # Check if the module has a logger but doesn't use it for exception handling
        if self.logger_initialized:
            with open(self.file_path, encoding="utf-8") as f:
                content = f.read()
                if "except " in content and "logger.exception" not in content:
                    self.issues.append(
                        LoggerIssue(
                            self.file_path,
                            "NO_LOGGER_EXCEPTION",
                            0,
                            "Module has exception handling but doesn't use logger.exception()",
                            fixable=False,
                        )
                    )

        return self.issues


def check_file(file_path: str) -> list[LoggerIssue]:
    """
    Check a file for logger initialization issues.

    Args:
        file_path: Path to the file to check

    Returns:
        List of logger issues found

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

            tree = ast.parse(content, filename=file_path)

            # Add parent pointers to all nodes in the AST
            for node_obj in ast.walk(tree):
                for child_node in ast.iter_child_nodes(node_obj):
                    child_node.parent = node_obj  # type: ignore[attr-defined]

            checker = LoggerChecker(file_path)
            checker.visit(tree)
        return checker.check()
    except SyntaxError as e:
        logger.warning(f"Syntax error in {file_path}: {e}")
        return [
            LoggerIssue(
                file_path,
                "SYNTAX_ERROR",
                e.lineno or 0,
                f"Syntax error: {e}",
                fixable=False,
            )
        ]
    except Exception as e:
        logger.warning(f"Error checking {file_path}: {e}")
        return [
            LoggerIssue(
                file_path, "CHECK_ERROR", 0, f"Error checking file: {e}", fixable=False
            )
        ]


def fix_file(file_path: str, issues: list[LoggerIssue]) -> bool:
    """
    Fix logger initialization issues in a file.

    Args:
        file_path: Path to the file to fix
        issues: List of issues to fix

    Returns:
        True if any fixes were applied, False otherwise

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        fixed = False

        # Find the right place to insert logger initialization
        insert_line = 0
        for issue in issues:
            if (
                issue.issue_type == "MISSING_LOGGER"
                or issue.issue_type == "LOGGER_INIT_TOO_LATE"
            ):
                # Find the end of imports
                import_pattern = re.compile(r"^(import|from)\s+")
                for i, line in enumerate(lines):
                    if import_pattern.match(line):
                        insert_line = max(insert_line, i + 1)

                # Insert after imports and before other code
                if insert_line > 0:
                    fixed = True
                    break

        # Replace root logger usage with module logger
        for i, line in enumerate(lines):
            if (
                "logging.debug(" in line
                or "logging.info(" in line
                or "logging.warning(" in line
                or "logging.error(" in line
                or "logging.critical(" in line
                or "logging.exception(" in line
            ):
                lines[i] = line.replace("logging.", "logger.")
                fixed = True

        # Fix string concatenation in logging calls
        for issue in issues:
            if issue.issue_type == "STRING_CONCAT_IN_LOGGING":
                line_number = issue.line_number - 1  # Convert to 0-based index
                if line_number < len(lines):
                    line = lines[line_number]

                    # Simple case: replace "logger.info("text" + var)" with "logger.info(f"text{var}")"
                    # This is a simple heuristic and won't work for all cases
                    if '"' in line and " + " in line and "))" in line:
                        # Extract the string and variable parts
                        parts = line.split('"')
                        if len(parts) >= 3:
                            before_quote = parts[0]
                            string_content = parts[1]
                            after_quote = parts[2]

                            if " + " in after_quote and ")" in after_quote:
                                var_part = (
                                    after_quote.split(" + ")[1].split(")")[0].strip()
                                )
                                new_line = f'{before_quote}f"{string_content}{{{var_part}}}"))\n'
                                lines[line_number] = new_line
                                fixed = True

        if fixed:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True

        return False
    except Exception as e:
        logger.warning(f"Error fixing {file_path}: {e}")
        return False


def scan_directory(
    directory: str,
    exclude_dirs: set[str],
    exclude_files: set[str],
    exclude_patterns: list[str],
    fix: bool = False,
    verbose: bool = False,
) -> tuple[list[LoggerIssue], int]:
    """
    Scan a directory for Python files and check for logger initialization issues.

    Args:
        directory: Directory to scan
        exclude_dirs: Set of directory names to exclude
        exclude_files: Set of file names to exclude
        exclude_patterns: List of file name patterns to exclude
        fix: Whether to fix issues automatically
        verbose: Whether to show detailed output

    Returns:
        Tuple of (list of issues found, number of files fixed)

    """
    issues = []
    fixed_count = 0

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories and any directory starting with a dot
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue

            if file in exclude_files:
                continue

            if any(re.match(pattern, file) for pattern in exclude_patterns):
                continue

            file_path = os.path.join(root, file)

            if verbose:
                logger.info(f"Checking {file_path}")

            file_issues = check_file(file_path)
            issues.extend(file_issues)

            if fix and any(issue.fixable for issue in file_issues):
                if fix_file(file_path, file_issues):
                    fixed_count += 1
                    if verbose:
                        logger.info(f"Fixed {file_path}")

    return issues, fixed_count


def main() -> int:
    """
    Main function.

    Returns:
        Exit code (0 for success, non-zero for failure)

    """
    # Configure logging early in main
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Check for proper logger initialization in Python files"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Paths to scan (default: current directory)",
    )
    parser.add_argument(
        "--fix", action="store_true", help="Attempt to fix issues automatically"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--exclude-dir", action="append", help="Additional directories to exclude"
    )
    parser.add_argument(
        "--exclude-file", action="append", help="Additional files to exclude"
    )
    parser.add_argument(
        "--exclude-pattern", action="append", help="Additional file patterns to exclude"
    )
    parser.add_argument(
        "--check-string-concat",
        action="store_true",
        help="Check for string concatenation in logging calls",
    )
    parser.add_argument(
        "--check-try-except",
        action="store_true",
        help="Check for try/except blocks around imports",
    )
    parser.add_argument(
        "--check-exception-logging",
        action="store_true",
        help="Check for proper exception logging",
    )
    parser.add_argument(
        "--check-basicconfig",
        action="store_true",
        help="Check for proper basicConfig usage",
    )
    parser.add_argument("--check-all", action="store_true", help="Enable all checks")
    args = parser.parse_args()

    # Set up exclusions
    exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()
    exclude_files = DEFAULT_EXCLUDE_FILES.copy()
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS.copy()

    if args.exclude_dir:
        exclude_dirs.update(args.exclude_dir)

    if args.exclude_file:
        exclude_files.update(args.exclude_file)

    if args.exclude_pattern:
        exclude_patterns.extend(args.exclude_pattern)

    all_issues = []
    total_fixed = 0

    for path in args.paths:
        if os.path.isdir(path):
            issues, fixed_count = scan_directory(
                path,
                exclude_dirs,
                exclude_files,
                exclude_patterns,
                args.fix,
                args.verbose,
            )
            all_issues.extend(issues)
            total_fixed += fixed_count
        elif os.path.isfile(path) and path.endswith(".py"):
            if args.verbose:
                logger.info(f"Checking {path}")

            file_issues = check_file(path)
            all_issues.extend(file_issues)

            if args.fix and any(issue.fixable for issue in file_issues):
                if fix_file(path, file_issues):
                    total_fixed += 1
                    if args.verbose:
                        logger.info(f"Fixed {path}")
        else:
            logger.warning(f"Skipping {path} (not a Python file or directory)")

    # Group issues by file
    issues_by_file: dict[str, list[LoggerIssue]] = {}
    for issue in all_issues:
        if issue.file_path not in issues_by_file:
            issues_by_file[issue.file_path] = []
        issues_by_file[issue.file_path].append(issue)

    # Print issues
    for file_path, file_issues in issues_by_file.items():
        print(f"\n{file_path}:")
        for issue in file_issues:
            print(f"  Line {issue.line_number}: {issue.issue_type}: {issue.message}")

    # Print summary
    print(f"\nFound {len(all_issues)} issues in {len(issues_by_file)} files")
    if args.fix:
        print(f"Fixed {total_fixed} files")

    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())
