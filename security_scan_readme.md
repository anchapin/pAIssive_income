# Security Scan Workflow

This document provides information about the enhanced security scan workflow for the pAIssive_income project.

## Overview

The security scan workflow is designed to identify security vulnerabilities in the codebase and dependencies. It runs the following security tools:

1. **Safety**: Checks for known vulnerabilities in Python dependencies
2. **Bandit**: Static analysis tool for Python code to find common security issues
3. **Trivy**: Comprehensive vulnerability scanner for containers and filesystems
4. **pnpm audit**: Checks for vulnerabilities in Node.js dependencies (if applicable)
5. **Node.js Dependency Scanning**: Added pnpm audit for checking Node.js dependencies.

> **Note:** This project uses [pnpm](https://pnpm.io/) as its primary package manager. `pnpm audit` is the recommended command for vulnerability scanning. `npm audit` is mentioned for informational purposes if dealing with npm-specific contexts.

---

## Node.js Dependency Scanning

If your project uses Node.js dependencies, you should regularly scan for vulnerabilities:

3. **Run pnpm Audit**:

pnpm audit

> If you are in an environment still using npm, you would use:
> npm audit

### Audit Results

`pnpm audit` (or `npm audit`) reports vulnerabilities in Node.js dependencies with the following information:
- [pnpm Audit Documentation](https://pnpm.io/cli/audit)
- [npm Audit Documentation](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning)
