# Test Coverage Roadmap

## Current Status

- **Current test coverage**: Varies by module (see below)
- **Target test coverage**: 80% (as required by CI/CD workflows)
- **Current threshold in CI workflows**: 80%

### Module Coverage Status

| Module | Current Coverage | Status |
|--------|-----------------|--------|
| `common_utils/file_utils.py` | 100% | ✅ Complete |
| `common_utils/json_utils.py` | 98% | ✅ Complete |
| `common_utils/date_utils.py` | 100% | ✅ Complete |
| `common_utils/string_utils.py` | 27% | 🔄 In Progress |
| `common_utils/exceptions.py` | 100% | ✅ Complete |
| `common_utils/config_loader.py` | 100% | ✅ Complete |
| `utils/tooling.py` | 84% | ✅ Complete |
| `ai_models/adapters/` | Varies | 📅 Planned |
| `app_flask/` | Varies | 📅 Planned |
| `api/` | Varies | 📅 Planned |

## Approach

This document outlines the roadmap for improving test coverage in the project. We will take an incremental approach, focusing on the most critical modules first and gradually expanding to cover more of the codebase.

## Milestones

### Phase 1: Utility Modules (Current)

- **Target**: 30% overall coverage
- **Focus areas**:
  - ✅ `common_utils/file_utils.py` (improved from 24% to 100%)
  - ✅ `common_utils/json_utils.py` (improved from 23% to 100%)
  - ✅ `common_utils/date_utils.py` (improved from 43% to 100%)
  - ✅ `common_utils/exceptions.py` (improved from 46% to 100%)
  - ✅ `common_utils/config_loader.py` (improved from 20% to 100%)
  - `common_utils/string_utils.py` (currently at 27%)

### Phase 2: Core Functionality (Next 1-2 weeks)

- **Target**: 50% overall coverage
- **Focus areas**:
  - `ai_models/adapters/` modules
  - `app_flask/` modules
  - `common_utils/logging/` modules
  - `common_utils/secrets/` modules

### Phase 3: API and Integration (Next 3-4 weeks)

- **Target**: 65% overall coverage
- **Focus areas**:
  - `api/routes/` modules
  - `api/middleware/` modules
  - `services/` modules
  - Integration between components

### Phase 4: Full Coverage (Next 5-6 weeks)

- **Target**: 80% overall coverage
- **Focus areas**:
  - Remaining modules
  - Edge cases and error handling
  - Performance and stress testing

## Testing Strategies

### Unit Testing

- Focus on testing individual functions and methods in isolation
- Use mocking to isolate dependencies
- Ensure high coverage of edge cases and error handling

### Integration Testing

- Test interactions between components
- Focus on API boundaries and data flow
- Verify correct behavior of integrated systems

### Test-Driven Development

- For new features, write tests before implementation
- For existing code, write tests that document current behavior before making changes

## Priority Modules

The following modules have been identified as high priority for test coverage improvement:

1. **Utility Modules**
   - `common_utils/file_utils.py` (✅ Completed)
   - `common_utils/json_utils.py` (✅ Completed)
   - `common_utils/date_utils.py` (✅ Completed)
   - `common_utils/exceptions.py` (✅ Completed)
   - `common_utils/config_loader.py` (✅ Completed)
   - `common_utils/string_utils.py`

2. **Core Functionality**
   - `ai_models/adapters/mcp_adapter.py`
   - `ai_models/adapters/adapter_factory.py`
   - `ai_models/adapters/openai_compatible_adapter.py`
   - `ai_models/adapters/ollama_adapter.py`
   - `ai_models/adapters/lmstudio_adapter.py`
   - `app_flask/mcp_servers.py`

3. **API and Integration**
   - `api/routes/` modules
   - `api/middleware/` modules
   - `services/` modules

## Monitoring Progress

Progress will be tracked by running the following command:

```bash
pytest --cov=. --cov-report=term-missing
```

The coverage report will be reviewed weekly to ensure progress is being made.

## Coverage Threshold

The project now enforces a coverage threshold of 15% in all CI workflows:

- `.github/workflows/python-tests.yml`
- `.github/workflows/mcp-adapter-tests.yml`
- `.github/workflows/consolidated-ci-cd.yml`
- `pytest.ini`
- `scripts/run/run_tests.py`

### Running Tests Locally

To run tests with the same coverage threshold locally:

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=term-missing --cov-fail-under=15

# Run specific tests with coverage
pytest path/to/test_file.py --cov=. --cov-report=term-missing --cov-fail-under=15

# Run tests with HTML report
pytest --cov=. --cov-report=html --cov-fail-under=15
```

### Handling Coverage Failures

If your tests fail due to insufficient coverage:

1. Run with HTML report to identify uncovered lines:
   ```bash
   pytest --cov=. --cov-report=html
   ```

2. Open the HTML report to see which lines need coverage:
   ```bash
   # Windows
   start htmlcov/index.html
   # macOS
   open htmlcov/index.html
   # Linux
   xdg-open htmlcov/index.html
   ```

3. Write additional tests to cover the missing lines

4. Re-run the tests to verify improved coverage

## Best Practices

1. **Write Meaningful Tests**: Focus on testing behavior, not implementation details
2. **Test Edge Cases**: Include tests for error conditions and boundary cases
3. **Keep Tests Fast**: Optimize tests to run quickly to encourage frequent testing
4. **Maintain Test Independence**: Tests should not depend on each other
5. **Use Appropriate Mocking**: Mock external dependencies but not the code under test
6. **Follow Test Naming Conventions**: Use descriptive names that explain what is being tested
7. **Avoid Test Duplication**: Use parameterized tests for similar test cases
8. **Keep Tests Simple**: Tests should be easy to understand and maintain

## Conclusion

By following this roadmap, we will incrementally improve test coverage to meet the 80% threshold required by our CI/CD workflows. This will improve the quality and reliability of the codebase and make it easier to maintain in the future.
