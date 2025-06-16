#!/bin/bash
# Run pyright static type checking

if command -v pyright &>/dev/null; then
  echo "Running pyright..."
  pyright .
else
  echo "pyright not found."
fi
