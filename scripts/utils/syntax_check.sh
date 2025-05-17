#!/bin/bash
# Simple script to check Python syntax

# Check a specific file
check_file() {
  python -m py_compile "$1" 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "Syntax error in $1"
    return 1
  fi
  return 0
}

# Find all Python files excluding common directories to ignore
find_python_files() {
  find . -name "*.py" -type f -not -path "*/\.*" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/build/*" -not -path "*/dist/*" -not -path "*/__pycache__/*"
}

# Main function
main() {
  if [ $# -gt 0 ]; then
    # Check specific files provided as arguments
    for file in "$@"; do
      check_file "$file" || exit 1
    done
  else
    # Find and check all Python files
    files=$(find_python_files)
    if [ -z "$files" ]; then
      echo "No Python files found"
      exit 0
    fi

    for file in $files; do
      check_file "$file" || exit 1
    done
  fi

  echo "All Python files passed syntax check"
  exit 0
}

# Run the main function with all arguments
main "$@"
