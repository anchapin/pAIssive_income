# Scripts Directory

This directory contains various utility scripts for the pAIssive_income project.

## Script Categories

- `fix/`: Scripts for fixing common issues
- `run/`: Scripts for running various components
- `setup/`: Scripts for setting up environments
- `utils/`: Utility scripts

## Shell Scripts

Shell scripts (`.sh` files) need to be executable on Unix-based systems. If you're using a Unix-based system (Linux, macOS), you can make a script executable with:

```bash
chmod +x scripts/script_name.sh
```

On Windows, shell scripts are typically run through WSL, Git Bash, or other Unix-like environments.

## Notable Scripts

- `start-mock-api.sh`: Used by docker-compose to start the mock API server for testing and CI environments
- `fix-docker-compose-errors.sh`: Fixes common Docker Compose issues
- `run-docker-compose-ci.sh`: Runs Docker Compose in CI environments

## Adding New Scripts

When adding new scripts:

1. Place them in the appropriate subdirectory
2. Make sure they have proper documentation
3. Make shell scripts executable on Unix systems
4. Add them to this README if they serve an important function
