#!/usr/bin/env python3
"""
Fix GitHub Actions workflow syntax errors.

This script fixes the common issue where workflow files have "true:" instead of "on:"
at the beginning, which causes workflow failures.
"""

from pathlib import Path


def fix_workflow_file(file_path):
    """Fix a single workflow file by replacing 'true:' with 'on:' at the beginning."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if the file starts with 'true:' (possibly after name declaration)
        lines = content.split("\n")
        fixed = False

        for i, line in enumerate(lines):
            # Look for lines that are exactly 'true:' or start with 'true:'
            if line.strip() == "true:":
                lines[i] = "on:"
                fixed = True
                print(f"Fixed line {i + 1} in {file_path}: '{line.strip()}' -> 'on:'")
                break
            if line.startswith("true:"):
                # Handle cases where there might be content after 'true:'
                lines[i] = line.replace("true:", "on:", 1)
                fixed = True
                print(f"Fixed line {i + 1} in {file_path}: '{line}' -> '{lines[i]}'")
                break

        if fixed:
            # Write the fixed content back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"✅ Successfully fixed {file_path}")
            return True
        print(f"ℹ️  No 'true:' found in {file_path}")
        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix all workflow files."""
    print("🔧 Fixing GitHub Actions workflow syntax errors...")

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
        print("\n🎉 Workflow syntax errors have been fixed!")
        print(
            "💡 You can now commit these changes and your workflows should work properly."
        )
    else:
        print("\n✅ All workflow files appear to have correct syntax already.")


if __name__ == "__main__":
    main()
