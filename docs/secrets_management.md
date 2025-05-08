# Secret Management Best Practices

## Overview

To protect sensitive information and credentials, this project uses automated tools and processes to prevent accidental leaks of secrets (API keys, passwords, private keys, etc.) in source code.

## Automated Secret Scanning

- **Pre-commit**: The `gitleaks` tool is configured as a pre-commit hook. It scans for secrets before code is committed.
- **CI/CD**: The GitHub Actions workflow runs gitleaks and other security scanners on every push and pull request.

## What is a Secret?

- API keys, tokens, passwords, private keys, certificates, or any credential that should not be public.

## How to Avoid Leaking Secrets

- **Never** hardcode secrets, credentials, or tokens in source code or configuration files.
- Use environment variables, secret managers, or CI/CD secrets to store sensitive data.
- If you need a placeholder, use obvious dummy values like `example-api-key` (which are allowlisted in scanning).

## Rotating and Removing Leaked Secrets

1. **If a secret is committed:**
   - Immediately rotate (invalidate and reissue) the secret in your provider (AWS, GitHub, etc).
   - Remove the secret from all places in the codebase. Use environment variables or secret managers instead.
   - If necessary, rewrite git history to remove the secret using tools like `git filter-repo`.

2. **Notify team members** if credentials may have been exposed.

## Local Secret Scanning

- Run `pre-commit run --all-files` to scan the entire repo for secrets before pushing.
- Or run `gitleaks detect --no-git -v --config=.gitleaks.toml` manually.

## Adding New Secrets

- Add secrets to CI/CD or deployment environments via secret managers or environment variables only.
- Never store plaintext secrets in version control.

## References

- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)