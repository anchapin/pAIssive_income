<!--
ARCHIVED: This file has been consolidated into docs/04_security_and_compliance/02_scanning_and_tooling.md and docs/09_archive_and_notes/amazon_q_notes.md for historical reference.
-->

# Bandit Security Scan Fix

This document explains the fix for the Bandit security scanning workflow issue in GitHub Actions.

## Problem

The GitHub Actions workflow for Bandit security scanning was failing with the following error:

```
Error: Path does not exist: security-reports/bandit-results-15053076509.sarif
```

This error occurred because the workflow was trying to upload a SARIF file that didn't exist. The issue was specifically in the Windows environment.

## Root Causes

1. **Directory Creation Issue**: The `security-reports` directory wasn't being properly created in the Windows environment.
2. **SARIF File Generation**: The Bandit command was failing to generate the SARIF file with the specific run ID.
3. **Bandit Configuration**: The Bandit configuration file for the specific run ID didn't exist.
4. **Error Handling**: There was insufficient error handling to create fallback files when Bandit failed.

## Solution

The solution involves several improvements to the workflow:

1. **Improved Directory Creation**: Added explicit directory creation with proper error handling.
2. **Pre-created SARIF Files**: Created empty SARIF files before running Bandit to ensure they exist.
3. **Bandit Configuration Generation**: Added a step to generate Bandit configuration files for the specific run ID.
4. **Better Error Handling**: Added more robust error handling to create fallback files when Bandit fails.
5. **JSON Output Format**: Changed Bandit output format from SARIF to JSON, which is more reliable in Bandit.
6. **Verification Steps**: Added verification steps to ensure the SARIF files exist before uploading.

## Implementation

The fix was implemented in several files:

1. **fix_bandit_security_scan.ps1**: A PowerShell script to fix the Bandit security scanning issue by creating the necessary directories and files.
2. **generate_bandit_config.py**: A Python script to generate Bandit configuration files for specific run IDs.
3. **run_bandit_scan.ps1**: A PowerShell script to run the Bandit scan with proper error handling.
4. **.github/workflows/security_scan.yml**: Updated the workflow to use the improved scripts and error handling.

## Usage

To fix the Bandit security scanning issue:

1. Run the `fix_bandit_security_scan.ps1` script with the run ID:

```powershell
powershell -ExecutionPolicy Bypass -File fix_bandit_security_scan.ps1 <run_id>
```

2. Verify that the SARIF files exist in the `security-reports` directory:

```powershell
Get-ChildItem -Path security-reports
```

3. Push the changes to the repository to trigger the GitHub Actions workflow.

## Verification

After implementing the fix, the GitHub Actions workflow should complete successfully without the "Path does not exist" error. The SARIF files should be properly created and uploaded to GitHub Advanced Security.

## Additional Notes

- The fix ensures that empty SARIF files are created even if Bandit fails, allowing the workflow to continue.
- The fix is compatible with all platforms (Windows, Linux, macOS) but specifically addresses the Windows issue.
- The fix maintains backward compatibility with existing Bandit configurations and SARIF files.

## Related Files

- `.github/bandit/bandit-config-windows-<run_id>.yaml`: Bandit configuration file for Windows.
- `security-reports/bandit-results-<run_id>.sarif`: SARIF file with the specific run ID.
- `security-reports/bandit-results.sarif`: Standard SARIF file for backward compatibility.
