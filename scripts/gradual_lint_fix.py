#!/usr/bin/env python3
"""
Gradual Lint Fix Strategy Script

This script implements a gradual approach to fixing linting issues:
1. For PRs: Only lint changed files
2. For main branch: Track progress and gradually expand coverage
3. Provides tools to systematically fix existing issues
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def get_changed_files(base_branch: str = "main") -> List[str]:
    """Get list of Python files changed compared to base branch."""
    try:
        # Get changed files from git
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )

        # Filter for Python files
        changed_files = [
            line.strip()
            for line in result.stdout.strip().split("\n")
            if line.strip().endswith(".py") and Path(line.strip()).exists()
        ]

        return changed_files
    except subprocess.CalledProcessError:
        print("Warning: Could not get changed files from git. Checking all files.")
        return []


def run_ruff_on_files(files: List[str], fix: bool = False) -> Dict[str, int]:
    """Run ruff on specific files and return error counts."""
    if not files:
        return {}

    results = {}

    for file in files:
        try:
            cmd = ["ruff", "check", file]
            if fix:
                cmd.append("--fix")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore", check=False,
            )

            # Count errors (each line is typically one error)
            if result.stdout:
                error_count = len([line for line in result.stdout.strip().split("\n") if line.strip()])
            else:
                error_count = 0

            results[file] = error_count

            if error_count > 0:
                print(f"📁 {file}: {error_count} issues")
                if not fix and result.stdout:  # Only show details if not fixing
                    print(result.stdout)
            else:
                print(f"✅ {file}: Clean")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error checking {file}: {e}")
            results[file] = -1

    return results


def get_baseline_errors() -> Dict[str, int]:
    """Get current error count for all files to establish baseline."""
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--output-format=concise"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore", check=False,
        )

        if result.stdout and result.stdout.strip():
            # Parse concise format: filename:line:col: code message
            file_counts = {}

            for line in result.stdout.strip().split("\n"):
                if line.strip() and ":" in line:
                    # Extract filename (everything before first colon)
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


def save_baseline(baseline: Dict[str, int], filename: str = "lint_baseline.json"):
    """Save baseline error counts to file."""
    baseline_file = Path(filename)
    with baseline_file.open("w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)
    print(f"💾 Baseline saved to {baseline_file}")


def load_baseline(filename: str = "lint_baseline.json") -> Dict[str, int]:
    """Load baseline error counts from file."""
    baseline_file = Path(filename)
    if baseline_file.exists():
        with baseline_file.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def check_pr_mode(base_branch: str = "main", fix: bool = False) -> int:
    """Check only changed files in PR mode."""
    print("🔍 Running in PR mode - checking only changed files...")

    changed_files = get_changed_files(base_branch)

    if not changed_files:
        print("✅ No Python files changed or could not detect changes.")
        return 0

    print(f"📝 Found {len(changed_files)} changed Python files:")
    for file in changed_files:
        print(f"  - {file}")

    results = run_ruff_on_files(changed_files, fix=fix)

    # Check if any changed files have new errors
    total_errors = sum(count for count in results.values() if count > 0)

    if total_errors == 0:
        print("✅ All changed files are lint-clean!")
        return 0
    print(f"❌ Found {total_errors} linting issues in changed files.")
    if not fix:
        print("💡 Run with --fix to automatically fix issues, or fix manually.")
    return 1


def check_progress_mode() -> int:
    """Check progress against baseline."""
    print("📊 Running in progress mode - checking against baseline...")

    baseline = load_baseline()
    if not baseline:
        print("📋 No baseline found. Creating new baseline...")
        current_errors = get_baseline_errors()
        save_baseline(current_errors)
        total_errors = sum(current_errors.values())
        print(f"📊 Baseline established: {total_errors} total errors across {len(current_errors)} files")
        return 0

    current_errors = get_baseline_errors()

    # Compare with baseline
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

    # Files that were completely fixed
    fixed_files = [f for f in baseline.keys() if f not in current_errors]

    # Report progress
    print("📈 Progress Report:")
    print(f"  ✅ Files completely fixed: {len(fixed_files)}")
    print(f"  📈 Files improved: {len(improved_files)}")
    print(f"  📉 Files regressed: {len(regressed_files)}")
    print(f"  🆕 New files with issues: {len(new_files)}")

    if improved_files:
        print("\n🎉 Improved files:")
        for filename, improvement in improved_files:
            print(f"  - {filename}: -{improvement} errors")

    if regressed_files:
        print("\n⚠️  Regressed files:")
        for filename, regression in regressed_files:
            print(f"  - {filename}: +{regression} errors")

    # Update baseline if there's overall improvement
    total_baseline = sum(baseline.values())
    total_current = sum(current_errors.values())

    if total_current <= total_baseline:
        save_baseline(current_errors)
        print(f"\n📊 Overall progress: {total_baseline} → {total_current} errors ({total_baseline - total_current:+d})")
        return 0
    print(f"\n📊 Overall regression: {total_baseline} → {total_current} errors ({total_current - total_baseline:+d})")
    return 1


def fix_top_files(count: int = 5) -> int:
    """Fix the files with the most errors."""
    print(f"🔧 Fixing top {count} files with most errors...")

    current_errors = get_baseline_errors()
    if not current_errors:
        print("✅ No errors found!")
        return 0

    # Sort files by error count
    sorted_files = sorted(current_errors.items(), key=lambda x: x[1], reverse=True)
    top_files = [filename for filename, _ in sorted_files[:count]]

    print("🎯 Targeting files:")
    for i, (filename, error_count) in enumerate(sorted_files[:count], 1):
        print(f"  {i}. {filename}: {error_count} errors")

    # Fix the files
    results = run_ruff_on_files(top_files, fix=True)

    # Check results
    fixed_count = sum(1 for count in results.values() if count == 0)
    print(f"\n✅ Successfully fixed {fixed_count}/{len(top_files)} files")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Gradual lint fix strategy")
    parser.add_argument(
        "--mode",
        choices=["pr", "progress", "fix"],
        default="pr",
        help="Mode: pr (check changed files), progress (check against baseline), fix (fix top error files)"
    )
    parser.add_argument(
        "--base-branch",
        default="main",
        help="Base branch for PR mode (default: main)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues where possible"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of files to fix in fix mode (default: 5)"
    )

    args = parser.parse_args()

    if args.mode == "pr":
        return check_pr_mode(args.base_branch, args.fix)
    if args.mode == "progress":
        return check_progress_mode()
    if args.mode == "fix":
        return fix_top_files(args.count)

    return 0


if __name__ == "__main__":
    sys.exit(main())
