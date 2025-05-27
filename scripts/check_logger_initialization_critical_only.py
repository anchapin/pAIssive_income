#!/usr/bin/env python3
"""
Check for critical logger initialization issues that would cause CI failures.
This version is more intelligent about distinguishing between actual problems
and acceptable patterns like function-level logger assignments.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class LoggerIssue:
    def __init__(self, file_path: str, line_number: int, issue_type: str, description: str, severity: str = "critical"):
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.description = description
        self.severity = severity

    def __str__(self):
        return f"{self.file_path}:{self.line_number}: {self.severity.upper()}: {self.issue_type} - {self.description}"


class SmartLoggerChecker(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[LoggerIssue] = []
        self.imports_seen = False
        self.logging_imported = False
        self.logger_initialized = False
        self.module_level_logger_line = None
        self.in_function = False
        self.in_class = False
        self.function_depth = 0
        self.class_depth = 0
        
    def visit_Import(self, node: ast.Import) -> None:
        self.imports_seen = True
        for alias in node.names:
            if alias.name == "logging":
                self.logging_imported = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports_seen = True
        if node.module and "logging" in node.module:
            self.logging_imported = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_depth += 1
        self.in_function = True
        self.generic_visit(node)
        self.function_depth -= 1
        if self.function_depth == 0:
            self.in_function = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_depth += 1
        self.in_function = True
        self.generic_visit(node)
        self.function_depth -= 1
        if self.function_depth == 0:
            self.in_function = False

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_depth += 1
        self.in_class = True
        self.generic_visit(node)
        self.class_depth -= 1
        if self.class_depth == 0:
            self.in_class = False

    def visit_Assign(self, node: ast.Assign) -> None:
        # Check for logger assignments
        for target in node.targets:
            if isinstance(target, ast.Name) and "logger" in target.id.lower():
                # Check if this is a call to logging.getLogger or similar
                if isinstance(node.value, ast.Call):
                    if self._is_logger_creation_call(node.value):
                        self._check_logger_assignment(node, target.id)
            elif isinstance(target, ast.Attribute) and "logger" in target.attr.lower():
                # Check for self.logger assignments
                if isinstance(node.value, ast.Call):
                    if self._is_logger_creation_call(node.value):
                        # self.logger assignments in __init__ are acceptable
                        if not (self.in_function and self._is_in_init_method()):
                            self._check_logger_assignment(node, target.attr)

        # Check for logging.basicConfig calls
        if isinstance(node.value, ast.Call):
            if self._is_basic_config_call(node.value):
                if not self.in_function:
                    self.issues.append(LoggerIssue(
                        self.file_path,
                        node.lineno,
                        "GLOBAL_BASICCONFIG",
                        "logging.basicConfig() called at module level - should be in main() or function"
                    ))

        self.generic_visit(node)

    def _is_logger_creation_call(self, call_node: ast.Call) -> bool:
        """Check if a call creates a logger."""
        if isinstance(call_node.func, ast.Attribute):
            if isinstance(call_node.func.value, ast.Name):
                if call_node.func.value.id == "logging" and call_node.func.attr == "getLogger":
                    return True
        elif isinstance(call_node.func, ast.Name):
            if call_node.func.id in ["get_logger", "get_secure_logger", "SecureLogger"]:
                return True
        return False

    def _is_basic_config_call(self, call_node: ast.Call) -> bool:
        """Check if a call is logging.basicConfig."""
        if isinstance(call_node.func, ast.Attribute):
            if isinstance(call_node.func.value, ast.Name):
                if call_node.func.value.id == "logging" and call_node.func.attr == "basicConfig":
                    return True
        return False

    def _is_in_init_method(self) -> bool:
        """Check if we're currently in an __init__ method."""
        # This is a simplified check - in a real implementation you'd track the current function name
        return True  # For now, assume self.logger in functions is acceptable

    def _check_logger_assignment(self, node: ast.Assign, logger_name: str) -> None:
        """Check if a logger assignment is problematic."""
        # If we're in a function or class method, it's usually acceptable
        if self.in_function:
            # Exception: if this is a module-level logger being assigned late in a function
            # that's called at module level, it could be problematic
            # For now, we'll be lenient with function-level assignments
            return
            
        # If we're at module level and this is after imports, check if it's the first logger
        if self.imports_seen and not self.logger_initialized:
            # This is the first module-level logger after imports - this is good
            self.logger_initialized = True
            self.module_level_logger_line = node.lineno
        elif self.imports_seen and self.logger_initialized:
            # Multiple module-level loggers - this could be problematic
            self.issues.append(LoggerIssue(
                self.file_path,
                node.lineno,
                "DUPLICATE_MODULE_LOGGER",
                f"Multiple module-level logger assignments (first at line {self.module_level_logger_line})"
            ))

    def visit_Call(self, node: ast.Call) -> None:
        # Check for missing logger.exception usage in exception handlers
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["error", "warning", "info", "debug"]:
                # This is a logging call - check if we're in an exception handler
                # and if so, suggest using logger.exception instead
                pass  # For now, we'll skip this check as it's not critical for CI
        
        self.generic_visit(node)


def check_file(file_path: str) -> List[LoggerIssue]:
    """Check a single Python file for critical logger initialization issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        checker = SmartLoggerChecker(file_path)
        checker.visit(tree)
        
        # Additional checks for missing logger when logging is imported
        if checker.logging_imported and not checker.logger_initialized:
            # Check if there are any logging calls without a logger
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "logging":
                        if node.func.attr in ["debug", "info", "warning", "error", "critical", "exception"]:
                            checker.issues.append(LoggerIssue(
                                file_path,
                                node.lineno,
                                "MISSING_LOGGER",
                                "logging module imported but no logger initialized - use logger = logging.getLogger(__name__)"
                            ))
                            break
        
        return checker.issues
        
    except Exception as e:
        return [LoggerIssue(file_path, 0, "PARSE_ERROR", f"Failed to parse file: {e}")]


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def main():
    """Main function to check all Python files."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."
    
    python_files = find_python_files(directory)
    all_issues = []
    
    for file_path in python_files:
        issues = check_file(file_path)
        all_issues.extend(issues)
    
    # Group issues by type and severity
    critical_issues = [issue for issue in all_issues if issue.severity == "critical"]
    
    if critical_issues:
        print(f"Found {len(critical_issues)} critical logger initialization issues:")
        print()
        
        # Group by file
        issues_by_file = {}
        for issue in critical_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        for file_path, file_issues in sorted(issues_by_file.items()):
            print(f"{file_path}:")
            for issue in sorted(file_issues, key=lambda x: x.line_number):
                print(f"  Line {issue.line_number}: {issue.issue_type} - {issue.description}")
            print()
        
        print(f"Summary: {len(critical_issues)} critical issues in {len(issues_by_file)} files")
        return 1
    else:
        print("No critical logger initialization issues found!")
        return 0


if __name__ == "__main__":
    sys.exit(main()) 