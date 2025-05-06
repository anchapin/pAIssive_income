'import os
import subprocess
from typing import List, Dict

class MergeResolver:
    def __init__(self):
        self.phases = {
            "config": [
                "pyproject.toml",
                ".pre-commit-config.yaml",
                "pytest.ini",
                ".coveragerc",
                "mypy.ini",
                "ruff.toml"
            ],
            "docker": [
                "Dockerfile",
                "docker-compose.yml",
                ".dockerignore"
            ],
            "github": [
                ".github/workflows/deploy.yml",
                ".github/workflows/ci.yml",
                ".github/workflows/security_scan.yml",
                ".github/workflows/codeql.yml"
            ],
            "docs": [
                "README.md",
                "SECURITY.md",
                "docs/*"
            ]
        }
    
    def resolve_phase(self, phase_name: str) -> None:
        print(f"\nResolving {phase_name} files...")
        files = self.phases.get(phase_name, [])
        for file in files:
            print(f"Processing {file}...")
            subprocess.run(["git", "checkout", "origin/main", "--", file], check=False)
            subprocess.run(["git", "add", file], check=False)

    def resolve_all(self) -> None:
        for phase_name in self.phases:
            self.resolve_phase(phase_name)
        print("\nResolution complete. Please review changes before committing.")

if __name__ == "__main__":
    resolver = MergeResolver()
    resolver.resolve_all()
'
