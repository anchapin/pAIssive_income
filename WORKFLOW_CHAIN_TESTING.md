# Workflow Chain Testing Guide

This document provides instructions for testing the workflow chain functionality where dependent workflows run after the "Auto Fix (Linting & CodeQL Issues)" workflow completes successfully.

## Overview

The following workflows have been updated to run after the auto-fix workflow completes:

1. **consolidated-ci-cd.yml** - Main CI/CD pipeline
2. **python-tests.yml** - Python testing
3. **codeql.yml** - CodeQL security analysis
4. **mcp-adapter-tests.yml** - MCP adapter tests
5. **frontend-vitest.yml** - Frontend unit tests
6. **frontend-e2e.yml** - Frontend E2E tests
7. **codeql-ubuntu.yml** - Ubuntu-specific CodeQL analysis

## Testing Steps

### 1. Manual Trigger Test

To test the workflow chain manually:

1. Navigate to the GitHub Actions tab in your repository
2. Find the "Auto Fix (Linting & CodeQL Issues)" workflow
3. Click "Run workflow" and select the appropriate options:
   - **fix_type**: Choose "both" to run both linting and CodeQL fixes
   - **branch**: Ensure you're running on a main branch (main, dev, master, develop, or devops_tasks)
4. Monitor the workflow execution

### 2. Expected Behavior

When the auto-fix workflow completes successfully:

1. **Auto-fix workflow runs first** and performs linting/CodeQL fixes
2. **Upon successful completion**, the following workflows should automatically trigger:
   - Consolidated CI/CD
   - Python Tests
   - CodeQL Analysis
   - MCP Adapter Tests
   - Frontend Vitest (if frontend files are present)
   - Frontend E2E (if frontend files are present)
   - CodeQL Ubuntu

### 3. Verification Checklist

After triggering the auto-fix workflow, verify:

- [ ] Auto-fix workflow completes successfully
- [ ] Dependent workflows appear in the Actions tab with "workflow_run" trigger
- [ ] All dependent workflows show the correct trigger source
- [ ] Workflows only run when auto-fix succeeds (not when it fails)
- [ ] Manual triggers still work for individual workflows

### 4. Troubleshooting

#### Workflows Not Triggering

If dependent workflows don't trigger after auto-fix completes:

1. **Check branch**: Workflow_run triggers only work from the default branch (main)
2. **Verify workflow file location**: Ensure all workflow files are on the main branch
3. **Check workflow name**: Ensure the workflow name matches exactly: "Auto Fix (Linting & CodeQL Issues)"
4. **Review permissions**: Ensure the repository has proper workflow permissions

#### Workflows Triggering on Failure

If workflows trigger even when auto-fix fails:

1. Check the `if` condition in each workflow job
2. Ensure the condition includes: `github.event.workflow_run.conclusion == 'success'`

### 5. Key Implementation Details

#### Workflow Run Trigger Configuration

Each dependent workflow includes:

```yaml
on:
  # ... existing triggers ...
  workflow_run:
    workflows: ["Auto Fix (Linting & CodeQL Issues)"]
    types:
      - completed
    branches:
      - main
      - dev
      - master
      - develop
      - devops_tasks  # (where applicable)
```

#### Success Condition

Each job includes:

```yaml
jobs:
  job-name:
    # Only run if auto-fix workflow completed successfully, or if triggered by other events
    if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}
```

### 6. Testing Scenarios

#### Scenario 1: Successful Auto-Fix
1. Trigger auto-fix workflow
2. Let it complete successfully
3. Verify all dependent workflows trigger

#### Scenario 2: Failed Auto-Fix
1. Trigger auto-fix workflow with intentional failure
2. Verify dependent workflows do NOT trigger

#### Scenario 3: Manual Workflow Triggers
1. Manually trigger individual workflows
2. Verify they still work independently

#### Scenario 4: Push/PR Triggers
1. Make a push to main branch
2. Verify workflows trigger normally (not waiting for auto-fix)

### 7. Monitoring and Logs

To monitor the workflow chain:

1. **GitHub Actions Tab**: View all workflow runs and their relationships
2. **Workflow Run Details**: Check the "triggered by" information
3. **Logs**: Review individual workflow logs for any issues

### 8. Important Notes

- **Default Branch Requirement**: The `workflow_run` trigger only works when the workflow file is on the default branch
- **Timing**: There may be a small delay between auto-fix completion and dependent workflow triggers
- **Concurrency**: The concurrency settings in workflows may affect execution order
- **Resource Limits**: Multiple workflows running simultaneously may hit GitHub Actions resource limits

## Success Criteria

The workflow chain is working correctly when:

1. Auto-fix workflow can be triggered manually and completes successfully
2. All dependent workflows automatically trigger after auto-fix success
3. Dependent workflows do not trigger when auto-fix fails
4. Individual workflows can still be triggered manually
5. Normal push/PR triggers continue to work for all workflows

## References

- [GitHub Actions workflow_run trigger documentation](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run)
- [GitHub Community Discussion on workflow chaining](https://github.com/orgs/community/discussions/66512) 