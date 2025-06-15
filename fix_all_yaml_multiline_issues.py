#!/usr/bin/env python3
"""Comprehensive fix for all YAML multiline string and syntax issues in GitHub Actions workflows."""
from __future__ import annotations

import re
from pathlib import Path

import yaml


def log(message: str, level: str = "INFO") -> None:
    """Log messages with level."""

def fix_multiline_run_commands(content: str) -> str:
    """Fix malformed multiline run commands."""
    # Pattern 1: Fix run commands with escaped newlines and backslashes
    # Example: run: 'command1\n\ncommand2\n\n'
    content = re.sub(
        r"run:\s*'([^']*(?:\\n|\\\\)[^']*)'",
        lambda m: "run: |\n        " + m.group(1).replace("\\n", "\n        ").replace("\\\\", "\\"),
        content,
        flags=re.MULTILINE
    )

    # Pattern 2: Fix run commands with escaped quotes and newlines
    # Example: run: "command1\ncommand2"
    return re.sub(
        r'run:\s*"([^"]*(?:\\n|\\"|\\\s)[^"]*)"',
        lambda m: "run: |\n        " + m.group(1).replace("\\n", "\n        ").replace('\\"', '"').replace(r"\\s", " "),
        content,
        flags=re.MULTILINE
    )


def fix_malformed_yaml_blocks(content: str) -> str:
    """Fix malformed YAML blocks and structures."""
    lines = content.split("\n")
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Fix malformed if-then-else blocks
        if "if [ -f" in line and "; then" in line and line.endswith("then"):
            # This is likely a malformed if statement
            len(line) - len(line.lstrip())
            fixed_lines.append(line)
            i += 1
            continue

        # Fix lines with escaped backslashes and colons
        if "\\:" in line or "\\\\" in line:
            line = line.replace("\\:", ":").replace("\\\\", "\\")

        # Fix malformed echo statements with line continuations
        if 'echo "' in line and "\\\n" in line:
            # Remove line continuation artifacts
            line = re.sub(r"\\\s*\n\s*\\", " ", line)

        # Fix malformed fi statements
        if stripped in {"fi:", 'fi:"'}:
            line = line.replace("fi:", "fi").replace('fi:"', "fi")

        # Fix malformed else statements
        if stripped == "else:":
            line = line.replace("else:", "else")

        # Fix lines ending with ": followed by quotes
        if re.match(r'.*:\s*":\s*$', line):
            line = re.sub(r':\s*":\s*$', "", line)

        # Fix malformed multiline indicators
        if line.strip().endswith("\\:"):
            line = line.replace("\\:", "")

        fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)

def fix_path_multiline_strings(content: str) -> str:
    """Fix multiline path strings in workflow triggers."""
    # Fix path sections with escaped newlines
    return re.sub(
        r"path:\s*'([^']*\\n[^']*)'",
        lambda m: "path:\n          " + "\n          ".join(m.group(1).replace("\\n", "").split()),
        content
    )


def fix_workflow_file(file_path: Path) -> bool:
    """Fix a single workflow file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply all fixes
        content = fix_multiline_run_commands(content)
        content = fix_malformed_yaml_blocks(content)
        content = fix_path_multiline_strings(content)

        # Additional cleanup
        # Remove trailing spaces
        content = re.sub(r" +\n", "\n", content)

        # Fix multiple consecutive empty lines
        content = re.sub(r"\n\n\n+", "\n\n", content)

        # Ensure file ends with newline
        if not content.endswith("\n"):
            content += "\n"

        # Only write if content changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            log(f"Fixed YAML issues in {file_path.name}")
            return True

        return False

    except Exception as e:
        log(f"Error fixing {file_path.name}: {e}", "ERROR")
        return False

def validate_yaml_file(file_path: Path) -> tuple[bool, str]:
    """Validate a YAML file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            yaml.safe_load(f)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error reading file: {e}"

def fix_all_workflows():
    """Fix all workflow files."""
    workflow_dir = Path(".github/workflows")

    if not workflow_dir.exists():
        log("Workflow directory not found", "ERROR")
        return False

    yaml_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    if not yaml_files:
        log("No YAML files found", "WARNING")
        return False

    log(f"Processing {len(yaml_files)} workflow files...")

    fixed_count = 0

    # Fix all files
    for yaml_file in yaml_files:
        if fix_workflow_file(yaml_file):
            fixed_count += 1

    log(f"Fixed issues in {fixed_count} files")

    # Validate all files
    valid_count = 0
    invalid_files = []

    for yaml_file in yaml_files:
        is_valid, error = validate_yaml_file(yaml_file)
        if is_valid:
            valid_count += 1
        else:
            invalid_files.append((yaml_file.name, error))

    log(f"Validation: {valid_count}/{len(yaml_files)} files are valid")

    if invalid_files:
        log("Remaining invalid files:", "WARNING")
        for filename, error in invalid_files[:10]:  # Show first 10
            log(f"  {filename}: {error[:100]}...", "WARNING")

    return len(invalid_files) == 0

def main() -> None:
    """Main function."""
    log("Comprehensive YAML Workflow Fix")
    log("=" * 40)

    success = fix_all_workflows()

    if success:
        log("\n🎉 All workflow files are now valid!")
    else:
        log("\n⚠️  Some files still have issues")

    log("\nRecommendations:")
    log("1. Review any remaining invalid files manually")
    log("2. Test workflows in a feature branch")
    log("3. Consider simplifying complex workflows")

if __name__ == "__main__":
    main()
