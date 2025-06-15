#!/usr/bin/env python3
"""Script to debug specific YAML syntax errors."""

def debug_yaml_errors() -> None:
    """Debug specific YAML syntax errors in workflow files."""
    # Files with errors and their line numbers
    error_files = [
        (".github/workflows/codeql-macos.yml", 317, 319),
        (".github/workflows/codeql-windows.yml", 184, 185),
        (".github/workflows/codeql.yml", 310, 313)
    ]

    for filepath, error_line, _context_line in error_files:

        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            # Show context around the error
            start = max(0, error_line - 5)
            end = min(len(lines), error_line + 5)

            for i in range(start, end):
                i + 1

        except Exception:
            pass

if __name__ == "__main__":
    debug_yaml_errors()
