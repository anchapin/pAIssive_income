"""missing_schemas.py - Utilities for detecting and reporting missing schemas."""

from __future__ import annotations

# Standard library imports
import logging

# Third-party imports

# Local imports
logger = logging.getLogger(__name__)


def report_missing_schemas(
    schema_names: list[str], available_schemas: list[str]
) -> list[str]:
    """
    Print a report of which schemas are missing from the available list.

    Args:
        schema_names (list): Required schema names.
        available_schemas (list): Available schema names.

    Returns:
        list: Missing schema names.

    """
    missing = [name for name in schema_names if name not in available_schemas]
    if missing:
        logger.warning("Missing schemas: %s", missing)
    else:
        logger.info("All required schemas are available.")
    return missing


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    """Demo missing schema reporting."""
    required = ["user", "transaction", "audit", "product"]
    available = ["user", "audit"]
    report_missing_schemas(required, available)


if __name__ == "__main__":
    main()
