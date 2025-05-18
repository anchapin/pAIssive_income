#!/usr/bin/env python3
"""Test if Python is working correctly."""

import sys
import os

def main():
    """Print Python environment information."""
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Is virtual environment: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
    print(f"sys.prefix: {sys.prefix}")
    if hasattr(sys, 'base_prefix'):
        print(f"sys.base_prefix: {sys.base_prefix}")

if __name__ == "__main__":
    main()
