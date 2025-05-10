#!/bin/bash
# Run dependency security audit using uv pip audit
if command -v uv &>/dev/null; then
    echo "Running uv pip audit..."
    uv pip audit
else
    echo "uv not found."
fi
