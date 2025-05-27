#!/usr/bin/env python3
"""
Fix comprehensive GitHub Actions workflow issues.

This script fixes multiple common issues in workflow files:
1. Malformed pip install commands with repeated pytest and incorrect flags
2. Duplicate Node.js setup steps
3. Other syntax and configuration issues
"""

import re
from pathlib import Path


def fix_malformed_pip_install(content):
    """Fix malformed pip install commands."""
    # Fix the specific malformed command with repeated pytest and incorrect flags
    malformed_pattern = r"python -m pip install ruff pyrefly pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py-cov pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py-xdist pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py-asyncio"

    # Replace with correct command
    correct_command = "python -m pip install ruff pyrefly pytest pytest-cov pytest-xdist pytest-asyncio"

    if malformed_pattern in content:
        content = content.replace(malformed_pattern, correct_command)
        return content, True

    # Also fix similar patterns with different variations
    patterns_to_fix = [
        (
            r"pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py-cov pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py-xdist pytest --ignore=tests/test_mcp_import\.py --ignore=tests/test_mcp_top_level_import\.py-asyncio",
            "pytest pytest-cov pytest-xdist pytest-asyncio",
        ),
    ]

    fixed = False
    for pattern, replacement in patterns_to_fix:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixed = True

    return content, fixed


def fix_duplicate_nodejs_setup(content):
    """Fix duplicate Node.js setup steps."""
    lines = content.split("\n")
    nodejs_setup_indices = []

    for i, line in enumerate(lines):
        if "name: Set up Node.js" in line:
            nodejs_setup_indices.append(i)

    if len(nodejs_setup_indices) > 1:
        # Remove duplicate Node.js setup steps (keep the first one)
        lines_to_remove = []
        for idx in nodejs_setup_indices[1:]:
            # Find the end of this step (next step or end of job)
            step_end = len(lines)
            for j in range(idx + 1, len(lines)):
                if lines[j].strip().startswith("- name:") or lines[
                    j
                ].strip().startswith("jobs:"):
                    step_end = j
                    break

            # Mark lines for removal
            for k in range(idx, step_end):
                lines_to_remove.append(k)

        # Remove lines in reverse order to maintain indices
        for idx in sorted(lines_to_remove, reverse=True):
            lines.pop(idx)

        return "\n".join(lines), True

    return content, False


def fix_workflow_dispatch_null(content):
    """Fix workflow_dispatch: null to workflow_dispatch: {}"""
    if "workflow_dispatch: null" in content:
        content = content.replace("workflow_dispatch: null", "workflow_dispatch: {}")
        return content, True
    return content, False


def fix_workflow_file(file_path):
    """Fix a single workflow file comprehensively."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        fixes_applied = []

        # Apply all fixes
        content, fixed1 = fix_malformed_pip_install(content)
        if fixed1:
            fixes_applied.append("malformed pip install commands")

        content, fixed2 = fix_duplicate_nodejs_setup(content)
        if fixed2:
            fixes_applied.append("duplicate Node.js setup steps")

        content, fixed3 = fix_workflow_dispatch_null(content)
        if fixed3:
            fixes_applied.append("workflow_dispatch null value")

        if fixes_applied:
            # Write the fixed content back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Fixed {file_path}: {', '.join(fixes_applied)}")
            return True
        print(f"ℹ️  No issues found in {file_path}")
        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix all workflow files."""
    print("🔧 Fixing comprehensive GitHub Actions workflow issues...")

    # Find all YAML files in .github/workflows/
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print(f"❌ Workflow directory {workflow_dir} not found!")
        return

    yaml_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    if not yaml_files:
        print("❌ No YAML workflow files found!")
        return

    print(f"📁 Found {len(yaml_files)} workflow files to check...")

    fixed_count = 0
    for yaml_file in yaml_files:
        print(f"\n🔍 Checking {yaml_file}...")
        if fix_workflow_file(yaml_file):
            fixed_count += 1

    print(f"\n✨ Summary: Fixed {fixed_count} out of {len(yaml_files)} workflow files")

    if fixed_count > 0:
        print("\n🎉 Comprehensive workflow issues have been fixed!")
        print(
            "💡 You can now commit these changes and your workflows should work properly."
        )
    else:
        print("\n✅ All workflow files appear to be correct already.")


if __name__ == "__main__":
    main()
