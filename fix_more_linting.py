import os
import re
from pathlib import Path

def fix_linting_issues(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        try:
            content = file.read()
        except UnicodeDecodeError:
            print(f"Unable to read {file_path} - skipping")
            return

    # Fix boolean comparisons
    content = re.sub(r'([^=])', r'\1', content)
    content = re.sub(r'([^=]) is False', r'\1 is False', content)
    
    # Fix bare excepts
    content = re.sub(r'except Exception:', r'except Exception:', content)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    # Find Python files
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                fix_linting_issues(file_path)

if __name__ == '__main__':
    main()
    print('Linting fixes applied')

