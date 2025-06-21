# Branching and Code Review Guidelines

## 1. Overview

Clear development guidelines are essential to maintain code quality, enable efficient collaboration, and ensure the long-term health of the project.

> **Note:** Following these guidelines helps us deliver robust features quickly and minimize technical debt.

## 2. Branching Strategy

- **Branch Naming Conventions:**
  - Features: `feature/&lt;issue-id&gt;-&lt;short-desc&gt;` (e.g., `feature/123-add-login`)
  - Bugfixes: `bugfix/&lt;issue-id&gt;-&lt;short-desc&gt;`
  - Hotfixes: `hotfix/&lt;issue-id&gt;-&lt;short-desc&gt;`
  - Documentation: `docs/&lt;short-desc&gt;`
  - Chores/maintenance: `chore/&lt;short-desc&gt;`

- **Branch Rules:**
  - Always branch off the latest `main` (or default) branch.
  - Keep branches focused and small—one logical change per branch.
  - Prefer `rebase` over `merge` to keep history clean (unless coordinated otherwise).
  - Delete branches after merging to reduce clutter.

> **Tip:** Use descriptive, concise branch names. Include the issue ID if applicable.

## 3. Issue Tracking

- **Every change must be linked to an issue.** No branch or PR without an associated issue.
- Write clear, actionable issue descriptions: include context, expected behavior, and acceptance criteria.
- Apply relevant labels (e.g., `bug`, `enhancement`, `docs`, `good first issue`).
- Link PRs to issues using GitHub’s closing keywords (e.g., `Fixes #123`).
- Keep issue status updated: move to `In Progress` when starting, and close only after merge.

> **Note:** See [GitHub Issue Documentation](https://docs.github.com/en/issues) for best practices.

## 4. Feature Development Workflow

1. **Create an issue** describing the work, or confirm that one exists.
2. **Branch off** from `main` using the naming conventions above.
3. **Commit granularity:** Commit often, but each commit should be a logical, self-contained change.
4. **Push early:** Open a draft PR as soon as possible to enable early feedback.
5. **Keep PRs small:** Aim for &lt;400 lines of code changed (excluding tests/docs). Split large changes into multiple PRs.
6. **Update docs and tests** as you implement—do not defer!
7. **Reference the issue** in every PR.

> **Note:** Small, focused PRs speed up reviews and reduce merge conflicts.

## 5. Code Review Process

- **Required reviewers:** At least 1 senior developer and 1 peer reviewer must approve before merging.
- **Review expectations:**
  - Code must be readable, maintainable, and consistent.
  - Adequate unit/integration tests are present and meaningful.
  - Inputs/outputs are validated and errors are handled.
  - Security, performance, and privacy considerations are addressed.
  - Documentation (inline and external) is updated as needed.
  - The change aligns with architectural principles and module boundaries.

- **Review Checklist (include in PR or review):**
  - [ ] Code is easy to understand and follows style guides
  - [ ] No obvious performance or security issues
  - [ ] All public functions/types are documented
  - [ ] Tests cover new and changed logic, including edge/error cases
  - [ ] Documentation is updated
  - [ ] No circular dependencies introduced
  - [ ] No sensitive data or secrets committed
  - [ ] All comments, debug prints, and TODOs are addressed or justified

- **How to request changes:** Use GitHub review comments. Be specific and constructive.
- **Resolving conversations:** Authors must address all review feedback and resolve review threads before merging.

> **Note:** See the [Team Guidelines](../../08_team_and_collaboration/team_guidelines.md) for review etiquette.

## 6. Pull Request & Merge Guidelines

- **PR template:** Always use the provided PR template and fill out all sections.
- **CI/CD:** All status checks (tests, linting, type checks) must pass before merging.
- **Merge policy:** Use **squash-merge** only. Do not use rebase-merge or merge commits.
- **Commit messages:** Squash commit message should summarize the change and reference the issue (e.g., `feat(auth): add login endpoint (#123)`).
- **Re-approval:** If new commits are pushed after approval, reviewers must re-approve.
- **Branch protection:** Main branch is protected—requires PR review, passing CI, and up-to-date with base before merge.

> **Note:** If a PR grows too large, split it before requesting review.

## 7. Coding Standards

- **Linting, formatting, and dependency management:** Follow [Development Workflow](01_development_workflow.md) for details on using `uv`, `pnpm`, and `ruff`.
- See [LINTING.md](../../../LINTING.md) and [formatting_guide.md](../../../formatting_guide.md) for style rules.

## 8. Testing Expectations

- See [Testing Strategy](03_testing_strategy.md) for full details.
- **Coverage:** 90%+ line coverage is required for all code; enforced in CI.
- **Types of tests:** Unit, integration, and end-to-end (E2E) as appropriate.
- **Mocking:** Use mocks for external dependencies in unit tests.
- **Deterministic tests:** All tests must be reliable and produce consistent results.

> **Warning:** PRs that lower overall coverage or lack adequate tests will not be merged.

## 9. Architectural Principles

- The project follows a **hexagonal** (ports-and-adapters) or modular architecture.
- Maintain clear domain boundaries; no leaking of internal details across modules.
- **No circular dependencies** between modules or packages.
- Use **dependency injection** for all external services and infrastructure.
- **Configuration** must be done via environment variables, never hardcoded.
- Prefer **immutability** where possible to reduce side effects.
- See [Architecture docs](04_architecture/) for detailed module and system diagrams.

## 10. Appendix

### Glossary

- **Issue:** A GitHub issue describing a bug, feature request, or task.
- **PR (Pull Request):** A proposed change to the codebase.
- **CI (Continuous Integration):** Automated tests, linting, and checks run on each PR.
- **Squash Merge:** Combining all PR commits into a single commit on merge.

### Useful Commands

- `uv pip install -r requirements.txt` — install Python deps
- `uv venv .venv` — create virtual environment
- `pnpm install` — install Node.js deps
- `pnpm test` — run frontend tests
- `python scripts/run/run_tests.py --with-coverage` — run Python tests with coverage
- `ruff check .` — lint Python code

> **Note:** For more, see [Development Workflow](01_development_workflow.md).