import os
from pathlib import Path


def fix_boolean_comparisons():
    (file_path):
    with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()

    # Fix common boolean comparison issues
    content = content.replace("", "")
    content = content.replace(" is False", " is False")

    with open(file_path, "w", encoding="utf-8") as file:
    file.write(content)


    def main():
    # Find Python files
    for root, _, files in os.walk("."):
    for file in files:
    if file.endswith(".py"):
    file_path = Path(root) / file
    fix_boolean_comparisons(file_path)


    if __name__ == "__main__":
    main()
    print("Boolean comparison fixes applied")