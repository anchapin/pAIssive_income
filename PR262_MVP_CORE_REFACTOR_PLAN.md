# PR #262 MVP Core Refactor Plan

## 🎯 Objective

Prepare and execute a core modules refactor towards the MVP slice as defined in [Issue #262](https://github.com/anchapin/pAIssive_income/issues/262), under the epic “Refactor Core Modules Towards MVP Slice.” This initiative aims to modernize, streamline, and prepare foundational components for reliable MVP delivery.

---

## 🗂 Scope

- `api/auth` – Authentication and authorization logic
- `common_utils/config` – Shared configuration and environment utilities
- `services/database` – Database access and ORM/refactoring
- `users/` – User models and management logic
- `utils/` – General-purpose utilities
- `main.py` – Entrypoint modernization
- `tests/` (relevant core module tests)
- _(additional modules to be confirmed during analysis phase)_

---

## ✅ Acceptance Criteria

- [ ] All targeted core modules refactored to MVP-ready state
- [ ] Unit and integration tests updated and passing for each module
- [ ] Type-checking (e.g. mypy, pyright) shows 100% success for refactored modules
- [ ] Linting (e.g. ruff, eslint) passes cleanly
- [ ] No files/directories listed in `.gitignore` are imported or tested
- [ ] Documentation updated and reviewed
- [ ] No regression in current CI pipelines (uv & pnpm workflows green)

---

## 🔧 Planned Work

1. **Analysis & Planning**
   - Confirm full list of modules in scope
   - Review current state and technical debt per module
2. **Incremental Refactor**
   - Apply agreed coding standards and modularization
   - Remove legacy/deprecated code paths
3. **Testing & Validation**
   - Update/create unit and integration tests
   - Ensure test isolation (exclude `.gitignore` content)
4. **Type & Lint Pass**
   - Achieve 100% type-check/lint compliance
5. **Documentation**
   - Update module-level and project docs
6. **Review & Signoff**
   - Code reviews with owners/maintainers
   - Address feedback iteratively
7. **Rollout & Migration**
   - Merge and monitor for regressions

---

## 🧪 Testing Strategy

- **Unit & Integration Tests:**  
  Update and expand coverage for refactored modules in `tests/`.  
  Ensure no files or directories listed in `.gitignore` are referenced, imported, or tested.
- **E2E/Smoke Tests:**  
  For impacted flows, run end-to-end checks as available.
- **Type Checking:**  
  Full strict mode on refactored code (using `pyright`/`mypy`).
- **Linting:**  
  All code must pass configured linters (e.g. `ruff` for Python, `eslint` for JavaScript/TypeScript components).
- **Tooling:**  
  CI tasks must use `uv` for Python envs and `pnpm` for Node.js.
- **CI Validation:**  
  All pipeline stages (test, lint, type-check) must pass in CI.

---

## 📝 Documentation

- Update module-level docstrings and README sections for all refactored modules
- Update or create relevant pages in `docs/` and `docs_source/`
- Add migration notes and API change summaries as needed

---

## 🚀 Rollout / Migration

- Staged merge: core modules first, followed by dependent layers
- Monitor for CI regressions post-merge
- Announce any breaking changes or deprecations in CHANGELOG and docs
- Provide migration/upgrade path for downstream consumers if applicable

---

## 🛡️ Risks & Mitigations

- **Risk:** Refactor introduces breaking changes  
  _Mitigation:_ Staged rollout, regression and E2E tests, clear docs
- **Risk:** Insufficient test coverage reveals bugs post-merge  
  _Mitigation:_ Expand/strengthen tests, enforce coverage minimums
- **Risk:** .gitignore’d content referenced by accident  
  _Mitigation:_ Explicit test exclusions, CI validation, code review
- **Risk:** CI/CD pipeline disruptions  
  _Mitigation:_ Use feature branch, validate all workflows before merge

---

## 📋 Checklist Before Merge

- [ ] Code owner(s) review complete
- [ ] All tests (unit/integration/E2E/type/lint) passing
- [ ] Docs updated and reviewed
- [ ] No .gitignore’d files referenced/imported
- [ ] CI green (uv + pnpm workflows)
- [ ] Rollback plan documented

---

## 🔗 References

- [Issue #262: Core Refactor for MVP](https://github.com/anchapin/pAIssive_income/issues/262)
- Epic: “Refactor Core Modules Towards MVP Slice”
- Example prior PR docs:  
  [`PR_166_WORKFLOW_FIXES_SUMMARY.md`](./PR_166_WORKFLOW_FIXES_SUMMARY.md),  
  [`PR243_CODEQL_FIXES_SUMMARY.md`](./PR243_CODEQL_FIXES_SUMMARY.md)
- `.gitignore` (repo root)
- [README.md](./README.md)

---

## 🕒 Timeline

- **Planning & Analysis:** 2 days
- **Refactor Implementation:** 5–8 days
- **Testing & Validation:** 2–3 days
- **Docs & Review:** 1–2 days
- **Rollout:** 1 day
- _Total Estimate:_ ~2 weeks

---

*Drafted: 2025-01-27 — For Issue #262 / MVP Core Refactor Initiative*