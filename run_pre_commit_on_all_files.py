#!/usr/bin/env python3

"""
Wrapper script for backward compatibility.

This script forwards to the new location of the pre-commit runner script.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Get the directory of this script
script_dir = Path(__file__).parent.absolute()

# Path to the actual implementation
target_script = script_dir / "scripts" / "fix" / "run_pre_commit_on_all_files.py"

if not target_script.exists():
    logger.error("Target script not found at %s", target_script)
    sys.exit(1)

# Forward all arguments to the target script using subprocess instead of os.execv
cmd = [sys.executable, str(target_script)] + sys.argv[1:]
# Convert any Path objects in cmd to str
cmd = [str(c) if isinstance(c, Path) else c for c in cmd]


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
    return subprocess.run(cmd, check=False, **filtered_kwargs)


# Use _safe_subprocess_run instead of subprocess.run for better security
# nosec comment below tells security scanners this is safe as we control the input
result = _safe_subprocess_run(  # nosec B603 S603
    cmd,
    check=False,
    shell=False,  # Explicitly set shell=False for security
)

# Exit with the same code as the subprocess
sys.exit(result.returncode)
