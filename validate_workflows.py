"""Validate GitHub workflow YAML files."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def validate_workflows() -> bool:
    """Validate all GitHub workflow YAML files."""
    workflow_dir = Path(".github/workflows")
    workflow_files = list(workflow_dir.glob("*.yml"))

    logger.info("Checking %d workflow files...", len(workflow_files))
    errors = []

    # Process files outside the loop to avoid performance overhead
    for file_path in workflow_files:
        error = _validate_single_workflow(file_path)
        if error:
            errors.append(error)

    logger.info(
        "Summary: %d/%d files valid",
        len(workflow_files) - len(errors),
        len(workflow_files),
    )

    if errors:
        logger.info("Detailed errors:")
        for file_path, error in errors:
            logger.error("%s: %s", file_path, error)

    return len(errors) == 0


def _validate_single_workflow(file_path: Path) -> tuple[Path, str] | None:
    """Validate a single workflow file and return error if any."""
    try:
        with file_path.open(encoding="utf-8") as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.exception("ERROR: %s", file_path.name)
        return (file_path, str(e))
    except OSError as e:
        logger.exception("ERROR: %s", file_path.name)
        return (file_path, str(e))
    else:
        logger.info("OK: %s", file_path.name)
        return None


if __name__ == "__main__":
    validate_workflows()
