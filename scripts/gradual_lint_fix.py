#!/usr/bin/env python3
"""
Gradual Lint Fix Strategy Script.

This script implements a gradual approach to fixing linting issues:
1. For PRs: Only lint changed files
2. For main branch: Track progress and gradually expand coverage
3. Provides tools to systematically fix existing issues
4. Supports critical-only mode for large PRs.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Critical error codes that could break functionality
CRITICAL_ERROR_CODES = [
    "E9",  # Runtime errors (syntax errors, etc.)
    "F63",  # Invalid print statement
    "F7",  # Syntax errors in type comments
    "F82",  # Undefined name in __all__
    "F821",  # Undefined name
    "F822",  # Undefined name in __all__
    "F831",  # Local variable assigned but never used
    "E999",  # Syntax error
    "W605",  # Invalid escape sequence
]


def _find_executable(name: str) -> str:
    """Return the full path to an executable, or the name if not found."""
    path = shutil.which(name)
    return path if path else name


def get_changed_files(base_branch: str = "main") -> list[str]:
    """Get list of Python files changed compared to base branch."""
    try:
        git_path = _find_executable("git")
        result = subprocess.run(
            [git_path, "diff", "--name-only", f"origin/{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            # errors="ignore" is used to avoid UnicodeDecodeError when reading subprocess output, safe in this context.
            errors="ignore",
            check=True,
        )
        changed_files = [
            line.strip()
            for line in result.stdout.strip().split("\n")
            if line.strip().endswith(".py") and Path(line.strip()).exists()
        ]
    except subprocess.CalledProcessError:
        print("Warning: Could not get changed files from git. Checking all files.")
    else:
        return changed_files
    return []


def run_ruff_on_files(
    files: list[str], fix: bool = False, critical_only: bool = False
) -> dict[str, int]:
    """Run ruff on specific files and return error counts."""
    if not files:
        return {}
    results = {}
    ruff_path = _find_executable("ruff")
    for file in files:
        cmd = [ruff_path, "check", file]
        if fix:
            cmd.append("--fix")
        if critical_only:
            select_codes = ",".join(CRITICAL_ERROR_CODES)
            cmd.extend(["--select", select_codes])
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                # errors="ignore" is used to avoid UnicodeDecodeError when reading subprocess output, safe in this context.
                errors="ignore",
                check=False,
            )
        except subprocess.CalledProcessError as e:
            print(f"\u274c Error checking {file}: {e}")
            results[file] = -1
            continue
        if result.stdout:
            error_count = len(
                [line for line in result.stdout.strip().split("\n") if line.strip()]
            )
        else:
            error_count = 0
        results[file] = error_count
        if error_count > 0:
            print(f"\U0001f4c1 {file}: {error_count} issues")
            if not fix and result.stdout:
                print(result.stdout)
        else:
            print(f"\u2705 {file}: Clean")
    return results


def get_baseline_errors() -> dict[str, int]:
    """Get current error count for all files to establish baseline."""
    try:
        ruff_path = _find_executable("ruff")
        result = subprocess.run(
            [ruff_path, "check", ".", "--output-format=concise"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            # errors="ignore" is used to avoid UnicodeDecodeError when reading subprocess output, safe in this context.
            errors="ignore",
            check=False,
        )
        if result.stdout and result.stdout.strip():
            file_counts = {}
            for line in result.stdout.strip().split("\n"):
                if line.strip() and ":" in line:
                    filename = line.split(":")[0]
                    if filename in file_counts:
                        file_counts[filename] += 1
                    else:
                        file_counts[filename] = 1
            return file_counts
        return {}
    except subprocess.CalledProcessError:
        print("Warning: Could not get baseline error counts")
        return {}
    else:
        return file_counts


def save_baseline(
    baseline: dict[str, int], filename: str = "lint_baseline.json"
) -> None:
    """Save baseline error counts to file."""
    baseline_file = Path(filename)
    with baseline_file.open("w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    print(f"\U0001f4be Baseline saved to {baseline_file}")


def load_baseline(filename: str = "lint_baseline.json") -> dict[str, int]:
    """Load baseline error counts from file."""
    baseline_file = Path(filename)
    if baseline_file.exists():
        with baseline_file.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def _print_progress_report(
    improved_files: list[str],
    regressed_files: list[str],
    new_files: list[str],
    fixed_files: list[str],
    baseline: dict,
    current_errors: dict,
) -> None:
    print("\U0001f4c8 Progress Report:")
    print(f"  \u2705 Files completely fixed: {len(fixed_files)}")
    print(f"  \U0001f4c8 Files improved: {len(improved_files)}")
    print(f"  \U0001f53a Files regressed: {len(regressed_files)}")
    print(f"  \U0001f195 New files with issues: {len(new_files)}")
    if improved_files:
        print("\n\U0001f389 Improved files:")
        for filename, improvement in improved_files:
            print(f"  - {filename}: -{improvement} errors")
    if regressed_files:
        print("\n\u26a0\ufe0f  Regressed files:")
        for filename, regression in regressed_files:
            print(f"  - {filename}: +{regression} errors")
    total_baseline = sum(baseline.values())
    total_current = sum(current_errors.values())
    if total_current <= total_baseline:
        print(
            f"\n\U0001f4ca Overall progress: {total_baseline} -> {total_current} errors ({total_baseline - total_current:+d})"
        )
    else:
        print(
            f"\n\U0001f4ca Overall regression: {total_baseline} -> {total_current} errors ({total_current - total_baseline:+d})"
        )


def check_progress_mode() -> int:
    """Check progress against baseline."""
    print("\U0001f4ca Running in progress mode - checking against baseline...")
    baseline = load_baseline()
    if not baseline:
        print("\U0001f4cb No baseline found. Creating new baseline...")
        current_errors = get_baseline_errors()
        save_baseline(current_errors)
        total_errors = sum(current_errors.values())
        print(
            f"\U0001f4ca Baseline established: {total_errors} total errors across {len(current_errors)} files"
        )
        return 0
    current_errors = get_baseline_errors()
    improved_files = []
    regressed_files = []
    new_files = []
    for filename, current_count in current_errors.items():
        baseline_count = baseline.get(filename, 0)
        if current_count < baseline_count:
            improved_files.append((filename, baseline_count - current_count))
        elif current_count > baseline_count:
            regressed_files.append((filename, current_count - baseline_count))
        elif filename not in baseline:
            new_files.append((filename, current_count))
    fixed_files = [f for f in baseline if f not in current_errors]
    _print_progress_report(
        improved_files,
        regressed_files,
        new_files,
        fixed_files,
        baseline,
        current_errors,
    )
    total_baseline = sum(baseline.values())
    total_current = sum(current_errors.values())
    if total_current <= total_baseline:
        save_baseline(current_errors)
        return 0
    return 1


def check_pr_mode(
    base_branch: str = "main",
    fix: bool = False,
    critical_only: bool = False,
) -> int:
    """Check only changed files in PR mode."""
    mode_desc = "critical errors only" if critical_only else "all linting issues"
    print(f"\U0001f50d Running in PR mode - checking {mode_desc} in changed files...")
    changed_files = get_changed_files(base_branch)
    if not changed_files:
        print("\u2705 No Python files changed or could not detect changes.")
        return 0
    print(f"\U0001f4dd Found {len(changed_files)} changed Python files:")
    for file in changed_files:
        print(f"  - {file}")
    results = run_ruff_on_files(changed_files, fix=fix, critical_only=critical_only)
    total_errors = sum(count for count in results.values() if count > 0)
    if total_errors == 0:
        success_msg = "critical checks" if critical_only else "linting checks"
        print(f"\u2705 All changed files pass {success_msg}!")
        return 0
    error_type = "critical issues" if critical_only else "linting issues"
    print(f"\u274c Found {total_errors} {error_type} in changed files.")
    if not fix:
        print("\U0001f4a1 Run with --fix to automatically fix issues, or fix manually.")
    if critical_only:
        return 1
    return 1


def fix_top_files(count: int = 5) -> int:
    """Fix the files with the most errors."""
    print(f"\U0001f527 Fixing top {count} files with most errors...")
    current_errors = get_baseline_errors()
    if not current_errors:
        print("\u2705 No errors found!")
        return 0
    sorted_files = sorted(current_errors.items(), key=lambda x: x[1], reverse=True)
    top_files = [filename for filename, _ in sorted_files[:count]]
    print("\U0001f3af Targeting files:")
    for i, (filename, error_count) in enumerate(sorted_files[:count], 1):
        print(f"  {i}. {filename}: {error_count} errors")
    results = run_ruff_on_files(top_files, fix=True)
    fixed_count = sum(1 for count in results.values() if count == 0)
    print(f"\n\u2705 Successfully fixed {fixed_count}/{len(top_files)} files")
    return 0


def main() -> int:
    """Run gradual lint fix strategy."""
    parser = argparse.ArgumentParser(description="Gradual lint fix strategy")
    parser.add_argument(
        "--mode",
        choices=["pr", "progress", "fix"],
        default="pr",
        help="Mode: pr (check changed files), progress (check against baseline), fix (fix top error files)",
    )
    parser.add_argument(
        "--base-branch", default="main", help="Base branch for PR mode (default: main)"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Automatically fix issues where possible"
    )
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Only check for critical errors that could break functionality",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of files to fix in fix mode (default: 5)",
    )
    args = parser.parse_args()
    if args.mode == "pr":
        return check_pr_mode(args.base_branch, args.fix, args.critical_only)
    if args.mode == "progress":
        return check_progress_mode()
    if args.mode == "fix":
        return fix_top_files(args.count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
