#!/bin/bash
# Build Sphinx documentation (if present)

if [[ -d "docs_source" ]] && command -v sphinx-build &>/dev/null; then
  echo "Building Sphinx docs..."
  sphinx-build docs_source docs/_build
else
  echo "Sphinx not configured or not found."
fi
