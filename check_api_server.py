"""Script to check the API server code for syntax errors."""

import ast
import sys

def check_syntax(file_path):
    """Check the syntax of a Python file.
    
    Args:
        file_path (str): Path to the Python file to check.
        
    Returns:
        bool: True if the file has valid syntax, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source = file.read()
        
        # Parse the source code
        ast.parse(source)
        print(f"✅ {file_path} has valid syntax.")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path} at line {e.lineno}, column {e.offset}:")
        print(f"   {e.text.strip()}")
        print(f"   {' ' * (e.offset - 1)}^")
        print(f"   {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error checking {file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_api_server.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not check_syntax(file_path):
        sys.exit(1)
