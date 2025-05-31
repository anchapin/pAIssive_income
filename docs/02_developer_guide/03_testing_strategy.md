# Testing Strategy

This project enforces high standards for test coverage, reliability, and maintainability.

---

## Types of Tests

- **Unit tests:** Isolate and verify individual functions/classes.
- **Integration tests:** Validate interactions between components and services.
- **End-to-end (E2E) tests:** Ensure workflows function as expected across the stack.

---

## Coverage Requirements

- **15% minimum line coverage** is enforced by CI.
- Run `python run_tests.py --with-coverage` locally before submitting a PR.
- Coverage gating is enforced via `--cov-fail-under=15` in CI.

---

## Best Practices & Lessons Learned

- **Mock external dependencies** (DBs, APIs, filesystems) for deterministic tests.
- **Edge cases:** Always add tests for error conditions and boundary values.
- **Markers:** Use pytest markers (`unit`, `integration`, `slow`, etc.) for organization ([see pytest.ini](../../pytest.ini)).
- **Structure:** Place tests under `tests/` in relevant subdirectories.

### Fixes & Lessons from History

- **Test failures due to missing environment setup**: Always run `init_db.py` and configure `.env` before running integration/E2E tests.
- **Platform-specific failures:** Ensure temporary directories and paths are cross-platform (see [docker-compose-fix-README.md](../../docker-compose-fix-README.md)).
- **Test discovery issues:** Name test files as `test_*.py` and functions as `test_*` for pytest compatibility.
- **Legacy test coverage drops:** Refactor/expand tests when refactoring modules, not after, to prevent regressions ([see improvement_plan.md](../../improvement_plan.md)).
- **Test status tracking:** Use `test_status_report.md` (archived) for full historical context.

---

## Running Tests

```bash
# Run all tests with coverage
python run_tests.py --with-coverage

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

---

For advanced troubleshooting, see [docs/07_troubleshooting_and_faq/troubleshooting.md](../07_troubleshooting_and_faq/troubleshooting.md) and archived notes in [docs/09_archive_and_notes/](../09_archive_and_notes/).