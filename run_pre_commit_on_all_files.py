#!/usr/bin/env python3

"""
Wrapper script for backward compatibility.

This script forwards to the new location of the pre-commit runner script.
"""

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

# Use subprocess.run instead of os.execv for better security
# nosec comment below tells security scanners this is safe as we control the input
result = subprocess.run(  # nosec B603 S603
    cmd,
    check=False,
    shell=False,  # Explicitly set shell=False for security
)

# Exit with the same code as the subprocess
sys.exit(result.returncode)
