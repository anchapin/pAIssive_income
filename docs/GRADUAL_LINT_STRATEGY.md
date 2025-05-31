# Gradual Lint Fix Strategy

This document outlines our approach to gradually improving code quality while maintaining development velocity.

## Overview

Instead of blocking all development with 400+ linting errors, we've implemented a **gradual fix strategy** that:

1. ✅ **Allows new PRs to pass** by only checking changed files
2. 📈 **Tracks progress** over time with a baseline system
3. 🔧 **Provides tools** to systematically fix existing issues
4. 🚀 **Maintains velocity** while improving quality

## Current Status

- **Baseline established**: 441 linting errors across 51 files
- **Tests passing**: All basic tests (9/9) are working
- **Strategy active**: New PRs only check changed files

## How It Works

### For Pull Requests

The new workflow (`.github/workflows/gradual-lint-check.yml`) only checks files that have changed in the PR:

```bash
# Check only changed files
python scripts/gradual_lint_fix.py --mode pr --base-branch main

# Auto-fix if possible
python scripts/gradual_lint_fix.py --mode pr --base-branch main --fix
```

### For Progress Tracking

Track improvement over time:

```bash
# Check progress against baseline
python scripts/gradual_lint_fix.py --mode progress
```

### For Systematic Fixing

Fix the worst files first:

```bash
# Fix top 5 files with most errors
python scripts/gradual_lint_fix.py --mode fix --count 5
```

## Usage Guide

### For Developers

1. **Creating PRs**: Your PR will only be checked for linting issues in files you've changed
2. **Auto-fixes**: The workflow will attempt to auto-fix simple issues
3. **Manual fixes**: If auto-fix isn't possible, you'll need to fix issues manually

### For Maintainers

1. **Weekly cleanup**: Run `python scripts/gradual_lint_fix.py --mode fix --count 10` to fix top error files
2. **Progress tracking**: Run `python scripts/gradual_lint_fix.py --mode progress` to see improvement
3. **Baseline updates**: The baseline automatically updates when overall errors decrease

## Files and Tools

### Key Files

- `scripts/gradual_lint_fix.py` - Main tool for gradual fixing
- `.github/workflows/gradual-lint-check.yml` - PR workflow for changed files only
- `lint_baseline.json` - Current baseline of errors (auto-generated)
- `ruff.toml` - Linting configuration

### Commands

```bash
# Check only changed files (PR mode)
python scripts/gradual_lint_fix.py --mode pr

# Check progress against baseline
python scripts/gradual_lint_fix.py --mode progress

# Fix top N files with most errors
python scripts/gradual_lint_fix.py --mode fix --count 5

# Auto-fix changed files
python scripts/gradual_lint_fix.py --mode pr --fix
```

## Benefits

1. **✅ Unblocked Development**: PRs can pass CI/CD without fixing all existing issues
2. **📈 Measurable Progress**: Track improvement over time with baseline comparison
3. **🎯 Focused Effort**: Fix the worst files first for maximum impact
4. **🔧 Automated Fixes**: Auto-fix simple issues where possible
5. **🚀 Maintained Velocity**: Keep shipping while improving quality

## Migration Plan

### Phase 1: Stabilization (Current)
- ✅ Establish baseline (441 errors across 51 files)
- ✅ Implement PR-only checking
- ✅ Create fixing tools

### Phase 2: Systematic Improvement (Next 2-4 weeks)
- 🎯 Fix top 10 files with most errors
- 📊 Reduce total errors by 50%
- 🔧 Add more auto-fix rules

### Phase 3: Full Coverage (Future)
- 🎯 Achieve <50 total errors
- 🔄 Enable full linting on all files
- 📈 Maintain high code quality

## Error Categories

Current errors by type (from baseline):
- **Style issues**: Import sorting, quotes, whitespace
- **Security issues**: Subprocess usage, path handling
- **Type annotations**: Missing or incorrect annotations
- **Complexity**: Functions too long or complex
- **Documentation**: Missing docstrings

## Best Practices

### For New Code
- Follow existing patterns in the codebase
- Use type hints for new functions
- Add docstrings for public functions
- Run `ruff check --fix` before committing

### For Fixing Existing Code
- Focus on high-impact files first
- Fix one category of errors at a time
- Test after each fix to ensure functionality
- Use the gradual fix tool for systematic improvement

## Monitoring

Track progress with:
```bash
# Weekly progress check
python scripts/gradual_lint_fix.py --mode progress

# Current error count
ruff check . --output-format=concise | wc -l

# Files with most errors
python scripts/gradual_lint_fix.py --mode fix --count 0  # Shows top files without fixing
```

## Support

If you encounter issues with the gradual fix strategy:

1. Check that `ruff` is installed: `pip install ruff`
2. Ensure you're on the correct branch for PR comparisons
3. Run `python scripts/gradual_lint_fix.py --mode progress` to refresh baseline
4. Contact the maintainers if the workflow fails

---

*This strategy allows us to improve code quality incrementally while maintaining development velocity. The goal is continuous improvement, not perfection overnight.* 