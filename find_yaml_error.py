"""Find YAML errors in workflow files."""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

<<<<<<< HEAD

def find_yaml_error() -> None:
    """Find and analyze YAML syntax errors in workflow files."""
    file_path = ".github/workflows/codeql.yml"

    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        logger.info("Total lines in file: %d", len(lines))
        logger.info("Lines around 310-312:")
=======
def find_yaml_error():
    file_path = ".github/workflows/codeql.yml"

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        print(f"Total lines in file: {len(lines)}")
        print("\nLines around 310-312:")
>>>>>>> origin/main

        for i in range(305, min(320, len(lines))):
            line_num = i + 1
            line_content = lines[i] if i < len(lines) else ""
<<<<<<< HEAD
            logger.info("%3d: %r", line_num, line_content)
=======
            print(f"{line_num:3d}: {line_content!r}")
>>>>>>> origin/main

        # Try to parse YAML
        yaml.safe_load(content)
        logger.info("YAML is valid!")

    except yaml.YAMLError as e:
<<<<<<< HEAD
        logger.exception("YAML Error")
=======
        print(f"\nYAML Error: {e}")
>>>>>>> origin/main
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            logger.exception(
                "Error at line %d, column %d", mark.line + 1, mark.column + 1
            )

            # Show context around the error
            lines = content.split("\n")
            start = max(0, mark.line - 5)
            end = min(len(lines), mark.line + 6)

<<<<<<< HEAD
            logger.info("Context around error:")
=======
            print("\nContext around error:")
>>>>>>> origin/main
            for i in range(start, end):
                marker = " >>> " if i == mark.line else "     "
                logger.info("%s%3d: %s", marker, i + 1, lines[i])

    except OSError:
        logger.exception("Error reading file")

<<<<<<< HEAD

=======
>>>>>>> origin/main
if __name__ == "__main__":
    find_yaml_error()
