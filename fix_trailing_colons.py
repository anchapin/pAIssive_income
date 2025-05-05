#!/usr/bin/env python3
import re
import sys

def fix_trailing_colons(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix trailing colons in docstrings
        content = re.sub(r'(""".*?"""):(\s*$)', r'\1\2', content, flags=re.DOTALL|re.MULTILINE)
        content = re.sub(r"('''.*?'''):(\s*$)", r'\1\2', content, flags=re.DOTALL|re.MULTILINE)
        
        # Fix trailing colons in comments
        content = re.sub(r'(#[^:\n]*):(\s*$)', r'\1\2', content, flags=re.MULTILINE)
        
        # Fix trailing colons at the end of lines
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            # Skip lines that should end with a colon (if, for, def, class, etc.)
            if re.match(r'^\s*(if|for|while|def|class|else|elif|try|except|finally|with)\s+.*:$', line):
                fixed_lines.append(line)
            else:
                # Remove trailing colon if it's not part of a valid construct
                if line.rstrip().endswith(':') and not line.rstrip().endswith('::'):
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
        fix_trailing_colons(file_path)
    else:
        print("Please provide a file path to fix")
