#!/usr/bin/env python3
import re
import sys

def fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix docstrings with trailing colons
        content = re.sub(r'(""".*?"""):(\s*$)', r'\1\2', content, flags=re.DOTALL|re.MULTILINE)
        content = re.sub(r'(""".*?"""):(\s*$)', r'\1\2', content, flags=re.DOTALL|re.MULTILINE)
        
        # Fix specific issues
        content = content.replace('"""Check if a file should be ignored based on patterns.""":', '"""Check if a file should be ignored based on patterns."""')
        content = content.replace('"""Fix test classes with __init__ methods.""":', '"""Fix test classes with __init__ methods."""')
        content = content.replace('for keyword in [:', 'for keyword in [')
        content = content.replace('print(f"Fixed {file_path} with {command[0]}"):', 'print(f"Fixed {file_path} with {command[0]}")')
        content = content.replace('--check", action="store_true", help="Check for issues without fixing":', '--check", action="store_true", help="Check for issues without fixing"')
        content = content.replace('if not fix_file(:', 'if not fix_file(')
        
        # Fix lines ending with colons that shouldn't have them
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            # Skip lines that should end with a colon (if, for, def, class, etc.)
            if re.match(r'^\s*(if|for|while|def|class|else|elif|try|except|finally|with)\s+.*:$', line):
                fixed_lines.append(line)
            # Fix lines with comments ending with colons
            elif ':' in line and '#' in line:
                comment_pos = line.find('#')
                if line[comment_pos:].strip().endswith(':'):
                    fixed_lines.append(line[:-1])
                else:
                    fixed_lines.append(line)
            # Remove trailing colon if it's not part of a valid construct
            elif line.rstrip().endswith(':') and not line.rstrip().endswith('::') and ': ' not in line:
                fixed_lines.append(line.rstrip()[:-1])
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed trailing colons in {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        fix_file(file_path)
    else:
        fix_file('fix_all_issues_final.py')
