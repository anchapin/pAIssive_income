#!/usr/bin/env python3
"""Security issues scanner and fixer for CI/CD.

This script is designed to be run in CI/CD workflows to scan for
security issues and generate reports in a standardized format.
It's a wrapper around the fix_potential_secrets.py script with
additional CI-friendly features.
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Set, cast

# Import the existing security tools if possible
try:
    from fix_potential_secrets import (
        scan_directory as scan_directory_for_secrets,
    )

    IMPORTED_SECRET_SCANNER = True
except ImportError:
    IMPORTED_SECRET_SCANNER = False


def setup_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments

    """
    parser = argparse.ArgumentParser(
        description="Security issues scanner and fixer for CI/CD"
    )
    parser.add_argument(
        "--scan-only", action="store_true", help="Only scan for issues, don't fix them"
    )
    parser.add_argument(
        "--output",
        default="security-report.sarif",
        help="Output file for the report (default: security-report.sarif)",
    )
    parser.add_argument(
        "--directory",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["sarif", "json", "text"],
        default="sarif",
        help="Output format (default: sarif)",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[
            ".git",
            ".github",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "build",
            "dist",
            ".pytest_cache",
        ],
        help="Directories to exclude from scanning",
    )

    return parser.parse_args()


def run_security_scan(directory: str, exclude_dirs: Set[str]) -> Dict[str, Any]:
    """Run the security scan using the appropriate tool.

    Args:
        directory: Directory to scan
        exclude_dirs: Directories to exclude

    Returns:
        Dict[str, Any]: Results of the scan

    """
    print(f"Scanning directory: {directory}")
    print(f"Excluding directories: {', '.join(exclude_dirs)}")

    # Use imported function if available
    if IMPORTED_SECRET_SCANNER:
        results = scan_directory_for_secrets(directory)
        return results

    # Fallback to subprocess call
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), "fix_potential_secrets.py"
        )

        # Check if the script exists
        if not os.path.exists(script_path):
            # Try relative path
            script_path = "fix_potential_secrets.py"
            if not os.path.exists(script_path):
                raise FileNotFoundError(
                    "Could not find fix_potential_secrets.py in current directory "
                    "or parent directory"
                )

        # Call the script using subprocess
        exclude_arg = ",".join(exclude_dirs)
        cmd = [
            sys.executable,
            script_path,
            directory,
            "--scan-only",
            f"--exclude={exclude_arg}",
        ]

        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Extract results from script output
        # This assumes fix_potential_secrets.py outputs a JSON report
        if result.stdout and result.returncode == 0:
            # Try to parse JSON from output
            try:
                # Find JSON in output (assuming it's delimited somehow)
                json_start = result.stdout.find("{")
                if json_start >= 0:
                    results = json.loads(result.stdout[json_start:])
                    return results
            except json.JSONDecodeError:
                pass

        # If we can't parse the output, return a simplified result
        print("Could not parse detailed results, returning simplified report")
        return {"error": "Could not parse output from security scanner"}

    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error running security scan: {e}")
        return {"error": f"Error running security scan: {type(e).__name__}"}


def generate_sarif_report(results: Dict[str, Any], output_file: str) -> None:
    """Generate a SARIF report from scan results.

    Args:
        results: Scan results
        output_file: Output file path

    """
    # Build URL in parts to avoid line length issues
    base = "https://raw.githubusercontent.com/"
    org = "oasis-tcs/sarif-spec/"
    path = "master/Schemata/sarif-schema-2.1.0.json"
    schema_url = base + org + path

    # Configure SARIF report
    sarif_report: Dict[str, Any] = {
        "$schema": schema_url,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SecretScanner",
                        "informationUri": "https://github.com/anchapin/pAIssive_income",
                        "rules": [
                            {
                                "id": "secret-detection",
                                "shortDescription": {
                                    "text": "Detect hardcoded secrets"
                                },
                                "fullDescription": {
                                    "text": "Identifies hardcoded credentials, tokens, "
                                    "and other secrets in code"
                                },
                                "helpUri": "https://github.com/anchapin/pAIssive_income",
                                "defaultConfiguration": {"level": "error"},
                            }
                        ],
                    }
                },
                "results": [],
            }
        ],
    }

    # Add results to SARIF report without including sensitive data
    sarif_results = cast(List[Dict[str, Any]], sarif_report["runs"][0]["results"])

    for file_path, secrets in results.items():
        if isinstance(secrets, list):
            for item in secrets:
                if isinstance(item, tuple) and len(item) >= 2:
                    # Handle tuple format (pattern_name, line_num, line, secret_value)
                    pattern_name, line_num = item[0], item[1]
                    sarif_results.append(
                        {
                            "ruleId": "secret-detection",
                            "level": "error",
                            "message": {"text": f"Potential {pattern_name} found"},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": file_path},
                                        "region": {"startLine": line_num},
                                    }
                                }
                            ],
                        }
                    )
                elif (
                    isinstance(item, dict) and "type" in item and "line_number" in item
                ):
                    # Handle dict format from JSON
                    pattern_name, line_num = item["type"], item["line_number"]
                    sarif_results.append(
                        {
                            "ruleId": "secret-detection",
                            "level": "error",
                            "message": {"text": f"Potential {pattern_name} found"},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": file_path},
                                        "region": {"startLine": line_num},
                                    }
                                }
                            ],
                        }
                    )

    try:
        with open(output_file, "w") as f:
            json.dump(sarif_report, f, indent=2)
        print(f"SARIF report saved to {output_file}")
    except Exception as e:
        # Don't log the exception details as they might include sensitive information
        print(f"Error writing SARIF report: {type(e).__name__}")
        sys.exit(1)


def main() -> int:
    """Execute the main program functionality.

    Returns:
        int: Exit code

    """
    args = setup_args()

    # Convert excluded directories to a set
    exclude_dirs = set(args.exclude)

    # Run the security scan
    results = run_security_scan(args.directory, exclude_dirs)

    # Check if there are any results
    if not results or (isinstance(results, dict) and not results):
        print("No security issues found.")
        return 0

    # Count issues found
    issue_count = 0
    if isinstance(results, dict):
        for _file_path, secrets in results.items():
            if isinstance(secrets, list):
                issue_count += len(secrets)

    print(f"Found {issue_count} potential security issues.")

    # Generate the report
    if args.format == "sarif":
        generate_sarif_report(results, args.output)
    elif args.format == "json":
        try:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"JSON report saved to {args.output}")
        except Exception as e:
            print(f"Error writing JSON report: {type(e).__name__}")
            return 1
    else:  # text format
        try:
            with open(args.output, "w") as f:
                for file_path, secrets in results.items():
                    f.write(f"File: {file_path}\n")
                    f.write("-" * (len(file_path) + 6) + "\n")
                    if isinstance(secrets, list):
                        for item in secrets:
                            if isinstance(item, tuple) and len(item) >= 2:
                                pattern_name, line_num = item[0], item[1]
                                f.write(f"  Line {line_num}: {pattern_name} found\n")
                            elif (
                                isinstance(item, dict)
                                and "type" in item
                                and "line_number" in item
                            ):
                                pattern_name, line_num = (
                                    item["type"],
                                    item["line_number"],
                                )
                                f.write(f"  Line {line_num}: {pattern_name} found\n")
                    f.write("\n")
            print(f"Text report saved to {args.output}")
        except Exception as e:
            print(f"Error writing text report: {type(e).__name__}")
            return 1

    # Return success if scan-only, otherwise return appropriate status for fixing
    if args.scan_only:
        return 0

    # Return non-zero if issues were found to signal that fixes are needed
    return 0 if issue_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
