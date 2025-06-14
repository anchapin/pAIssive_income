"""Validate GitHub workflow YAML files."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

<<<<<<< HEAD

def validate_workflows() -> bool:
    """Validate all GitHub workflow YAML files."""
    workflow_dir = Path(".github/workflows")
    workflow_files = list(workflow_dir.glob("*.yml"))

    logger.info("Checking %d workflow files...", len(workflow_files))
=======
def validate_workflows():
    workflow_dir = ".github/workflows"
    workflow_files = glob.glob(os.path.join(workflow_dir, "*.yml"))

    print(f"Checking {len(workflow_files)} workflow files...")
>>>>>>> origin/main
    errors = []

    # Process files outside the loop to avoid performance overhead
    for file_path in workflow_files:
<<<<<<< HEAD
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


=======
        try:
            with open(file_path, encoding="utf-8") as f:
                yaml.safe_load(f)
            print(f"OK: {os.path.basename(file_path)}")
        except Exception as e:
            error_msg = f"ERROR: {os.path.basename(file_path)}: {e!s}"
            print(error_msg)
            errors.append((file_path, str(e)))

    print(f"\nSummary: {len(workflow_files) - len(errors)}/{len(workflow_files)} files valid")

    if errors:
        print("\nDetailed errors:")
        for file_path, error in errors:
            print(f"\n{file_path}:")
            print(f"  {error}")

    return len(errors) == 0

>>>>>>> origin/main
if __name__ == "__main__":
    validate_workflows()
