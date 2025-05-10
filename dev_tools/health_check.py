#!/usr/bin/env python3
"""health_check.py.

Orchestrates repository quality checks:
- Linting (flake8, ruff)
- Formatting (black or ruff format)
- Static typing (mypy)
- Security (bandit)
- Dependency audit (uv pip audit)
Requires tools: flake8, ruff, mypy, bandit, uv (with pip audit functionality), black,
"""Run uv pip audit for dependency security."""
if shutil.which("uv"):
    run("uv pip audit", "Python dependency audit")
else:
    print("uv not found, skipping dependency audit.")


def docs():
    """Build Sphinx documentation, if present."""
    if os.path.isdir("docs_source") and shutil.which("sphinx-build"):
        run(
            "sphinx-build docs_source docs/_build",
            "Sphinx documentation build",
        )
    else:
        print("Sphinx not configured or not found, skipping docs build.")


def usage():
    """Print usage instructions."""
    print(__doc__)


def main():
    """Entry point for orchestrated health checks."""
    args = set(sys.argv[1:])
    if not args or "--all" in args:
        lint()
        type_check()
        security()
        deps()
        docs()
    else:
        if "--lint" in args:
            lint()
        if "--type" in args:
            type_check()
        if "--security" in args:
            security()
        if "--deps" in args:
            deps()
        if "--docs" in args:
            docs()
        if "--help" in args or "-h" in args:
            usage()


if __name__ == "__main__":
    main()
