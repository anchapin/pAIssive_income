#!/bin/bash
# Shell script to run the fix_pre_commit_issues.py script

echo "Running fix_pre_commit_issues.py..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python not found in PATH!"
    exit 1
fi

# Check if the script exists
if [ ! -f fix_pre_commit_issues.py ]; then
    echo "Error: fix_pre_commit_issues.py not found!"
    exit 1
fi

# Run the script with verbose output
python fix_pre_commit_issues.py --verbose "$@"

# Check exit code
if [ $? -ne 0 ]; then
    echo "Error: fix_pre_commit_issues.py failed!"
    exit 1
fi

echo "Pre-commit issues fixed successfully."
exit 0
