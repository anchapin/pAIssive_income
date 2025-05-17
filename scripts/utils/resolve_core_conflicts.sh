#!/bin/bash

# Script to help with merge conflict resolution
files_to_resolve=(
    "README.md"
    "pyproject.toml"
    "setup.py"
    ".dockerignore"
    "Dockerfile"
    "docker-compose.yml"
    "pytest.ini"
    ".pre-commit-config.yaml"
    ".github/workflows/deploy.yml"
)

for file in "${files_to_resolve[@]}"; do
    echo "Resolving $file..."
    git checkout --theirs "$file"
    git add "$file"
done
