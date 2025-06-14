"""Find YAML errors in workflow files."""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def find_yaml_error() -> None:
    """Find and analyze YAML syntax errors in workflow files."""
    file_path = ".github/workflows/codeql.yml"

    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        logger.info("Total lines in file: %d", len(lines))
        logger.info("Lines around 310-312:")

        for i in range(305, min(320, len(lines))):
            line_num = i + 1
            line_content = lines[i] if i < len(lines) else ""
            logger.info("%3d: %r", line_num, line_content)

        # Try to parse YAML
        yaml.safe_load(content)
        logger.info("YAML is valid!")

    except yaml.YAMLError as e:
        logger.exception("YAML Error")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            logger.exception(
                "Error at line %d, column %d", mark.line + 1, mark.column + 1
            )

            # Show context around the error
            lines = content.split("\n")
            start = max(0, mark.line - 5)
            end = min(len(lines), mark.line + 6)

            logger.info("Context around error:")
            for i in range(start, end):
                marker = " >>> " if i == mark.line else "     "
                logger.info("%s%3d: %s", marker, i + 1, lines[i])

    except OSError:
        logger.exception("Error reading file")
if __name__ == "__main__":
    find_yaml_error()
