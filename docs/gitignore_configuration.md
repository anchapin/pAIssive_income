# .gitignore Configuration

This document describes the `.gitignore` configuration used in the pAIssive_income project.

## Overview

The `.gitignore` file specifies intentionally untracked files that Git should ignore. This is important for:

1. Preventing sensitive information from being committed
2. Excluding build artifacts and temporary files
3. Keeping the repository clean and focused on source code

## Configuration

The project's `.gitignore` file is organized into sections for different types of files:

### Python-specific

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
```

### Testing and Coverage

```
# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
```

### Environment and IDE

```
# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
*venv*/
*env*/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo
```

### Project-specific

```
# Project specific
project_plan.json
example_project_plan.json

# OS specific
.DS_Store
Thumbs.db
node_modules
.aider*

# Playwright reports
ui/react_frontend/playwright-report/
```

### Node.js and Frontend

```
# Logs
logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dev-debug.log

# Dependency directories
node_modules/

# Editor directories and files
.idea
.vscode
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Task files
tasks.json
tasks/
```

## Recent Updates

The `.gitignore` file has been updated to include:

1. Additional virtual environment patterns (`*venv*/`, `*env*/`) to catch all variations of virtual environment directories
2. Node.js and frontend-specific patterns for logs and dependency directories
3. Task-related files (`tasks.json`, `tasks/`) used by task management tools
4. Additional IDE-specific files and directories

## Usage

### Adding Files to .gitignore

To add new patterns to the `.gitignore` file:

1. Edit the `.gitignore` file
2. Add the new pattern on a new line
3. Commit the changes

Example:
```bash
echo "*.log" >> .gitignore
git add .gitignore
git commit -m "Add *.log to .gitignore"
```

### Ignoring Already Tracked Files

If you need to ignore a file that is already tracked by Git:

```bash
git rm --cached <file>
```

Then commit the changes.

### Checking Ignored Status

To check if a file is ignored:

```bash
git check-ignore -v <file>
```

## Best Practices

1. **Be specific**: Use specific patterns rather than overly broad ones
2. **Group related patterns**: Keep related patterns together in the file
3. **Comment sections**: Use comments to organize the file into sections
4. **Include common patterns**: Include patterns for common build artifacts and temporary files
5. **Exclude sensitive files**: Always exclude files containing sensitive information like API keys and credentials

## Related Documentation

- [Contributing Guide](contributing.md)
- [Environment Variables](environment_variables.md)
- [Development Workflow](dev_workflow.md)
