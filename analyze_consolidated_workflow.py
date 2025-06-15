#!/usr/bin/env python3
"""Analyze consolidated-ci-cd.yml for problematic multiline string patterns."""

from __future__ import annotations

from pathlib import Path


def analyze_workflow() -> list[tuple[int, int, str]]:
    """Analyze workflow file for problematic multiline string patterns."""
    # Read the file
    workflow_path = Path(".github/workflows/consolidated-ci-cd.yml")
    with workflow_path.open(encoding="utf-8") as f:
        content = f.read()

    return _find_problematic_patterns(content)


def _find_problematic_patterns(content: str) -> list[tuple[int, int, str]]:
    """Find problematic multiline string patterns in workflow content."""
    problematic_patterns = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        pattern = _check_run_line_for_issues(line, lines, i)
        if pattern:
            problematic_patterns.append(pattern)

    return problematic_patterns


def _check_run_line_for_issues(
    line: str, lines: list[str], line_num: int
) -> tuple[int, int, str] | None:
    """Check if a run line has problematic patterns."""
    if not ("run:" in line and ('"' in line or "'" in line)):
        return None

    # Check for backslash continuations
    has_backslash, end_line = _find_backslash_continuations(lines, line_num)

    if has_backslash:
        return (line_num, end_line, line.strip())

    return None


def _find_backslash_continuations(lines: list[str], start_line: int) -> tuple[bool, int]:
    """Find backslash continuations in workflow lines."""
    j = start_line
    has_backslash = False
    end_line = start_line
    max_check_lines = min(len(lines), start_line + 50)

    while j < max_check_lines:
        current_line = lines[j-1]

        if "\\" in current_line and (r"\ " in current_line or "\\\r" in current_line):
            has_backslash = True
            end_line = j

        if _should_stop_checking(current_line, j, start_line, has_backslash):
            break

        j += 1

    return has_backslash, end_line


def _should_stop_checking(line: str, current_pos: int, start_pos: int, has_backslash: bool) -> bool:
    """Determine if we should stop checking for continuations."""
    if current_pos <= start_pos:
        return False

    if line.strip() and not line.startswith(" ") and not has_backslash:
        return True

    return bool(line.strip() and line.startswith("    - name:"))

if __name__ == "__main__":
    analyze_workflow()
