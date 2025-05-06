import os
import subprocess

def resolve_core_conflicts():
    files_to_resolve = [
        "README.md",
        "pyproject.toml",
        "setup.py",
        ".dockerignore",
        "Dockerfile",
        "docker-compose.yml",
        "pytest.ini",
        ".pre-commit-config.yaml",
        ".github/workflows/deploy.yml"
    ]
    
    for file in files_to_resolve:
        print(f"Resolving {file}...")
        subprocess.run(["git", "checkout", "origin/main", "--", file], check=False)
        subprocess.run(["git", "add", file], check=False)

if __name__ == "__main__":
    resolve_core_conflicts()
