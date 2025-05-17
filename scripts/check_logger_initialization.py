#!/usr/bin/env python
"""
Script to check for proper logger initialization in Python files.

This script scans Python files in the specified directories and checks for common
logger initialization issues, such as:
- Using logging before initializing a logger
- Not initializing a logger at the top of the module
- Using the root logger directly instead of a module-specific logger

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
from typing import Dict, List, Optional, Set, Tuple

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

# Default directories to exclude
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
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
        fixable: bool = False
    ):
        """Initialize a logger issue.

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
        """Initialize the logger checker.

        Args:
            file_path: Path to the file being checked
        """
        self.file_path = file_path
        self.issues: List[LoggerIssue] = []
        self.logger_initialized = False
        self.logger_name = None
        self.logging_imported = False
        self.logging_used_before_init = False
        self.root_logger_used = False
        self.imports_end_line = 0
        self.docstring_end_line = 0
        self.first_logging_use_line = 0

    def visit_Import(self, node: ast.Import) -> None:
        """Visit an import node.

        Args:
            node: The AST node being visited
        """
        for name in node.names:
            if name.name == "logging":
                self.logging_imported = True
                self.imports_end_line = max(self.imports_end_line, node.end_lineno or 0)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit an import from node.

        Args:
            node: The AST node being visited
        """
        if node.module == "logging":
            self.logging_imported = True
        self.imports_end_line = max(self.imports_end_line, node.end_lineno or 0)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit an assignment node.

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
                self.logger_name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else None
                
                # Check if logger is initialized after it's used
                if self.logging_used_before_init:
                    self.issues.append(
                        LoggerIssue(
                            self.file_path,
                            "LATE_LOGGER_INIT",
                            node.lineno,
                            f"Logger initialized after it's used (first use at line {self.first_logging_use_line})",
                            fixable=True
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
                            fixable=True
                        )
                    )
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        """Visit an expression node.

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
        """Visit a function call node.

        Args:
            node: The AST node being visited
        """
        # Check for direct use of logging module
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "logging"
            and node.func.attr in ["debug", "info", "warning", "error", "critical", "exception"]
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
                    fixable=True
                )
            )
        self.generic_visit(node)

    def check(self) -> List[LoggerIssue]:
        """Check for logger initialization issues.

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
                    fixable=True
                )
            )
        return self.issues


def check_file(file_path: str) -> List[LoggerIssue]:
    """Check a file for logger initialization issues.

    Args:
        file_path: Path to the file to check

    Returns:
        List of logger issues found
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content, filename=file_path)
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
                fixable=False
            )
        ]
    except Exception as e:
        logger.warning(f"Error checking {file_path}: {e}")
        return [
            LoggerIssue(
                file_path,
                "CHECK_ERROR",
                0,
                f"Error checking file: {e}",
                fixable=False
            )
        ]


def fix_file(file_path: str, issues: List[LoggerIssue]) -> bool:
    """Fix logger initialization issues in a file.

    Args:
        file_path: Path to the file to fix
        issues: List of issues to fix

    Returns:
        True if any fixes were applied, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        fixed = False
        
        # Find the right place to insert logger initialization
        insert_line = 0
        for issue in issues:
            if issue.issue_type == "MISSING_LOGGER" or issue.issue_type == "LOGGER_INIT_TOO_LATE":
                # Find the end of imports
                import_pattern = re.compile(r"^(import|from)\s+")
                for i, line in enumerate(lines):
                    if import_pattern.match(line):
                        insert_line = max(insert_line, i + 1)
                
                # Insert after imports and before other code
                if insert_line > 0:
                    lines.insert(insert_line, "\n# Configure logging\nlogger = logging.getLogger(__name__)\n\n")
                    fixed = True
                    break
        
        # Replace root logger usage with module logger
        for i, line in enumerate(lines):
            if "logging.debug(" in line or "logging.info(" in line or "logging.warning(" in line or \
               "logging.error(" in line or "logging.critical(" in line or "logging.exception(" in line:
                lines[i] = line.replace("logging.", "logger.")
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
    exclude_dirs: Set[str],
    exclude_files: Set[str],
    exclude_patterns: List[str],
    fix: bool = False,
    verbose: bool = False
) -> Tuple[List[LoggerIssue], int]:
    """Scan a directory for Python files and check for logger initialization issues.

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
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
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
    """Main function.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Check for proper logger initialization in Python files")
    parser.add_argument("paths", nargs="*", default=["."], help="Paths to scan (default: current directory)")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues automatically")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    exclude_dirs = DEFAULT_EXCLUDE_DIRS
    exclude_files = DEFAULT_EXCLUDE_FILES
    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS
    
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
                args.verbose
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
    issues_by_file: Dict[str, List[LoggerIssue]] = {}
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
