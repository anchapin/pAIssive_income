#!/usr/bin/env python3
import sys

def check_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check for hidden characters
        line_num = 1
        pos = 0
        for i, byte in enumerate(content):
            if byte == ord('\n'):
                line_num += 1
                pos = 0
            else:
                pos += 1
            
            if line_num == 18 and pos >= 60:
                print(f"Line 18, position {pos}: Byte value {byte} (hex: {hex(byte)})")
        
        return True
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        check_file(file_path)
    else:
        check_file('fix_all_issues_final.py')
