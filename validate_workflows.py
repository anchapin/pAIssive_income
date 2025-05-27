#!/usr/bin/env python3
"""
Validate GitHub Actions workflow files for common issues.

This script checks for:
1. Basic YAML syntax
2. Required workflow structure
3. Common configuration issues
"""

from pathlib import Path

import yaml


def validate_workflow_file(file_path):
    """Validate a single workflow file."""
    issues = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check for basic YAML syntax
        try:
            workflow = yaml.safe_load(content)
        except yaml.YAMLError as e:
            issues.append(f"YAML syntax error: {e}")
            return issues

        # Check required fields
        if not isinstance(workflow, dict):
            issues.append("Workflow must be a dictionary")
            return issues

        if "name" not in workflow:
            issues.append("Missing 'name' field")

        if "on" not in workflow:
            issues.append("Missing 'on' field (workflow triggers)")

        if "jobs" not in workflow:
            issues.append("Missing 'jobs' field")

        # Check for common issues
        if "true" in workflow:
            issues.append("Found 'true' key - should probably be 'on'")

        # Check jobs structure
        if "jobs" in workflow and isinstance(workflow["jobs"], dict):
            for job_name, job_config in workflow["jobs"].items():
                if not isinstance(job_config, dict):
                    issues.append(f"Job '{job_name}' must be a dictionary")
                    continue

                if "runs-on" not in job_config:
                    issues.append(f"Job '{job_name}' missing 'runs-on' field")

                if "steps" not in job_config:
                    issues.append(f"Job '{job_name}' missing 'steps' field")

        # Check for malformed pip install commands
        if (
            "pytest --ignore=" in content
            and "pytest --ignore=" in content[content.find("pytest --ignore=") + 20 :]
        ):
            issues.append(
                "Found potentially malformed pip install command with repeated pytest"
            )

        return issues

    except Exception as e:
        return [f"Error reading file: {e}"]


def main():
    """Main function to validate all workflow files."""
    print("🔍 Validating GitHub Actions workflow files...")

    # Find all YAML files in .github/workflows/
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print(f"❌ Workflow directory {workflow_dir} not found!")
        return

    yaml_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    if not yaml_files:
        print("❌ No YAML workflow files found!")
        return

    print(f"📁 Found {len(yaml_files)} workflow files to validate...")

    total_issues = 0
    for yaml_file in yaml_files:
        print(f"\n🔍 Validating {yaml_file}...")
        issues = validate_workflow_file(yaml_file)

        if issues:
            print(f"❌ Found {len(issues)} issue(s):")
            for issue in issues:
                print(f"   • {issue}")
            total_issues += len(issues)
        else:
            print("✅ No issues found")

    print(
        f"\n📊 Summary: Found {total_issues} total issues across {len(yaml_files)} files"
    )

    if total_issues == 0:
        print("🎉 All workflow files appear to be valid!")
    else:
        print("⚠️  Some issues were found. Please review and fix them.")


if __name__ == "__main__":
    main()
