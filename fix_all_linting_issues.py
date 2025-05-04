#!/usr/bin/env python
"""
"""
Fix all linting issues in the project.
Fix all linting issues in the project.


This script fixes the following issues:
    This script fixes the following issues:
    1. Remove unused imports (F401)
    1. Remove unused imports (F401)
    2. Fix module level imports not at top of file (E402)
    2. Fix module level imports not at top of file (E402)
    3. Fix redefinitions of unused variables (F811)
    3. Fix redefinitions of unused variables (F811)
    """
    """


    import os
    import os




    def fix_unused_imports():
    def fix_unused_imports():
    """Fix unused imports in Python files."""
    print("Fixing unused imports...")
    os.system("ruff check --select F401 --fix .")
    print("Done fixing unused imports.")


    def fix_imports_not_at_top():
    """Fix module level imports not at top of file."""
    print("Fixing imports not at top of file...")
    os.system("ruff check --select E402 --fix .")
    print("Done fixing imports not at top of file.")


    def fix_redefined_unused_variables():
    """Fix redefinitions of unused variables."""
    print("Fixing redefined unused variables...")
    os.system("ruff check --select F811 --fix .")
    print("Done fixing redefined unused variables.")


    def fix_line_too_long():
    """Fix lines that are too long."""
    print("Fixing lines that are too long...")
    os.system("black .")
    print("Done fixing lines that are too long.")


    def fix_missing_whitespace():
    """Fix missing whitespace around operators."""
    print("Fixing missing whitespace...")
    os.system("black .")
    print("Done fixing missing whitespace.")


    def fix_trailing_whitespace():
    """Fix trailing whitespace."""
    print("Fixing trailing whitespace...")
    os.system("ruff check --select W291 --fix .")
    print("Done fixing trailing whitespace.")


    def fix_indentation():
    """Fix indentation issues."""
    print("Fixing indentation issues...")
    os.system("black .")
    print("Done fixing indentation issues.")


    def fix_import_order():
    """Fix import order."""
    print("Fixing import order...")
    os.system("isort .")
    print("Done fixing import order.")


    def fix_all_files():
    """Fix all linting issues in all files."""
    print("Fixing all linting issues...")
    fix_unused_imports()
    fix_imports_not_at_top()
    fix_redefined_unused_variables()
    fix_line_too_long()
    fix_missing_whitespace()
    fix_trailing_whitespace()
    fix_indentation()
    fix_import_order()
    print("All linting issues fixed!")


    if __name__ == "__main__":
    fix_all_files()
    print("All linting issues fixed!")
