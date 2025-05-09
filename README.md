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

## Dependency Maintenance Workflow

**Python:**
1. **Add/Upgrade/Remove a Dependency:**
   - Edit `requirements.txt` and/or `requirements-dev.txt` as needed.
   - (Optional but recommended for upgrades: run `pip install --upgrade <package-name>` to update and test locally.)
2. **Reinstall All Dependencies:**
   - Run:
     ```sh
     pip install -r requirements.txt -r requirements-dev.txt
     ```
3. **Regenerate the Lockfile:**
   - Run:
     ```sh
     pip freeze > requirements.lock
     ```
   - Commit all changed files (`requirements.txt`, `requirements-dev.txt`, `requirements.lock`).

**Node.js:**
1. **Add/Upgrade/Remove a Dependency:**
   - Use npm commands (`npm install <pkg>`, `npm uninstall <pkg>`, `npm update <pkg>`).
   - This will update both `package.json` and `package-lock.json`.
2. **Test your changes locally:**
   - Run:
     ```sh
     npm ci
     ```
3. **Commit both `package.json` and `package-lock.json`** if changed.

**After Any Dependency Change:**
- Run tests and linter to ensure nothing is broken.
- Push your branch and check CI results (including security scan).
- Review and address any security findings.

**Dependabot PR Workflow:**
- Review automated PRs for dependency updates.
- Ensure CI passes and no new vulnerabilities are introduced.
- Merge promptly to keep dependencies healthy and secure.

