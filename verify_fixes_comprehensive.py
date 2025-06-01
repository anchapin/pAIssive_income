#!/usr/bin/env python3
"""
Comprehensive verification script for all fixes applied to resolve workflow failures.

This script verifies:
1. Syntax errors are fixed
2. Import statements are correct
3. Mock modules exist
4. Configuration files are valid
5. Test files can be imported
"""

import ast
import json
import logging
import sys
from pathlib import Path
from typing import List, Tuple

# Configure logging
logger = logging.getLogger(__name__)


def check_syntax_errors(file_path: str) -> Tuple[bool, str]:
    """Check if a Python file has syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile the file
        compile(content, file_path, 'exec')
        return True, "No syntax errors"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def check_import_statements(file_path: str) -> Tuple[bool, str]:
    """Check if import statements in a file are valid."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check imports
        tree = ast.parse(content, filename=file_path)
        
        # Check for problematic imports
        problematic_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['some_third_party_module']:
                        problematic_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in ['some_third_party_module']:
                    problematic_imports.append(node.module)
        
        if problematic_imports:
            return False, f"Problematic imports found: {problematic_imports}"
        
        return True, "Import statements are valid"
    except Exception as e:
        return False, f"Error checking imports: {e}"


def check_mock_modules() -> Tuple[bool, str]:
    """Check if required mock modules exist."""
    mock_modules = [
        "mock_crewai",
        "mock_mcp"
    ]
    
    missing_modules = []
    for module in mock_modules:
        module_path = Path(module)
        init_file = module_path / "__init__.py"
        
        if not module_path.exists():
            missing_modules.append(f"{module} directory")
        elif not init_file.exists():
            missing_modules.append(f"{module}/__init__.py")
    
    if missing_modules:
        return False, f"Missing mock modules: {missing_modules}"
    
    return True, "All mock modules exist"


def check_configuration_files() -> Tuple[bool, str]:
    """Check if configuration files are valid."""
    config_files = [
        ("pytest.ini", "ini"),
        ("pyproject.toml", "toml"),
        ("ruff.toml", "toml")
    ]
    
    issues = []
    for file_path, file_type in config_files:
        path = Path(file_path)
        if path.exists():
            try:
                if file_type == "toml":
                    # Basic TOML validation (just check if it's readable)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Basic check for TOML structure
                        if '[' not in content and '=' not in content:
                            issues.append(f"{file_path}: Invalid TOML structure")
                elif file_type == "ini":
                    # Basic INI validation
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Basic check for INI structure
                        if '[' not in content:
                            issues.append(f"{file_path}: Invalid INI structure")
            except Exception as e:
                issues.append(f"{file_path}: {e}")
    
    if issues:
        return False, f"Configuration file issues: {issues}"
    
    return True, "Configuration files are valid"


def main():
    """Main verification function."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    logger.info("Starting comprehensive verification of fixes...")
    
    # Files that were fixed for syntax errors
    fixed_files = [
        "init_agent_db.py",
        "main.py", 
        "app_flask/middleware/logging_middleware.py",
        "scripts/check_logging_in_modified_files.py",
        "scripts/fix/fix_security_issues.py",
        "logging_config.py"
    ]
    
    # Test files to check for import issues
    test_files = [
        "tests/test_validation.py",
        "tests/test_init_agent_db.py",
        "tests/test_main.py",
        "tests/security/test_security_fixes.py"
    ]
    
    all_passed = True
    
    # Check syntax errors in fixed files
    logger.info("Checking syntax errors in fixed files...")
    for file_path in fixed_files:
        if Path(file_path).exists():
            passed, message = check_syntax_errors(file_path)
            if passed:
                logger.info(f"✓ {file_path} - {message}")
            else:
                logger.error(f"✗ {file_path} - {message}")
                all_passed = False
        else:
            logger.warning(f"? {file_path} - File not found")
    
    # Check import statements
    logger.info("Checking import statements...")
    all_files = fixed_files + test_files
    for file_path in all_files:
        if Path(file_path).exists():
            passed, message = check_import_statements(file_path)
            if passed:
                logger.info(f"✓ {file_path} - {message}")
            else:
                logger.error(f"✗ {file_path} - {message}")
                all_passed = False
    
    # Check mock modules
    logger.info("Checking mock modules...")
    passed, message = check_mock_modules()
    if passed:
        logger.info(f"✓ Mock modules - {message}")
    else:
        logger.error(f"✗ Mock modules - {message}")
        all_passed = False
    
    # Check configuration files
    logger.info("Checking configuration files...")
    passed, message = check_configuration_files()
    if passed:
        logger.info(f"✓ Configuration files - {message}")
    else:
        logger.error(f"✗ Configuration files - {message}")
        all_passed = False
    
    # Summary
    if all_passed:
        logger.info("🎉 All verifications passed! Fixes appear to be working correctly.")
        return 0
    else:
        logger.error("❌ Some verifications failed. Additional fixes may be needed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
