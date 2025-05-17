#!/bin/bash
# Shell script to run fix_linting_issues.py with the provided arguments

echo "Running fix_linting_issues.py..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python not found in PATH!"
    exit 1
fi

# Check if the script exists
if [ ! -f fix_linting_issues.py ]; then
    echo "Error: fix_linting_issues.py not found!"
    exit 1
fi

# Run the script with all arguments passed to this shell script
python fix_linting_issues.py "$@"

# Check exit code
if [ $? -ne 0 ]; then
    echo "Error: fix_linting_issues.py failed!"
    exit 1
fi

echo "Script completed successfully."
exit 0
