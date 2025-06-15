#!/usr/bin/env python3
"""Script to validate YAML syntax of GitHub workflow files."""

import os
import sys

import yaml


def check_workflow_files() -> bool:
    """Check all workflow files for YAML syntax errors."""
    workflow_dir = ".github/workflows"
    errors = []
    successes = []

    if not os.path.exists(workflow_dir):
        return False

    # Get all YAML files in the workflows directory
    workflow_files = [f for f in os.listdir(workflow_dir) if f.endswith((".yml", ".yaml"))]

    if not workflow_files:
        return False


    for filename in sorted(workflow_files):
        filepath = os.path.join(workflow_dir, filename)
        try:
            with open(filepath, encoding="utf-8") as f:
                yaml.safe_load(f)
            successes.append(filename)
        except yaml.YAMLError as e:
            errors.append((filename, str(e)))
        except Exception as e:
            errors.append((filename, str(e)))


    if errors:
        for filename, _error in errors:
            pass
        return False

    return True

if __name__ == "__main__":
    success = check_workflow_files()
    sys.exit(0 if success else 1)
