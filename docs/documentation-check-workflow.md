# Documentation Check Workflow

This document provides detailed information about the Documentation Check workflow used in our GitHub Actions CI/CD pipeline.

## Overview

The Documentation Check workflow (`check-documentation.yml`) ensures that whenever code or configuration files are changed in a pull request or push, at least one documentation file is also updated. This enforces our policy that all code changes must be accompanied by appropriate documentation updates.

## Workflow File

The workflow is defined in `.github/workflows/check-documentation.yml` and is triggered on:
- Pull requests (opened, synchronized, reopened, or edited)
- Pushes to main/master branches

## How It Works

The workflow uses a custom Python script (`.github/scripts/check_documentation_updated.py`) that:

1. Gets the list of files changed in the current PR or commit
2. Categorizes files as documentation or non-documentation
3. If non-documentation files were changed but no documentation files were updated, the check fails

### Documentation Files Definition

Documentation files are defined as:
- Any Markdown (*.md) file at the repository root
- Any file (of any type) within the 'docs/' or 'docs_source/' directories

## Key Features

### 1. Accurate File Change Detection

- Uses `fetch-depth: 0` to fetch all history for accurate file change detection
  ```yaml
  - name: Checkout repository
    uses: actions/checkout@v4
    with:
      fetch-depth: 0  # Fetch all history for accurate file change detection
  ```

### 2. Comprehensive Git Information

- Provides detailed Git information for debugging
  ```yaml
  - name: Debug Git Info
    run: |
      echo "GitHub Event: ${{ github.event_name }}"
      echo "Base Ref: ${{ github.base_ref }}"
      echo "Head Ref: ${{ github.head_ref }}"
      echo "SHA: ${{ github.sha }}"
      echo "Repository: ${{ github.repository }}"
      echo "Current branch:"
      git branch --show-current
      echo "Git status:"
      git status
      echo "Git log (last 5 commits):"
      git log -n 5 --oneline
  ```

### 3. Robust File Change Detection

The Python script includes:
- Multiple methods to detect file changes
- Fallback mechanisms when primary methods fail
- Detailed logging for troubleshooting

## When the Check Fails

If the check fails, you'll see an error message like:

```
❌ Documentation not updated! The following files were changed without any documentation update:
  - path/to/file1.py
  - path/to/file2.py

To fix: Update the documentation (e.g., in docs/ or a root-level .md file) 
to reflect your code changes and include it in your pull request.
```

## How to Fix a Failed Check

1. **Identify the appropriate documentation file** to update based on the changes you made
2. **Update the documentation** to reflect your code changes
3. **Commit and push** the documentation updates to your branch
4. The check will automatically run again on the new commit

## Best Practices

1. **Update documentation as you code**: Don't wait until the check fails to update documentation
2. **Be specific and detailed**: Document not just what changed, but why it changed and how it works
3. **Cross-reference related docs**: If your changes affect multiple areas, update all relevant documentation
4. **Include examples**: When appropriate, include examples of how to use new or changed functionality
5. **Update the table of contents**: If you add new documentation files, update the table of contents in `docs/README.md`

## Conclusion

The Documentation Check workflow ensures that our documentation stays up-to-date with code changes, making it easier for developers to understand and use our codebase. By enforcing this policy, we maintain high-quality documentation that accurately reflects the current state of the project.
