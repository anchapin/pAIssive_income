#!/usr/bin/env python3
"""Check specific line in YAML file."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

with Path(".github/workflows/codeql-macos.yml").open() as f:
    lines = f.readlines()

logger.info("Total lines: %d", len(lines))
logger.info("Line 320: '%s'", lines[319].rstrip())
logger.info("Line 320 length: %d", len(lines[319]))
logger.info("Line 320 repr: %r", lines[319])

# Check surrounding lines
for i in range(318, 323):
    if i < len(lines):
        logger.info("Line %d: '%s'", i + 1, lines[i].rstrip())
