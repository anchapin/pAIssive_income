# Project Environment & Dependency Management

## Python

- **Install dependencies**:
  ```sh
  pip install -r requirements.txt -r requirements-dev.txt
  ```

- **Dependency Locking**:  
  This project uses a `requirements.lock` file to ensure reproducible environments. After updating dependencies, **install both `requirements.txt` and `requirements-dev.txt`**, then regenerate the lockfile:
  ```sh
  pip install -r requirements.txt -r requirements-dev.txt
  pip freeze > requirements.lock
  ```

- **Development dependencies** are managed with `requirements-dev.txt`.

## Node.js

- **Install dependencies**:
  ```sh
  npm ci
  ```
- Dependencies are pinned via `package-lock.json`.
- **Security scanning**: `npm audit` is run automatically in CI to detect vulnerabilities.

## Automated Dependency Updates

- [Dependabot](https://docs.github.com/en/code-security/dependabot) is enabled for Python, Node.js, Docker, and GitHub Actions dependencies. Update PRs are created automatically, including for the Python lockfile (`requirements.lock`).

## Vulnerability Scanning

- Security scanning runs automatically on pushes and pull requests:
  - Python: `pip-audit`, `safety`
  - Node.js: `npm audit`
  - Static analysis: `bandit`, `semgrep`, `pylint`
  - Container: `trivy`
  - Secret scanning: `gitleaks`

## Best Practices

- Regularly review and address Dependabot and security scan PRs.
- Regenerate the Python lockfile after any dependency updates.
- See `.github/workflows/security_scan.yml` for the full list of automated checks.

## Keeping Dependencies Healthy

- When adding or removing Python dependencies, update both `requirements.txt`/`requirements-dev.txt` and **regenerate `requirements.lock`**.
- For Node.js, always use `npm ci` for installation and let Dependabot update `package-lock.json`.
- Review and merge Dependabot PRs and address security alerts promptly.

## Dependency Upgrade & Removal Workflow

### Python

1. **To upgrade a dependency:**
   - Edit `requirements.txt` and/or `requirements-dev.txt` to change the version specifier.
   - Run:
     ```sh
     pip install -r requirements.txt -r requirements-dev.txt
     pip freeze > requirements.lock
     ```
   - Commit the updated requirements files and the new `requirements.lock`.
   - Run tests and CI to confirm compatibility.

2. **To remove a dependency:**
   - Remove the package from `requirements.txt` and/or `requirements-dev.txt`.
   - Uninstall it from your environment:
     ```sh
     pip uninstall <package-name>
     ```
   - Regenerate `requirements.lock` as above.
   - Search the codebase for any usage and remove or refactor as needed.
   - Run all tests and CI workflows to confirm removal is safe.

### Node.js

1. **To upgrade a dependency:**
   - Run:
     ```sh
     npm install <package-name>@latest
     ```
     or specify a version as needed.
   - Commit the updated `package.json` and `package-lock.json`.
   - Run tests and CI to confirm compatibility.

2. **To remove a dependency:**
   - Run:
     ```sh
     npm uninstall <package-name>
     ```
   - Commit the updated `package.json` and `package-lock.json`.
   - Remove all usage in the codebase.
   - Run all tests and CI workflows.

**Tips:**
- After removal, search for any lingering imports/usages.
- Always update lockfiles after changes.
- Review CI results for issues after any dependency changes.

