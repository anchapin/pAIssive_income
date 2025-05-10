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

## Dependency Upgrade and Removal Workflow

### Python

**Removing a dependency:**
1. Remove the package from `requirements.txt` and/or `requirements-dev.txt`.
2. (Optional) Uninstall the package locally:  
   ```sh
   pip uninstall <package-name>
   ```
3. Reinstall all dependencies to ensure your environment matches the new requirements:  
   ```sh
   pip install -r requirements.txt -r requirements-dev.txt
   ```
4. Regenerate the lockfile:  
   ```sh
   pip freeze > requirements.lock
   ```
5. Run tests and check for breakage.
6. Commit the changes (`requirements.txt`, `requirements-dev.txt`, and `requirements.lock`).

**Upgrading a dependency:**
1. Edit the version specifier in `requirements.txt`/`requirements-dev.txt` as needed.
2. Reinstall dependencies:
   ```sh
   pip install -r requirements.txt -r requirements-dev.txt
   ```
3. Regenerate the lockfile.
4. Run tests and the security scan workflow.
5. Commit the changes.

### Node.js

**Removing a dependency:**
1. Run:
   ```sh
   npm uninstall <package-name>
   ```
   This updates both `package.json` and `package-lock.json`.
2. Run tests and check for issues.
3. Commit the changes.

**Upgrading a dependency:**
1. Run:
   ```sh
   npm install <package-name>@latest
   ```
   or specify a version as needed.
2. Run tests and review lockfile changes.
3. Commit the changes.

**General:**
- Always rerun tests after upgrades/removals.
- Regenerate lockfiles as described.
- Push changes and let CI and Dependabot check for issues and vulnerabilities.

