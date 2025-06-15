#!/usr/bin/env python3
"""
Targeted YAML syntax fix script for specific GitHub Actions workflow issues.
Addresses malformed multiline strings, escaped characters, and block mapping issues.
"""

import re
from pathlib import Path


def log(message: str, level: str = "INFO") -> None:
    """Log messages with level."""

def fix_multiline_strings(content: str) -> str:
    """Fix malformed multiline strings in YAML."""
    # Pattern 1: Fix malformed run commands with escaped characters
    # Look for patterns like: run: "source .venv/bin/activate\nif [ -f "fix_linting_issues.py" ]; then:\n..."

    # Fix escaped newlines and quotes in run commands
    content = re.sub(
        r'run:\s*"([^"]*(?:\\n|\\"|\\:|\\\s)[^"]*)"',
        lambda m: "run: |\n        " + m.group(1).replace("\\n", "\n        ").replace('\\"', '"').replace("\\:", ":").replace(r"\\s", " "),
        content,
        flags=re.MULTILINE | re.DOTALL
    )

    # Pattern 2: Fix malformed if conditions and blocks
    content = re.sub(
        r'if \[ -f "([^"]+)" \]; then:\s*\\:\s*\\\s*',
        r'if [ -f "\1" ]; then',
        content
    )

    # Pattern 3: Fix malformed else blocks
    content = re.sub(
        r'else:\s*echo "([^"]+)"\s*\\:\s*\\\s*',
        r'else\n          echo "\1"',
        content
    )

    # Pattern 4: Fix malformed fi statements
    content = re.sub(
        r'fi:\s*":\s*$',
        "fi",
        content,
        flags=re.MULTILINE
    )

    # Pattern 5: Fix malformed git status checks
    return re.sub(
        r'if \[\[ -n "\$\(git status --porcelain\)" \]\]; then\s*echo "changes=true"\s*\\\s*>> \$GITHUB_OUTPUT',
        'if [[ -n "$(git status --porcelain)" ]]; then\n          echo "changes=true" >> $GITHUB_OUTPUT',
        content
    )


def fix_yaml_structure(content: str) -> str:
    """Fix YAML structural issues."""
    # Fix malformed step definitions
    lines = content.split("\n")
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fix lines that end with colons followed by quotes
        if re.match(r'.*:\s*":\s*$', line):
            # Remove the malformed ending
            line = re.sub(r':\s*":\s*$', "", line)

        # Fix lines with escaped colons and backslashes
        if "\\:" in line or "\\\\" in line:
            line = line.replace("\\:", ":").replace("\\\\", "\\")

        # Fix malformed multiline indicators
        if line.strip().endswith("\\:"):
            line = line.replace("\\:", "")

        # Fix malformed quotes in run commands
        if "run:" in line and line.count('"') % 2 != 0:
            # Unmatched quotes, likely needs to be a multiline string
            if line.strip().startswith("run:") and '"' in line:
                # Convert to multiline format
                run_content = line.split("run:", 1)[1].strip().strip('"')
                indent = len(line) - len(line.lstrip())
                line = " " * indent + "run: |"
                fixed_lines.append(line)
                # Add the content with proper indentation
                if run_content:
                    fixed_lines.append(" " * (indent + 2) + run_content)
                i += 1
                continue

        fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)

def fix_specific_workflow_file(file_path: Path) -> bool:
    """Fix specific YAML issues in a workflow file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply fixes
        content = fix_multiline_strings(content)
        content = fix_yaml_structure(content)

        # Additional cleanup
        # Remove multiple consecutive empty lines
        content = re.sub(r"\n\n\n+", "\n\n", content)

        # Ensure file ends with newline
        if not content.endswith("\n"):
            content += "\n"

        # Only write if content changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            log(f"Fixed specific YAML issues in {file_path.name}")
            return True

        return False

    except Exception as e:
        log(f"Error fixing {file_path.name}: {e}", "ERROR")
        return False

def fix_problematic_files():
    """Fix the most problematic workflow files."""
    workflow_dir = Path(".github/workflows")

    # List of files that had specific issues
    problematic_files = [
        "auto-fix.yml",
        "codeql-fixed.yml",
        "codeql-macos-fixed.yml",
        "codeql-macos.yml",
        "codeql-ubuntu.yml",
        "codeql-windows-fixed.yml",
        "codeql-windows.yml",
        "codeql.yml",
        "consolidated-ci-cd-simplified.yml",
        "docker-compose-workflow.yml",
        "ensure-codeql-fixed.yml",
        "fix-workflow-issues.yml",
        "frontend-e2e.yml",
        "frontend-vitest.yml",
        "js-coverage.yml",
        "mcp-adapter-tests.yml",
        "mock-api-server.yml",
        "pr-166-simplified-working.yml",
        "pr-166-workflow-fixes.yml",
        "pr-trigger-fix.yml",
        "setup-pnpm.yml",
        "setup-uv.yml",
        "tailwind-build.yml",
        "test-setup-script-simplified.yml",
        "test-setup-script.yml"
    ]

    fixed_count = 0

    for filename in problematic_files:
        file_path = workflow_dir / filename
        if file_path.exists():
            if fix_specific_workflow_file(file_path):
                fixed_count += 1
        else:
            log(f"File not found: {filename}", "WARNING")

    log(f"Fixed specific issues in {fixed_count} files")
    return fixed_count > 0

def main() -> None:
    """Main function."""
    log("Targeted YAML Syntax Fix for GitHub Actions Workflows")
    log("=" * 60)

    success = fix_problematic_files()

    if success:
        log("\n✅ Applied targeted fixes to problematic workflow files")
        log("Run validation again to check remaining issues")
    else:
        log("\n⚠️  No files were modified")

    log("\nNext steps:")
    log("1. Run validation script again")
    log("2. Manually review any remaining issues")
    log("3. Test workflows in a feature branch")

if __name__ == "__main__":
    main()
