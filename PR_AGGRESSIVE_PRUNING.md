# Aggressive Pruning PR

## Motivation & Scope

This PR addresses Issue #267: **“Aggressive Pruning: Remove Experimental, Redundant, and Unused Code”**.
The goal is to reduce technical debt by permanently removing legacy, experimental, and redundant files and directories that are no longer referenced by production code, tests, or CI workflows.

## Removals Checklist

- Entire legacy/experimental directories:
  - `artist_experiments/`
  - `scripts/fix/`
- Root-level scripts and placeholders no longer referenced:
  - `fix_github_actions.bat`, `fix_github_actions.ps1`, `fix_test_collection_warnings.py`, `sues.py`
  - `generate_bandit_config_fixed.py`
  - All `*_fixed.py` and `*.staged` files at project root
- Scripts in `scripts/` no longer referenced:
  - `fix_pr_trigger.py`, `fix_workflow_issues.py`
- Unused requirements files:
  - `requirements-artist.txt`, `requirements-test-minimal.txt`, `requirements_mem0.txt`, `requirements_filtered.txt`, `requirements_test.txt`

## Notes

- No functional code or test execution paths were impacted.
- No CI or devops scripts reference any of the removed files/directories.
- The codebase, tests, and workflows should operate identically post-cleanup.