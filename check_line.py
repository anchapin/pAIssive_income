#!/usr/bin/env python3

with open('.github/workflows/codeql-macos.yml', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print(f"Line 320: '{lines[319].rstrip()}'")
print(f"Line 320 length: {len(lines[319])}")
print(f"Line 320 repr: {repr(lines[319])}")

# Check surrounding lines
for i in range(318, 323):
    if i < len(lines):
        print(f"Line {i+1}: '{lines[i].rstrip()}'")
