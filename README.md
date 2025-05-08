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

**To upgrade or remove a dependency:**

1. Edit `requirements.txt` and/or `requirements-dev.txt` to add, upgrade, or remove the relevant package.
2. (Recommended) Create and activate a fresh virtual environment.
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
3. Reinstall all dependencies with:
   ```sh
   pip install -r requirements.txt -r requirements-dev.txt
   ```
4. Regenerate the lockfile:
   ```sh
   pip freeze > requirements.lock
   ```
5. Run tests to ensure the environment works as expected.
6. Commit the changes to `requirements.txt`, `requirements-dev.txt`, and `requirements.lock`.

### Node.js

**To upgrade or remove a dependency:**

1. Use npm/yarn for dependency changes:
   - To upgrade: `npm install <package>@latest`
   - To remove: `npm uninstall <package>`
2. This updates both `package.json` and `package-lock.json` automatically.
3. Run tests to ensure everything works.
4. Commit both `package.json` and `package-lock.json`.

**Tips:**
- After any dependency change, always check for (and address) new security issues flagged by CI.
- If in doubt, let Dependabot handle version bumps and review/merge its PRs.

