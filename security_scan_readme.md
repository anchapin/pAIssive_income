# Security Scan Workflow

This document provides information about the enhanced security scan workflow for the pAIssive_income project.

## Overview

The security scan workflow is designed to identify security vulnerabilities in the codebase and dependencies. It runs the following security tools:

1. **Safety**: Checks for known vulnerabilities in Python dependencies
2. **Bandit**: Static analysis tool for Python code to find common security issues
3. **Trivy**: Comprehensive vulnerability scanner for containers and filesystems
4. **npm audit**: Checks for vulnerabilities in Node.js dependencies (if applicable)
5. **Node.js Dependency Scanning**: Added npm audit for checking Node.js dependencies.

> **Note:** If you are using [pnpm](https://pnpm.io/) as your package manager, you can use `pnpm audit` as an alternative to `npm audit` for vulnerability scanning.

---

## Node.js Dependency Scanning

If your project uses Node.js dependencies, you should regularly scan for vulnerabilities:

3. **Run npm Audit** (if using Node.js):

npm audit

> Or, if you use pnpm:  
> pnpm audit

### npm Audit Results

npm audit reports vulnerabilities in Node.js dependencies with the following information:
- [npm Audit Documentation](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning)
