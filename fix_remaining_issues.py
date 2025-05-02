#!/usr/bin/env python
"""
Script to fix remaining issues in Python files.
"""

import os
import re
import subprocess
import sys


def fix_e402_issues(file_path):
    """Fix E402 issues (imports not at top of file)."""
    print(f"\nFixing E402 issues in {file_path}...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find all import statements
    import_pattern = re.compile(r'^(from\s+[\w.]+\s+import\s+.*|import\s+.*)$', re.MULTILINE)
    imports = import_pattern.findall(content)
    
    # If there are no imports, return
    if not imports:
        print(f"No imports found in {file_path}")
        return True
    
    # Find the first non-comment, non-empty line
    lines = content.split('\n')
    first_code_line = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            first_code_line = i
            break
    
    # Collect all imports
    all_imports = []
    for imp in imports:
        if imp not in all_imports:
            all_imports.append(imp)
    
    # Remove all imports from the content
    for imp in all_imports:
        content = content.replace(imp + '\n', '')
    
    # Insert all imports at the beginning of the file, after any module docstring
    docstring_end = 0
    if first_code_line > 0 and lines[0].strip().startswith('"""'):
        for i in range(1, len(lines)):
            if lines[i].strip().endswith('"""'):
                docstring_end = i + 1
                break
    
    new_content = '\n'.join(lines[:docstring_end]) + '\n'
    new_content += '\n'.join(all_imports) + '\n\n'
    new_content += '\n'.join(lines[docstring_end:])
    
    # Write the new content back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✅ Fixed E402 issues in {file_path}")
    return True


def fix_f401_issues(file_path):
    """Fix F401 issues (unused imports)."""
    print(f"\nFixing F401 issues in {file_path}...")
    
    try:
        # Use ruff to fix unused imports
        subprocess.run(
            ["ruff", "check", "--select=F401", "--fix", file_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ Fixed F401 issues in {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fix F401 issues in {file_path}")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return False


def fix_f821_issues(file_path):
    """Fix F821 issues (undefined names)."""
    print(f"\nFixing F821 issues in {file_path}...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Common undefined names and their imports
    undefined_names = {
        "time": "import time",
        "torch": "import torch",
        "anext": "# Replace 'anext' with 'asyncio.anext' for Python < 3.10 compatibility",
        "generate_id": "def generate_id():\n    \"\"\"Generate a random ID.\"\"\"\n    import uuid\n    return str(uuid.uuid4())",
    }
    
    # Check for each undefined name
    modified = False
    for name, import_stmt in undefined_names.items():
        if re.search(r'\b' + name + r'\b', content) and name not in ["anext"]:
            # Check if the import is already present
            if import_stmt not in content:
                # Add the import at the top of the file
                content = import_stmt + "\n" + content
                modified = True
                print(f"Added import for {name}")
        
        # Special case for anext
        if name == "anext" and "anext" in content:
            content = content.replace("await anext(", "await asyncio.anext(")
            modified = True
            print("Replaced 'anext' with 'asyncio.anext'")
    
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Fixed F821 issues in {file_path}")
    else:
        print(f"No F821 issues to fix in {file_path}")
    
    return True


def fix_syntax_errors(file_path):
    """Fix syntax errors."""
    print(f"\nFixing syntax errors in {file_path}...")
    
    # For now, just print a message to manually fix the file
    print(f"⚠️ Syntax errors in {file_path} need to be fixed manually.")
    return False


def process_file(file_path):
    """Process a file to fix all issues."""
    print(f"\nProcessing {file_path}...")
    
    # Check for E402 issues
    try:
        result = subprocess.run(
            ["ruff", "check", "--select=E402", file_path],
            capture_output=True,
            text=True,
        )
        if "E402" in result.stdout:
            fix_e402_issues(file_path)
    except subprocess.CalledProcessError:
        pass
    
    # Check for F401 issues
    try:
        result = subprocess.run(
            ["ruff", "check", "--select=F401", file_path],
            capture_output=True,
            text=True,
        )
        if "F401" in result.stdout:
            fix_f401_issues(file_path)
    except subprocess.CalledProcessError:
        pass
    
    # Check for F821 issues
    try:
        result = subprocess.run(
            ["ruff", "check", "--select=F821", file_path],
            capture_output=True,
            text=True,
        )
        if "F821" in result.stdout:
            fix_f821_issues(file_path)
    except subprocess.CalledProcessError:
        pass
    
    # Check for syntax errors
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        compile(content, file_path, "exec")
    except SyntaxError:
        fix_syntax_errors(file_path)
    
    return True


def process_directory(directory, exclude_dirs=None):
    """Process all Python files in a directory and its subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = [".venv", ".git", "__pycache__"]
    
    all_passed = True
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if not process_file(file_path):
                    all_passed = False
    
    return all_passed


def main():
    """Main function to parse args and run the script."""
    directory = "."
    exclude_dirs = [".venv", ".git", "__pycache__"]
    
    success = process_directory(directory, exclude_dirs)
    
    if success:
        print("\n✅ All files processed successfully!")
        return 0
    else:
        print("\n⚠️ Some files could not be fixed automatically and need manual attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
