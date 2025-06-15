#!/usr/bin/env python3

with open(".github/workflows/codeql-macos.yml") as f:
    lines = f.readlines()


# Check surrounding lines
for i in range(318, 323):
    if i < len(lines):
        pass
