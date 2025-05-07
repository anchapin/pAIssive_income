"""fix_security_issues - Script to scan for security issues in codebase.

This script scans for potential security issues related to clear-text logging
and storage of sensitive information. It outputs findings in SARIF format
for integration with GitHub Security features.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set

# Files to focus on
TARGET_FILES = [
    "common_utils/secrets/audit.py",
    "common_utils/secrets/cli.py",
    "fix_potential_secrets.py",
]

# Patterns to detect
PATTERNS = [
    # Pattern 1: Clear-text logging of sensitive information
    (
        r'logger\.(?:info|debug|warning|error|critical)\s*\(\s*f["\'].*?{.*?secret.*?}.*?["\']',
        "Clear-text logging of sensitive information",
        "warning",
    ),
    # Pattern 2: Direct printing of sensitive values
    (
        r"print\s*\(\s*(.*?secret.*?)\s*\)",
        "Direct printing of sensitive values",
        "error",
    ),
    # Pattern 3: Logging sensitive file paths
    (
        (
            r"logger\.(?:info|debug|warning|error|critical)\s*\(\s*f"
            r'["\'].*?Report saved to {.*?}["\']'
        ),
        "Logging sensitive file paths",
        "warning",
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


def scan_file_for_issues(file_path: str) -> List[Dict[str, Any]]:
    """Scan a file for security issues and return findings in SARIF format."""
    findings = []

    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
            lines = content.splitlines()

        # Apply each pattern
        for pattern, message, level in PATTERNS:
            for match in re.finditer(pattern, content):
                # Get line number
                line_num = content.count("\n", 0, match.start()) + 1

                # Get the matched line content
                matched_line = lines[line_num - 1]

                finding = {
                    "ruleId": f"security-check/{pattern[:30]}",
                    "level": level,
                    "message": {"text": message},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": file_path},
                                "region": {
                                    "startLine": line_num,
                                    "snippet": {"text": matched_line},
                                },
                            }
                        }
                    ],
                }
                findings.append(finding)

        # Special pattern checks for specific files
        if file_path == "common_utils/secrets/audit.py":
            # Check for line 285: Clear-text logging check
            pattern = (
                r'logger\.info\s*\(\s*f["\']Found {.*?} potential '
                r'secrets in {.*?} files["\']'
            )
            for match in re.finditer(pattern, content):
                line_num = content.count("\n", 0, match.start()) + 1
                msg = "Logging count of potential secrets without secure context"
                finding = {
                    "ruleId": ("security-check/clear-text-secrets-count"),
                    "level": "warning",
                    "message": {"text": msg},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": file_path},
                                "region": {
                                    "startLine": line_num,
                                    "snippet": {"text": lines[line_num - 1]},
                                },
                            }
                        }
                    ],
                }
                findings.append(finding)

    except Exception as e:
        print(f"Error scanning {file_path}: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        findings.append(
            {
                "ruleId": "security-check/scan-error",
                "level": "error",
                "message": {"text": f"Error scanning file: {str(e)}"},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": file_path},
                            "region": {"startLine": 1},
                        }
                    }
                ],
            }
        )

    return findings


def create_sarif_report(findings: List[Dict[str, Any]], output_file: str):
    """Create a SARIF format report from the findings."""
    sarif_report = {
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs/"
            "sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
        ),
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Security Issue Scanner",
                        "rules": [
                            {
                                "id": "security-check/clear-text-logging",
                                "shortDescription": {
                                    "text": (
                                        "Clear-text logging of sensitive information"
                                    )
                                },
                                "fullDescription": {
                                    "text": (
                                        "Logging sensitive information in "
                                        "clear text can expose secrets"
                                    )
                                },
                                "defaultConfiguration": {"level": "warning"},
                            }
                        ],
                    }
                },
                "results": findings,
            }
        ],
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sarif_report, f, indent=2)


def main() -> int:
    """Run the main program to scan for security issues."""
    parser = argparse.ArgumentParser(description="Scan for security issues in code")
    parser.add_argument(
        "--scan-only", action="store_true", help="Only scan for issues without fixing"
    )
    parser.add_argument(
        "--output", help="Output file for SARIF report", default="security-report.sarif"
    )
    args = parser.parse_args()

    try:
        print("Running security issue scanner...")
        print(f"Current working directory: {os.getcwd()}")

        all_findings = []
        failed_files = []

        for file_path in TARGET_FILES:
            normalized_path = os.path.normpath(file_path)
            print(f"\nScanning file: {normalized_path}")

            if not os.path.exists(normalized_path):
                print(f"⚠️ File not found: {normalized_path}")
                failed_files.append(normalized_path)
                continue

            if should_exclude(normalized_path):
                print(f"⚠️ File excluded: {normalized_path}")
                continue

            try:
                findings = scan_file_for_issues(normalized_path)
                all_findings.extend(findings)

                if findings:
                    print(f"Found {len(findings)} potential issues")
                else:
                    print("No security issues found")

            except Exception as e:
                print(f"Error processing {normalized_path}: {e}")
                import traceback

                traceback.print_exc()
                failed_files.append(normalized_path)

        # Create SARIF report
        create_sarif_report(all_findings, args.output)
        print(f"\nSARIF report saved to {args.output}")

        # Print summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Scanned {len(TARGET_FILES)} files")
        print(f"Found {len(all_findings)} potential security issues")

        if failed_files:
            print("\nFailed files:")
            for file_path in failed_files:
                print(f"  - {file_path}")
            return 1

        return 0 if not all_findings else 1  # Exit with 1 if issues found

    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
