# CONTRIBUTING

Contribution guidelines and best practices have moved to [docs/contributing.md](docs/contributing.md) in the centralized documentation.

## Testing Standards

To maintain a robust, reliable, and high-quality codebase, all contributions must meet these **testing standards**:

- **Minimum Coverage:** All code changes must maintain or increase overall test coverage. A minimum of **90% line coverage** is enforced by CI using coverage tools. Any PR that causes coverage to drop below this threshold will fail and cannot be merged.
- **Coverage Enforcement:** Coverage is enforced in CI via `--cov-fail-under=90`. You must run `python run_tests.py --with-coverage` locally and confirm coverage before submitting a PR.
- **Test Types:** All new features, bug fixes, or refactors must be accompanied by appropriate **unit** and/or **integration** tests. If your change introduces new paths, add tests for both success and error/failure scenarios.
- **Edge Cases & Error Handling:** Tests must cover not only typical usage, but also edge cases, boundary conditions, invalid inputs, and error handling. For APIs, include tests for failure modes (e.g., bad requests, unauthorized access, rate limits).
- **Markers & Organization:** Use `pytest` markers (such as `unit`, `integration`, `slow`, `api`, `security`) as described in `pytest.ini` to organize tests. This allows for selective and efficient test execution.
- **Test Placement & Structure:** Place new or expanded tests in the appropriate directory under `tests/` (e.g., `tests/api/` for API endpoints, `tests/services/` for services). Follow the structure of existing test files.
- **Mocking External Dependencies:** In unit tests, mock all external resources (such as databases, APIs, services) to ensure tests are deterministic and reliable.
- **Test Readability:** Write clear, descriptive test names and docstrings, and structure tests for readability and maintainability.
- **CI Compliance:** All tests (unit, integration, etc.) must pass in CI, and coverage must meet the threshold. See `.github/workflows/ci.yml` for details of enforcement.
- **Documentation:** When adding new modules, endpoints, or features, update or add docstrings and relevant documentation (including usage examples or test documentation) as appropriate.

**Summary:**
Before submitting a PR:

- Ensure your changes are fully tested, including edge/error cases.
- Run `python run_tests.py --with-coverage` and confirm coverage is **at least 90%**.
- Ensure your code passes all linting and type checks (`ruff`, `mypy`, etc.).
- Check that all automated tests pass in CI.

For questions or clarifications on testing, consult `test_coverage_plan.md`, review existing tests, or ask a maintainer.

## Pull Request Checklist

- [ ] My code includes tests covering all new/changed logic and edge/error cases.
- [ ] I ran `python run_tests.py --with-coverage` and confirmed coverage is ≥90%.
- [ ] My code passes all linting and type checks (`ruff`, `mypy`, etc.).
- [ ] All automated tests pass in CI.
