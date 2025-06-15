#!/usr/bin/env python3
"""
Comprehensive YAML syntax fix script for GitHub Actions workflows.
Addresses specific parsing errors found in workflow validation.
"""

import re
from pathlib import Path
from typing import Tuple

import yaml


def log(message: str, level: str = "INFO") -> None:
    """Log messages with level."""

def fix_yaml_file(file_path: Path) -> bool:
    """Fix YAML syntax errors in a specific file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix 1: Remove duplicate 'on:' sections and malformed triggers
        lines = content.split("\n")
        fixed_lines = []
        skip_until_next_section = False
        in_on_section = False
        on_section_found = False

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith("#"):
                fixed_lines.append(line)
                i += 1
                continue

            # Handle 'on:' sections
            if stripped in {"on:", "'on':", '"on":'}:
                if on_section_found:
                    # This is a duplicate, skip it and everything until next top-level section
                    skip_until_next_section = True
                    i += 1
                    continue
                fixed_lines.append("on:")
                on_section_found = True
                in_on_section = True
                i += 1
                continue

            # Check if we're starting a new top-level section
            if not line.startswith(" ") and not line.startswith("\t") and ":" in line:
                skip_until_next_section = False
                in_on_section = False

            # Skip lines if we're in a duplicate section
            if skip_until_next_section:
                i += 1
                continue

            # Fix malformed YAML structures
            if in_on_section:
                # Fix common on: section issues
                if "true:" in stripped:
                    # Skip malformed true: entries
                    i += 1
                    continue

                # Fix push/pull_request sections
                if stripped in ["push:", "pull_request:", "schedule:", "workflow_dispatch:"]:
                    fixed_lines.append(f"  {stripped}")
                    i += 1
                    continue

                # Fix branches/paths indentation
                if stripped.startswith(("branches:", "paths:")):
                    if not line.startswith("    "):
                        fixed_lines.append(f"    {stripped}")
                    else:
                        fixed_lines.append(line)
                    i += 1
                    continue

                # Fix list items in on: section
                if stripped.startswith("- "):
                    if not line.startswith("      "):
                        fixed_lines.append(f"      {stripped}")
                    else:
                        fixed_lines.append(line)
                    i += 1
                    continue

            # Fix multiline string issues
            if "|" in line and not line.strip().endswith("|"):
                # Ensure proper multiline string formatting
                parts = line.split("|")
                if len(parts) == 2:
                    fixed_lines.append(f"{parts[0]}|")
                    # Handle the content after |
                    remaining = parts[1].strip()
                    if remaining:
                        # Add the remaining content as a new line with proper indentation
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.append(" " * (indent + 2) + remaining)
                else:
                    fixed_lines.append(line)
                i += 1
                continue

            # Fix escaped characters in strings
            if "\\n" in line:
                line = line.replace("\\n", "\n")
            if '\\"' in line:
                line = line.replace('\\"', '"')

            # Fix malformed step names and run commands
            if stripped.startswith("- name:") and "run:" in stripped:
                # Split name and run into separate lines
                parts = stripped.split("run:", 1)
                if len(parts) == 2:
                    name_part = parts[0].strip()
                    run_part = parts[1].strip()
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(" " * indent + name_part)
                    fixed_lines.append(" " * (indent + 2) + f"run: {run_part}")
                else:
                    fixed_lines.append(line)
                i += 1
                continue

            # Fix missing colons in key-value pairs
            if not line.startswith(" ") and not line.startswith("\t") and line.strip() and ":" not in line and "=" not in line:
                # This might be a key without a colon
                if not line.strip().startswith("-"):
                    line = line.strip() + ":"

            fixed_lines.append(line)
            i += 1

        content = "\n".join(fixed_lines)

        # Additional fixes for common YAML issues

        # Fix: Remove trailing spaces that can cause issues
        content = re.sub(r" +\n", "\n", content)

        # Fix: Ensure proper spacing around colons
        content = re.sub(r"(\w):(\w)", r"\1: \2", content)

        # Fix: Remove multiple consecutive empty lines
        content = re.sub(r"\n\n\n+", "\n\n", content)

        # Fix: Ensure file ends with newline
        if not content.endswith("\n"):
            content += "\n"

        # Only write if content changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            log(f"Fixed YAML syntax in {file_path.name}")
            return True

        return False

    except Exception as e:
        log(f"Error fixing {file_path.name}: {e}", "ERROR")
        return False

def validate_yaml_file(file_path: Path) -> Tuple[bool, str]:
    """Validate a YAML file and return (is_valid, error_message)."""
    try:
        with open(file_path, encoding="utf-8") as f:
            yaml.safe_load(f)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error reading file: {e}"

def fix_all_workflows():
    """Fix all workflow files in .github/workflows/."""
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        log("Workflow directory not found", "ERROR")
        return False

    log("Starting comprehensive YAML syntax fixes...")

    # Get all YAML files
    yaml_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    if not yaml_files:
        log("No YAML files found", "WARNING")
        return False

    fixed_count = 0
    total_count = len(yaml_files)

    # First pass: Fix syntax errors
    for yaml_file in yaml_files:
        if fix_yaml_file(yaml_file):
            fixed_count += 1

    log(f"Fixed syntax in {fixed_count}/{total_count} files")

    # Second pass: Validate all files
    valid_count = 0
    invalid_files = []

    for yaml_file in yaml_files:
        is_valid, error = validate_yaml_file(yaml_file)
        if is_valid:
            valid_count += 1
            log(f"✅ Valid: {yaml_file.name}")
        else:
            invalid_files.append((yaml_file.name, error))
            log(f"❌ Invalid: {yaml_file.name} - {error[:100]}...", "ERROR")

    log(f"\nValidation Summary: {valid_count}/{total_count} files are valid")

    if invalid_files:
        log("\nRemaining issues:", "WARNING")
        for filename, error in invalid_files[:5]:  # Show first 5 errors
            log(f"  {filename}: {error[:150]}...", "WARNING")
        if len(invalid_files) > 5:
            log(f"  ... and {len(invalid_files) - 5} more files with errors", "WARNING")

    return valid_count == total_count

def main() -> None:
    """Main function."""
    log("GitHub Actions Workflow YAML Syntax Fixer")
    log("=" * 50)

    success = fix_all_workflows()

    if success:
        log("\n🎉 All workflow files are now valid!")
    else:
        log("\n⚠️  Some files still have issues. Manual review may be needed.")

    log("\nNext steps:")
    log("1. Review any remaining invalid files")
    log("2. Test workflows in a feature branch")
    log("3. Commit the fixes")

if __name__ == "__main__":
    main()
