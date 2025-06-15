#!/usr/bin/env python3
"""Analyze consolidated-ci-cd.yml for problematic multiline string patterns."""


def analyze_workflow():
    # Read the file
    with open(".github/workflows/consolidated-ci-cd.yml", encoding="utf-8") as f:
        content = f.read()

    # Find all problematic multiline strings that start with quotes and have backslash continuations
    problematic_patterns = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        # Look for run: followed by quoted strings with backslash continuations
        if "run:" in line and ('"' in line or "'" in line):
            # Check if this line and following lines have backslash continuations
            j = i
            has_backslash = False
            end_line = i
            while j < len(lines) and j < i + 50:  # Check next 50 lines max
                if "\\" in lines[j-1] and (r"\ " in lines[j-1] or "\\\r" in lines[j-1]):
                    has_backslash = True
                    end_line = j
                if lines[j-1].strip() and not lines[j-1].startswith(" ") and j > i and not has_backslash:
                    break
                if j > i and lines[j-1].strip() and lines[j-1].startswith("    - name:"):
                    break
                j += 1

            if has_backslash:
                problematic_patterns.append((i, end_line, line.strip()))

    for _line_start, _line_end, _line_content in problematic_patterns:
        pass

    # Also find specific error patterns

    # Look for unescaped quotes in run blocks
    in_run_block = False
    for i, line in enumerate(lines, 1):
        if "run:" in line and '"' in line:
            in_run_block = True
            # Check for immediate quote issues
            if line.count('"') % 2 != 0:
                pass
        elif in_run_block and line.strip() and not line.startswith(" "):
            in_run_block = False

    return problematic_patterns

if __name__ == "__main__":
    analyze_workflow()
