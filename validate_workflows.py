"""Validate YAML syntax in GitHub workflow files."""

from __future__ import annotations

from pathlib import Path

import yaml


def validate_workflows() -> bool:
    """Validate workflow files for correct YAML syntax."""
    workflow_dir = Path(".github/workflows")
    workflow_files = list(workflow_dir.glob("*.yml"))

    errors = []

    for file_path in workflow_files:
        try:
            with file_path.open(encoding="utf-8") as f:
                yaml.safe_load(f)
        except Exception as e:
            errors.append((file_path, str(e)))

    if errors:
        for _file_path, _error in errors:
            pass

    return len(errors) == 0

if __name__ == "__main__":
    validate_workflows()
