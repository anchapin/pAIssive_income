import glob
import os

import yaml


def validate_workflows():
    workflow_dir = ".github/workflows"
    workflow_files = glob.glob(os.path.join(workflow_dir, "*.yml"))

    print(f"Checking {len(workflow_files)} workflow files...")
    errors = []

    for file_path in workflow_files:
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

if __name__ == "__main__":
    validate_workflows()
