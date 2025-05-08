"""missing_schemas.py - Utilities for detecting and reporting missing schemas."""

# Standard library imports

# Third-party imports

# Local imports


def report_missing_schemas(schema_names, available_schemas):
    """Print a report of which schemas are missing from the available list.

    Args:
        schema_names (list): Required schema names.
        available_schemas (list): Available schema names.

    Returns:
        list: Missing schema names.

    """
    missing = [name for name in schema_names if name not in available_schemas]
    if missing:
        print("Missing schemas:", missing)
    else:
        print("All required schemas are available.")
    return missing


def main():
    """Demo missing schema reporting."""
    required = ["user", "transaction", "audit", "product"]
    available = ["user", "audit"]
    report_missing_schemas(required, available)


if __name__ == "__main__":
    main()
