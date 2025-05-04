
import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple


def get_python_files():
    #!/usr/bin/env python
    pass  # Added missing block
    Script to update Pydantic models to use the new V2 style with ConfigDict.
    This script addresses the remaining Pydantic deprecation warnings for class-based config.





    (directory: str, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
    """Get all Python files in a directory and its subdirectories."""
    if exclude_patterns is None:
    exclude_patterns = []

    python_files = []
    for root, _, files in os.walk(directory):
    for file in files:
    if file.endswith(".py"):
    file_path = Path(os.path.join(root, file))

    # Check if file should be excluded
    if any(re.search(pattern, str(file_path)) for pattern in exclude_patterns):
    continue

    python_files.append(file_path)

    return python_files


    def contains_pydantic_model(file_content: str) -> bool:
    """Check if a file contains Pydantic models."""
    patterns = [
    r"class\s+\w+\s*\([^)]*BaseModel[^)]*\)",  # class X(BaseModel):
    r"from\s+pydantic\s+import",  # from pydantic import
    r"import\s+pydantic",  # import pydantic
    ]

    for pattern in patterns:
    if re.search(pattern, file_content):
    return True

    return False


    def has_class_config(file_content: str) -> bool:
    """Check if a file contains class Config for Pydantic models."""
    pattern = r"class\s+Config\s*:"
    return bool(re.search(pattern, file_content))


    def update_pydantic_model(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Update a Pydantic model to use ConfigDict instead of class Config."""
    with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

    if not contains_pydantic_model(content) or not has_class_config(content):
    return False, "No Pydantic models with class Config found"

    # Parse the Python file
    try:
    tree = ast.parse(content)
except SyntaxError as e:
    return False, f"Syntax error: {e}"

    # Track changes
    changes_made = False
    updated_content = content

    # Find all class definitions
    for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
    # Check if this is a Pydantic model by looking at its bases
    is_pydantic_model = False
    for base in node.bases:
    if isinstance(base, ast.Name) and base.id == "BaseModel":
    is_pydantic_model = True
    break
    elif isinstance(base, ast.Attribute) and base.attr == "BaseModel":
    is_pydantic_model = True
    break

    if not is_pydantic_model:
    continue

    # Look for class Config within the model
    for item in node.body:
    if isinstance(item, ast.ClassDef) and item.name == "Config":
    # Found a class Config, need to replace it with model_config = ConfigDict(...)
    config_start = item.lineno
    config_end = item.end_lineno if hasattr(item, "end_lineno") else item.lineno

    # Extract the content of the Config class  content.splitlines()[config_start-1:config_end]
    config_content = "\n".join(config_lines)

    # Extract the configuration options
    config_options = {}
    for config_item in item.body:
    if isinstance(config_item, ast.Assign):
    for target in config_item.targets:
    if isinstance(target, ast.Name):
    if isinstance(config_item.value, ast.Constant):
    config_options[target.id] = config_item.value.value

    # Create the ConfigDict statement
    config_dict_str = "model_config = ConfigDict("
    if config_options:
    config_dict_str += ", ".join(f"{k}={repr(v)}" for k, v in config_options.items())
    config_dict_str += ")"

    # Add import for ConfigDict if not already present
    if "from pydantic import ConfigDict" not in content:
    if "from pydantic import" in content:
    # Add ConfigDict to existing import
    updated_content = re.sub(
    r"from pydantic import (.+)",
    r"from pydantic import \1, ConfigDict",
    updated_content
    )
    else:
    # Add new import
    updated_content = "from pydantic import ConfigDict\n" + updated_content

    # Replace the class Config with model_config = ConfigDict(...)
    updated_content = updated_content.replace(config_content, config_dict_str)
    changes_made = True

    if changes_made and not dry_run:
    with open(file_path, "w", encoding="utf-8") as f:
    f.write(updated_content)

    return changes_made, "Updated Pydantic model to use ConfigDict"


    def main():
    """Main function to parse args and run the script."""  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error
    parser = argparse.ArgumentParser(description="Update Pydantic models to use ConfigDict instead of class Config.")
    parser.add_argument(
    "path",
    nargs="?",
    default=".",
    help="Path to a file or directory to process (default: current directory)",
    )
    parser.add_argument(
    "--exclude",
    nargs="+",
    default=[],
    help="Patterns to exclude from processing",
    )
    parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Don't actually modify files, just show what would be changed",
    )

    args = parser.parse_args()

    path = Path(args.path)
    if path.is_file():
    # Process a single file
    changed, message = update_pydantic_model(path, args.dry_run)
    if changed:
    print(f"✅ Updated {path}: {message}")
    else:
    print(f"ℹ️ Skipped {path}: {message}")
    else:
    # Process a directory
    files = get_python_files(args.path, args.exclude)
    updated_count = 0

    for file_path in files:
    changed, message = update_pydantic_model(file_path, args.dry_run)
    if changed:
    print(f"✅ Updated {file_path}: {message}")
    updated_count += 1
    else:
    print(f"ℹ️ Skipped {file_path}: {message}")

    print(f"\nProcessed {len(files)} files, updated {updated_count} files.")

    return 0


    if __name__ == "__main__":
    sys.exit(main(