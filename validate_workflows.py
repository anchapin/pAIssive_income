"""Validate GitHub workflow YAML files."""

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

    for file_path in workflow_files:
        try:
            with file_path.open(encoding="utf-8") as f:
                yaml.safe_load(f)
            logger.info("OK: %s", file_path.name)
        except yaml.YAMLError as e:
            logger.exception("ERROR: %s", file_path.name)
            errors.append((file_path, str(e)))
        except OSError as e:
            logger.exception("ERROR: %s", file_path.name)
            errors.append((file_path, str(e)))

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


if __name__ == "__main__":
    validate_workflows()
