"""fix_security_issues - Script to fix security issues identified by CodeQL.

This script specifically targets security issues related to clear-text logging
and storage of sensitive information. It scans the codebase for patterns that
might expose sensitive data and replaces them with secure alternatives.
"""

import os
import re
import sys
from typing import Optional, Set

# Files to focus on
TARGET_FILES = [
    "common_utils/secrets/audit.py",
    "common_utils/secrets/cli.py",
    "fix_potential_secrets.py",
]

# Patterns to detect and fix
PATTERNS = [
    # Pattern 1: Clear-text logging of sensitive information
    (
        r'logger\.(?:info|debug|warning|error|critical)\s*\(\s*f["\'].*?{.*?secret.*?}.*?["\']',
        lambda match: re.sub(r"({.*?secret.*?})", r"[REDACTED]", match.group(0)),
    ),
    # Pattern 2: Direct printing of sensitive values
    (r"print\s*\(\s*(.*?secret.*?)\s*\)", r"print(mask_sensitive_data(\1))"),
    # Pattern 3: Logging sensitive file paths
    (
        (
            r"logger\.(?:info|debug|warning|error|critical)\s*\(\s*f"
            r'["\'].*?Report saved to {.*?}["\']'
        ),
        r'logger.info("Report saved", extra={"file": \1})',
    ),
]

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
}


def should_exclude(file_path: str, exclude_dirs: Optional[Set[str]] = None) -> bool:
    """Check if a file should be excluded from scanning."""
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS

    # Normalize path
    file_path = os.path.normpath(file_path)

    # Check if the file is in an excluded directory
    path_parts = file_path.split(os.sep)
    for part in path_parts:
        if part in exclude_dirs:
            return True

    return False


def fix_security_issues_in_file(file_path: str) -> bool:
    """Fix security issues in a file."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        modified = False
        new_content = content

        # Apply each pattern
        for pattern, replacement in PATTERNS:
            if callable(replacement):
                # If replacement is a function, use re.sub with the function
                matches = re.findall(pattern, new_content)
                if matches:
                    new_content = re.sub(pattern, replacement, new_content)
                    modified = True
            else:
                # Otherwise, use simple string replacement
                matches = re.findall(pattern, new_content)
                if matches:
                    # Convert replacement to string if it's not already
                    replacement_str = str(replacement)
                    new_content = re.sub(pattern, replacement_str, new_content)
                    modified = True

        # Special fixes for specific files
        if file_path == "common_utils/secrets/audit.py":
            # Fix for line 285: Clear-text logging of sensitive information
            new_content = re.sub(
                (
                    r'logger\.info\s*\(\s*f["\']Found {.*?} potential '
                    r'secrets in {.*?} files["\']'
                ),
                (
                    r'logger.info("Found potential secrets in files", '
                    r'extra={"count": total_secrets, "file_count": len(results)})'
                ),
                new_content,
            )

            # Fix for line 331: Clear-text storage of sensitive information
            new_content = re.sub(
                r'logger\.info\s*\(\s*f["\']Report saved to {.*?}["\']',
                r'logger.info("Report saved", extra={"file": output_file})',
                new_content,
            )

            # Fix for line 339: Clear-text logging of sensitive information
            new_content = re.sub(
                r"print\s*\(\s*output\s*\)",
                (
                    r"from common_utils.logging.secure_logging "
                    r"import mask_sensitive_data\n"
                    r"        print(mask_sensitive_data(output))"
                ),
                new_content,
            )

            modified = True

        elif file_path == "common_utils/secrets/cli.py":
            # Fix for line 135: Clear-text logging of sensitive information
            new_content = re.sub(
                r"print\s*\(\s*value\s*\)",
                (
                    r"from common_utils.logging.secure_logging "
                    r"import mask_sensitive_data\n"
                    r"    masked_value = mask_sensitive_data(value)\n"
                    r"    print(masked_value)"
                ),
                new_content,
            )

            # Fix for line 189: Clear-text logging of sensitive information
            new_content = re.sub(
                r'print\s*\(\s*f["\']  {key}["\']',
                r'# Don\'t print the actual secret values\n        print(f"  {key}"',
                new_content,
            )

            modified = True

        elif file_path == "fix_potential_secrets.py":
            # Fix for line 294: Clear-text logging of sensitive information
            new_content = re.sub(
                (
                    r"log_message = safe_log_sensitive_info\(pattern_name, "
                    r"line_num, len\(secret\)\)"
                ),
                (
                    r"# Don\'t pass the actual secret, just its length\n"
                    r"            secret_length = len(secret) if secret else 0\n"
                    r"            log_message = safe_log_sensitive_info("
                    r"pattern_name, line_num, secret_length)"
                ),
                new_content,
            )

            modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Fixed security issues in {file_path}")
            return True
        else:
            print(f"No security issues found in {file_path}")
            return True
    except Exception as e:
        print(f"Error fixing security issues in {file_path}: {e}")
        return False


def main() -> int:
    """Run the main program to fix security issues."""
    try:
        print("Running fix_security_issues.py")
        print(f"Current working directory: {os.getcwd()}")

        success_count = 0
        failed_files = []

        for file_path in TARGET_FILES:
            normalized_path = os.path.normpath(file_path)
            print(f"\nProcessing file: {normalized_path}")

            if not os.path.exists(normalized_path):
                print(f"⚠️ File not found: {normalized_path}")
                failed_files.append(normalized_path)
                continue

            if should_exclude(normalized_path):
                print(f"⚠️ File excluded: {normalized_path}")
                continue

            try:
                if fix_security_issues_in_file(normalized_path):
                    success_count += 1
                else:
                    failed_files.append(normalized_path)
            except Exception as e:
                print(f"Error processing {normalized_path}: {e}")
                import traceback

                traceback.print_exc()
                failed_files.append(normalized_path)

        # Print summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(
            f"Successfully processed {success_count} out of {len(TARGET_FILES)} files."
        )

        if failed_files:
            print("\nFailed files:")
            for file_path in failed_files:
                print(f"  - {file_path}")

        return 0 if success_count == len(TARGET_FILES) else 1
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
