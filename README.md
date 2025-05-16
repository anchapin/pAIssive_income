# Speeding Up Python Tests

This project is configured for fast test runs. Here are some tips:

## 1. Install Dev Dependencies (including pytest-xdist)

To enable parallel test execution and all developer/testing features, install the dev dependencies using [uv](https://github.com/astral-sh/uv):

```sh
uv pip install -e .[dev]
```
This will install `pytest`, `pytest-xdist`, and all plugins required for advanced testing.

## 2. Run Tests in Parallel (recommended)

We use [pytest-xdist](https://pypi.org/project/pytest-xdist/) to run tests in parallel across all available CPU cores:

```sh
pytest -n auto
```
By default, `-n auto` uses all available CPU cores. You can override with e.g. `pytest -n 4` to use 4 workers.

## 3. Profile Slow Tests

Find the slowest tests:

```sh
pytest --durations=10
```

## 4. Only Collect Tests from `tests/`

Test collection is limited to the `tests/` directory for speed.

## 5. Mock External Calls for Speed

If possible, mock out network/database/API calls in your tests to keep them fast and reliable.

