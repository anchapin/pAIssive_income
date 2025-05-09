# Contributing to pAIssive Income

Thank you for considering contributing to the pAIssive Income project! Please read these guidelines carefully to ensure a smooth contribution process.

...

## Testing Standards

To maintain quality and reliability, all code contributions must meet the following **testing standards**:

### Coverage Requirements

- **Minimum Coverage:** All code must be covered by automated tests (unit, integration, etc.) to achieve at least **90% overall test coverage**. This is enforced in CI; pull requests will fail if coverage drops below the threshold.
- **Branch Coverage:** Where practical, ensure that all logical branches (e.g., if/else, error paths) are exercised by tests.
- **New Features:** All new features must include corresponding tests that cover normal use, edge cases, and error handling.
- **Bug Fixes:** All bug fixes must include a test that demonstrates the issue and verifies the fix.
- **Negative Testing:** Every API endpoint and public method should have at least one negative test (invalid input, denied access, etc.).
- **Untestable Code:** If a code path cannot be reasonably tested (e.g., due to external system behavior), add a clear comment and use `# pragma: no cover`.
- **Documentation:** For complex logic or non-obvious behavior, add comments in tests describing the scenario.
- **Coverage Reports:** Review the coverage report (HTML, terminal, or CI summary) to ensure all new/changed code is covered. (If available, see the project coverage badge or report in the CI output.)

### Test Types

- **Unit Tests:** Should test individual functions, classes, and methods in isolation.
- **Integration Tests:** Should test how multiple components interact, including workflows and API endpoints.
- **Error Handling:** Every endpoint and public function should have tests for invalid input, authentication/authorization errors, and unexpected edge cases.
- **Performance/Security Tests:** If your code affects performance or security, add or update relevant tests as appropriate.

### Test Practices

- Use **pytest** for all tests.
- Place tests in the appropriate subdirectory under `tests/` (e.g., `tests/api/`, `tests/unit/`).
- Name test files as `test_*.py` and test classes as `Test*`.
- Use markers (`@pytest.mark.unit`, `@pytest.mark.integration`, etc.) as appropriate.
- Use mocking (e.g., `pytest-mock`, `unittest.mock`) for external dependencies and side effects.
- Structure tests to be repeatable; avoid time, order, or environment dependencies.

### Running Tests

- Run the full test suite and coverage check locally with:
  ```
  python run_tests.py --with-coverage --phase all
  ```
- Fix any failures before submitting a pull request.
- Check coverage results and add tests for any new or changed code that is not covered.

### PR Review Checklist

- [ ] All new/changed code is tested.
- [ ] CI passes, including coverage check.
- [ ] No decrease in overall coverage.
- [ ] All tests are clear, maintainable, and use good naming and structure.

For further details, refer to the [test coverage plan](test_coverage_plan.md).

Thank you for helping maintain a high standard of quality in this project!
