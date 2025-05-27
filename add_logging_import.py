#!/usr/bin/env python3

import logging
import os
import re
import sys

# Configure logging
logger = logging.getLogger(__name__)

"""
Script to add logging import to test files.
"""



def add_logging_import(file_path):
    """Add logging import to a Python file if it's missing."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Check if logging is already imported
    if re.search(r"import\s+logging", content) or re.search(r"from\s+logging\s+import", content):
        print(f"Logging already imported in {file_path}")
        return False

    # Find the first import statement
    import_match = re.search(r"^(from|import)\s+", content, re.MULTILINE)
    if import_match:
        # Insert logging import before the first import
        pos = import_match.start()
        new_content = content[:pos] + "import logging\n" + content[pos:]
    else:
        # If no imports found, add after docstring or at the beginning
        docstring_match = re.search(r'^""".*?"""', content, re.DOTALL)
        if docstring_match:
            pos = docstring_match.end()
            new_content = content[:pos] + "\n\nimport logging\n" + content[pos:]
        else:
            new_content = "import logging\n" + content

    # Write the modified content back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Added logging import to {file_path}")
    return True

def process_directory(directory):
    """Process all Python test files in a directory."""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = os.path.join(root, file)
                if add_logging_import(file_path):
                    count += 1
    return count

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "tests"

    count = process_directory(directory)
    print(f"Added logging import to {count} files")
