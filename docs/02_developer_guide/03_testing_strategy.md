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
- Run `uv run python -m pytest --cov` locally before submitting a PR.
- Coverage gating is enforced via `--cov-fail-under=15` in CI.
- Coverage reports are generated in both text and XML formats.
- Coverage tracking includes Python files in `src/`, `ui/`, and `sdk/javascript/` directories.

---

## Best Practices & Lessons Learned

- **Mock external dependencies** (DBs, APIs, filesystems) for deterministic tests.
- **Edge cases:** Always add tests for error conditions and boundary values.
- **Markers:** Use pytest markers (`unit`, `integration`, `slow`, etc.) for organization ([see pytest.ini](../../pytest.ini)).
- **Structure:** Place tests under `tests/` in relevant subdirectories.

### Recent Improvements (PR 278)

#### Dependency Resolution
- **Fixed pytest import issues**: Resolved missing pytest dependency by installing dev dependencies
- **Database driver fixes**: Added psycopg2-binary for PostgreSQL support in Flask tests
- **Flask extension dependencies**: Installed Flask-SQLAlchemy, Flask-Migrate, and Flask-Limiter
- **Import conflict resolution**: Fixed module import issues across test files

#### Test Infrastructure Enhancements
- **MCP adapter test reliability**: Improved cross-platform test execution for MCP adapters
- **Coverage tracking improvements**: Enhanced coverage reporting with proper file inclusion patterns
- **Test environment setup**: Better handling of optional dependencies in test environments
- **Platform-specific test fixes**: Resolved Ubuntu, Windows, and macOS test compatibility issues

#### Test Execution Improvements
- **uv package manager integration**: Migrated from pip to uv for faster dependency resolution
- **Parallel test execution**: Enhanced pytest configuration for better performance
- **Error handling**: Improved test failure reporting and debugging information
- **CI/CD integration**: Better test result reporting in GitHub Actions workflows

### Fixes & Lessons from History

- **Test failures due to missing environment setup**: Always run `init_db.py` and configure `.env` before running integration/E2E tests.
- **Platform-specific failures:** Ensure temporary directories and paths are cross-platform (see [docker-compose-fix-README.md](../../docker-compose-fix-README.md)).
- **Test discovery issues:** Name test files as `test_*.py` and functions as `test_*` for pytest compatibility.
- **Legacy test coverage drops:** Refactor/expand tests when refactoring modules, not after, to prevent regressions ([see improvement_plan.md](../../improvement_plan.md)).
- **Test status tracking:** Use `test_status_report.md` (archived) for full historical context.
- **Dependency management**: Use `uv pip install -e ".[dev]"` to ensure all test dependencies are available.

---

## Running Tests

### Prerequisites
- Ensure all dependencies are installed: `uv pip install -e ".[dev]"`
- Install database drivers: `uv pip install psycopg2-binary flask-sqlalchemy flask-migrate`
- For Flask tests, ensure Flask-Limiter is installed: `uv pip install flask-limiter`

### Test Commands

```bash
# Run all tests with coverage
uv run python -m pytest --cov

# Run specific test file
uv run python -m pytest tests/test_basic.py -v

# Run only unit tests
uv run python -m pytest -m unit

# Run only integration tests
uv run python -m pytest -m integration

# Run tests with detailed output
uv run python -m pytest -v --tb=short
```

### Platform-Specific Testing

```bash
# Test MCP adapters (cross-platform)
uv run python -m pytest tests/ai_models/adapters/ -v

# Test Flask application
uv run python -m pytest tests/test_basic.py -v

# Test with coverage report
uv run python -m pytest --cov --cov-report=html
```

---

For advanced troubleshooting, see [docs/07_troubleshooting_and_faq/troubleshooting.md](../07_troubleshooting_and_faq/troubleshooting.md) and archived notes in [docs/09_archive_and_notes/](../09_archive_and_notes/).