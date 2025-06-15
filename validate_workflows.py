import glob
import os

import yaml


def validate_workflows():
    workflow_dir = ".github/workflows"
    workflow_files = glob.glob(os.path.join(workflow_dir, "*.yml"))

    errors = []

    for file_path in workflow_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                yaml.safe_load(f)
        except Exception as e:
            f"ERROR: {os.path.basename(file_path)}: {e!s}"
            errors.append((file_path, str(e)))


    if errors:
        for file_path, _error in errors:
            pass

    return len(errors) == 0

if __name__ == "__main__":
    validate_workflows()
