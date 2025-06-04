# CodeQL Auto-Fix Disabled

## Overview

This document explains the changes made to prevent the GitHub Actions bot from automatically fixing CodeQL issues and committing those changes to the repository.

## Changes Made

The following changes were implemented to prevent automatic fixing of CodeQL issues:

1. **Modified `fix-codeql-issues.yml` workflow**:
   - Renamed to "Fix CodeQL Issues (Manual Mode)"
   - Removed automatic trigger on pull requests
   - Changed permissions from `write` to `read` for contents and pull-requests
   - Removed the automatic fix script execution
   - Removed the automatic commit and push steps

2. **Modified `auto-fix.yml` workflow**:
   - Renamed to "Auto Fix (Linting Only)"
   - Removed the `codeql` and `both` options from the workflow dispatch inputs
   - Completely removed the `fix-codeql-issues` job

3. **Updated CodeQL workflow files**:
   - Modified `codeql.yml`, `codeql-fixed.yml`, `codeql-macos.yml`, and `codeql-ubuntu.yml`
   - Replaced the automatic fix script execution with just creating a `.codeqlignore` file
   - Added comments explaining that we're not automatically fixing CodeQL issues

## Why These Changes Were Made

The GitHub Actions bot was automatically fixing CodeQL issues and committing those changes to the repository, as seen in this commit:
https://github.com/anchapin/pAIssive_income/pull/166/commits/68fdd9055597fbbca6f13efba797ce319593a95d

This automatic behavior was not desired because:
1. It can introduce unexpected changes to the codebase
2. It bypasses the normal code review process
3. It can potentially introduce new issues or break existing functionality
4. It makes it harder to track who made what changes and why

## How to Fix CodeQL Issues Manually

If you need to fix CodeQL issues, you can:

1. Run the CodeQL analysis locally using the GitHub CLI:
   ```bash
   gh codeql github analyze --language=javascript-typescript,python
   ```

2. Review the results and fix the issues manually

3. If you want to use the fix script as a reference, you can run it locally without committing:
   ```bash
   chmod +x scripts/fix-codeql-issues.sh
   ./scripts/fix-codeql-issues.sh
   ```
   Then review the changes before committing them.

## Restoring Auto-Fix Functionality

If you want to restore the automatic fixing of CodeQL issues, you can:

1. Revert the changes to the workflow files
2. Re-enable the automatic triggers in `fix-codeql-issues.yml`
3. Restore the `fix-codeql-issues` job in `auto-fix.yml`
4. Restore the fix script execution in the CodeQL workflow files

## Additional Resources

- [GitHub CodeQL Documentation](https://codeql.github.com/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Security Documentation](https://docs.github.com/en/code-security)
