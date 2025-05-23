# Instructions to Fix Frontend E2E Workflow

The frontend-e2e workflow is failing because it's trying to use npm instead of pnpm. Here are the exact changes needed to fix the workflow:

## Changes Needed in `.github/workflows/frontend-e2e.yml`:

1. Update the Node.js setup to use pnpm cache:
```yaml
- name: Set up Node.js ${{ matrix.node-version }}
  uses: actions/setup-node@v4
  with:
    node-version: ${{ matrix.node-version }}
    cache: 'pnpm'
    cache-dependency-path: 'ui/react_frontend/pnpm-lock.yaml'
```

2. Update the pnpm setup:
```yaml
- name: Setup pnpm
  uses: pnpm/action-setup@v4
  with:
    version: 8
    run_install: false
```

## Steps to Apply These Changes:

1. Open the file `.github/workflows/frontend-e2e.yml` in your editor
2. Find the "Set up Node.js" step (around line 28) and update it to include the cache configuration
3. Find the "Setup pnpm" step (around line 41) and update it to use v4 and add run_install: false
4. Commit and push the changes

## Example Commit Message:
"Fix frontend-e2e workflow to use pnpm action-setup@v4 and configure Node.js with pnpm cache"

These changes will fix the failing frontend-e2e workflow in your PR.
