# Enhanced Mock path-to-regexp

This is an enhanced mock implementation of the path-to-regexp package for CI compatibility.

## Features

- Robust CI environment detection (GitHub Actions, Docker)
- Security improvements:
  - ReDoS prevention through regex limits
  - Path traversal protection
  - Input validation and sanitization
  - Anti-DoS measures
- Comprehensive error handling
- Enhanced logging for debugging
- Full API compatibility with path-to-regexp

## CI Environment Support

This mock implementation automatically detects and adapts to:
- GitHub Actions
- Docker containers
- Generic CI environments

## Usage

The mock implementation provides all standard path-to-regexp functions:
- pathToRegexp(path, [keys], [options])
- parse(path)
- compile(path)
- tokensToRegexp(tokens, [keys], [options])
- tokensToFunction(tokens)

Plus additional safety features:
- Automatic input sanitization
- Parameter validation
- Length limits for DoS prevention
- Debug logging

## Installation

This package is automatically installed by the CI workflow. No manual installation is required.
