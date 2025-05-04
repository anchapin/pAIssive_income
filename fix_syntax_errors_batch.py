"""
Batch fix syntax errors across Python files in the project.

This script walks through the project directory and applies syntax fixes
to all Python files, excluding those matching .gitignore patterns.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Set

def get_gitignore_patterns() -> Set[str]:
    """Get patterns from .gitignore file.

    Returns:
    Set of gitignore patterns
    """
    patterns = set()
    gitignore_path = Path(__file__).parent / '.gitignore'

    if gitignore_path.exists():
    with open(gitignore_path, 'r') as f:
    for line in f:
    line = line.strip()
    if line and not line.startswith('#'):
    patterns.add(line)

    return patterns

    def should_exclude(path: str, gitignore_patterns: Set[str]) -> bool:
    """Check if a path should be excluded based on gitignore patterns.

    Args:
    path: File path to check
    gitignore_patterns: Set of patterns from .gitignore

    Returns:
    True if path should be excluded, False otherwise
    """
    path_parts = path.split(os.sep)

    for pattern in gitignore_patterns:
    # Handle directory patterns (ending with /)
    if pattern.endswith('/'):
    pattern = pattern[:-1]
    if any(fnmatch.fnmatch(part, pattern) for part in path_parts):
    return True
    # Handle file patterns
    elif any(fnmatch.fnmatch(part, pattern) for part in path_parts):
    return True
    # Handle full path patterns
    elif fnmatch.fnmatch(path, pattern):
    return True

    return False

    def find_python_files(start_dir: str, gitignore_patterns: Set[str]) -> List[str]:
    """Find all Python files in directory, excluding gitignored ones.

    Args:
    start_dir: Directory to start searching from
    gitignore_patterns: Set of patterns from .gitignore

    Returns:
    List of Python file paths
    """
    python_files = []

    for root, _, files in os.walk(start_dir):
    for file in files:
    if not file.endswith('.py'):
    continue

    full_path = os.path.join(root, file)
    relative_path = os.path.relpath(full_path, start_dir)

    if not should_exclude(relative_path, gitignore_patterns):
    python_files.append(full_path)

    return python_files

    def fix_docstring_formatting(content: str) -> str:
    """Fix docstring formatting issues.

    Args:
    content: File content to fix

    Returns:
    Fixed content
    """
    lines = content.split('\n')
    in_docstring = False
    docstring_indent = 0
    fixed_lines = []

    for i, line in enumerate(lines):
    # Detect docstring start
    if '"""' in line and not in_docstring:
    in_docstring = True
    docstring_indent = len(line) - len(line.lstrip())
    # Remove extra newline after docstring start
    if i + 1 < len(lines) and not lines[i + 1].strip():
    continue

    # Handle docstring content
    if in_docstring:
    stripped = line.strip()
    if stripped:
    # Maintain consistent indentation for docstring content
    fixed_lines.append(' ' * docstring_indent + stripped)
    else:
    fixed_lines.append(line)

    # Detect docstring end
    if '"""' in line and line.count('"""') % 2 == 0:
    in_docstring = False
    else:
    fixed_lines.append(line)

    return '\n'.join(fixed_lines)

    def fix_indentation(content: str) -> str:

    Args:
    content: File content to fix

    Returns:
    Fixed content
    """
    lines = content.split('\n')
    fixed_lines = []
    base_indent = 4

    for i, line in enumerate(lines):
    stripped = line.strip()

    if not stripped:
    fixed_lines.append('')
    continue

    # Determine correct indentation level
    indent_level = 0
    for prev_line in reversed(lines[:i]):
    prev_stripped = prev_line.strip()
    if prev_stripped and prev_stripped.endswith(':'):
    indent_level += 1
    break
    elif prev_stripped and prev_stripped.startswith(('try:', 'except ', 'finally:')):
    indent_level += 1
    break

    # Apply correct indentation
    if stripped.startswith(('except ', 'finally:')):
    indent_level = max(0, indent_level - 1)

    fixed_line = ' ' * (base_indent * indent_level) + stripped
    fixed_lines.append(fixed_line)

    return '\n'.join(fixed_lines)

    def fix_syntax_errors(file_path: str) -> None:
    """Fix syntax errors in a Python file.

    Args:
    file_path: Path to the Python file to fix
    """
    try:
    # Read with utf-8 encoding
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

    # Apply fixes
    fixed_content = content
    fixed_content = fix_docstring_formatting(fixed_content)
    fixed_content = fix_indentation(fixed_content)

    # Write back only if changes were made
    if fixed_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)
    print(f"Fixed {file_path}")

except UnicodeError as e:
    print(f"Unicode error processing {file_path}: {str(e)}")
except Exception as e:
    print(f"Error processing {file_path}: {str(e)}")

    def main():
    """Main entry point."""
    # Get project root directory
    project_dir = Path(__file__).parent

    # Get gitignore patterns
    gitignore_patterns = get_gitignore_patterns()

    # Find Python files
    python_files = find_python_files(str(project_dir), gitignore_patterns)

    print(f"Found {len(python_files)} Python files to process")

    # Fix each file
    for file_path in python_files:
    fix_syntax_errors(file_path)

    if __name__ == '__main__':
    main()
