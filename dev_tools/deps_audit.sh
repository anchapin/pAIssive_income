#!/bin/bash
# Run pip-audit for Python dependency security audit

if command -v pip-audit &>/dev/null; then
  echo "Running pip-audit..."
  pip-audit
else
  echo "pip-audit not found."
fi