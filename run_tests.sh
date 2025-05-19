#!/bin/bash
# Run pytest with the specified arguments

# Create security-reports directory
mkdir -p security-reports
echo "Created security-reports directory"

# Set environment variables to bypass virtual environment checks
export PYTHONNOUSERSITE=1
export SKIP_VENV_CHECK=1

# Set CI environment variable if running in GitHub Actions
if [ -n "$GITHUB_ACTIONS" ]; then
    export CI=1
    echo "GitHub Actions environment detected"
fi

# Run pytest with the specified arguments
python -m pytest "$@"
exit $?
