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

## Dependency Workflow

Follow these steps for adding, upgrading, or removing dependencies:

### Python

**Add or Upgrade a Dependency:**
1. Add or update the package in `requirements.txt` or `requirements-dev.txt`.
2. Run:
   ```sh
   pip install -r requirements.txt -r requirements-dev.txt
   pip freeze > requirements.lock
   ```
3. Commit both the requirements file(s) and `requirements.lock`.

**Remove a Dependency:**
1. Remove the package from the relevant requirements file(s).
2. (Optional) Uninstall from your environment:
   ```sh
   pip uninstall <package>
   ```
3. Reinstall all dependencies and regenerate lockfile as above.

**After any change:**  
- Push your branch and ensure CI passes (security/lint/test checks).
- Address any Dependabot PRs or security scan alerts as they appear.

### Node.js

**Add or Upgrade a Dependency:**
1. Use `npm install <package>` or `npm update <package>`.
2. Commit both `package.json` and `package-lock.json`.

**Remove a Dependency:**
1. Use `npm uninstall <package>`.
2. Commit both `package.json` and `package-lock.json`.

**After any change:**  
- Use `npm ci` to install dependencies in CI and locally for reproducibility.
- Review security scan results and update as needed.

For more details, see `.github/workflows/security_scan.yml` and the [Dependabot documentation](https://docs.github.com/en/code-security/dependabot).

