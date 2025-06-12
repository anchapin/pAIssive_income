#!/usr/bin/env python3
"""Script to validate YAML syntax of GitHub workflow files."""

import logging
import sys
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def check_workflow_files() -> bool:
    """Check all workflow files for YAML syntax errors."""
    workflow_dir = ".github/workflows"
    errors = []
    successes = []

    if not Path(workflow_dir).exists():
        logger.error("Workflow directory %s not found", workflow_dir)
        return False

    # Get all YAML files in the workflows directory
    workflow_files = [
        f.name for f in Path(workflow_dir).iterdir() if f.suffix in {".yml", ".yaml"}
    ]

    if not workflow_files:
        logger.error("No workflow files found")
        return False

    logger.info("Checking %d workflow files...", len(workflow_files))

    for filename in sorted(workflow_files):
        filepath = Path(workflow_dir) / filename
        try:
            with filepath.open(encoding="utf-8") as f:
                yaml.safe_load(f)
            logger.info("PASS: %s", filename)
            successes.append(filename)
        except yaml.YAMLError as e:
            logger.error("FAIL: %s: %s", filename, e)
            errors.append((filename, str(e)))
        except OSError as e:
            logger.error("FAIL: %s: %s", filename, e)
            errors.append((filename, str(e)))

    logger.info("Summary:")
    logger.info("   PASSED: %d files", len(successes))
    logger.info("   FAILED: %d files", len(errors))

    if errors:
        logger.info("Error Details:")
        for filename, error in errors:
            logger.error("   %s: %s", filename, error)
        return False

    return True


if __name__ == "__main__":
    success = check_workflow_files()
    sys.exit(0 if success else 1)
