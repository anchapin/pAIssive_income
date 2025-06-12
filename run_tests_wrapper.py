#!/usr/bin/env python3
"""
Simple wrapper script for running tests.

This script runs pytest directly without any virtual environment checks.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Create security-reports directory
Path("security-reports").mkdir(parents=True, exist_ok=True)

# Set environment variables to bypass virtual environment checks
os.environ["PYTHONNOUSERSITE"] = "1"
os.environ["SKIP_VENV_CHECK"] = "1"

# Set CI environment variable if running in GitHub Actions
if os.environ.get("GITHUB_ACTIONS"):
    os.environ["CI"] = "1"

# Get command line arguments
args = sys.argv[1:]

# Add default arguments if none provided
if not args:
    args = ["-v"]


def _safe_subprocess_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:  # noqa: ANN003
    cmd = [str(c) if isinstance(c, Path) else c for c in cmd]
    if "cwd" in kwargs and isinstance(kwargs["cwd"], Path):
        kwargs["cwd"] = str(kwargs["cwd"])
    allowed_keys = {
        "cwd",
        "timeout",
        "check",
        "shell",
        "text",
        "capture_output",
        "input",
        "encoding",
        "errors",
        "env",
    }
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}
    return subprocess.run(cmd, check=False, **filtered_kwargs)  # noqa: S603


# Run pytest directly
try:
    # The following subprocess call is static and not user-supplied; shell=False is used, so this is safe.
    result = _safe_subprocess_run(
        [sys.executable, "-m", "pytest", *args],
        timeout=3600,  # 1 hour timeout
    )
    sys.exit(result.returncode)
except (subprocess.SubprocessError, OSError):
    sys.exit(1)
