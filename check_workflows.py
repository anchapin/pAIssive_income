#!/usr/bin/env python3
"""
Script to validate YAML syntax of GitHub workflow files
"""

import yaml
import os
import sys

def check_workflow_files():
    """Check all workflow files for YAML syntax errors"""
    workflow_dir = '.github/workflows'
    errors = []
    successes = []

    if not os.path.exists(workflow_dir):
        print(f"ERROR: Workflow directory {workflow_dir} not found")
        return False

    # Get all YAML files in the workflows directory
    workflow_files = [f for f in os.listdir(workflow_dir) if f.endswith(('.yml', '.yaml'))]

    if not workflow_files:
        print("ERROR: No workflow files found")
        return False

    print(f"Checking {len(workflow_files)} workflow files...\n")

    for filename in sorted(workflow_files):
        filepath = os.path.join(workflow_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print(f"PASS: {filename}")
            successes.append(filename)
        except yaml.YAMLError as e:
            print(f"FAIL: {filename}: {e}")
            errors.append((filename, str(e)))
        except Exception as e:
            print(f"FAIL: {filename}: {e}")
            errors.append((filename, str(e)))

    print(f"\nSummary:")
    print(f"   PASSED: {len(successes)} files")
    print(f"   FAILED: {len(errors)} files")

    if errors:
        print(f"\nError Details:")
        for filename, error in errors:
            print(f"   {filename}: {error}")
        return False

    return True

if __name__ == "__main__":
    success = check_workflow_files()
    sys.exit(0 if success else 1)
