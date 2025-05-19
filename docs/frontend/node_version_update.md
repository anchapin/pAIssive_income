# Node.js Version Update

This document outlines the update of Node.js from version 18 to version 24 in the frontend Docker configuration and describes the new dynamic version detection and fallback behavior introduced in `scripts/run-docker-compose-ci.sh`.

## Overview

As part of our dependency maintenance strategy, we've updated the Node.js version used in our frontend Docker container from 18-alpine to 24-alpine. This update ensures we're using the latest Long-Term Support (LTS) version of Node.js, which provides improved performance, security, and features.

## Changes Made

- Updated `ui/react_frontend/Dockerfile.dev` to use `node:24-alpine` instead of `node:18-alpine`
- Updated related CI/CD workflows to support Node.js 24
- Enhanced `scripts/run-docker-compose-ci.sh` with dynamic Node.js version detection and fallback mechanisms

## Dynamic Version Detection and Fallback Behavior

The `scripts/run-docker-compose-ci.sh` script now includes intelligent Node.js version detection and fallback mechanisms:

1. **Dynamic Version Detection**: The script automatically detects the Node.js version from the `Dockerfile.dev` file using pattern matching.

2. **Fallback Mechanism**: If the detected version cannot be pulled, the script tries alternative versions in this order:
   - node:24-alpine
   - node:20-alpine
   - node:18-alpine
   - node:16-alpine

3. **Dockerfile Update**: When a fallback image is used, the script automatically updates the `Dockerfile.dev` file to match the available version.

This approach ensures that CI/CD pipelines remain resilient even when specific Node.js versions are temporarily unavailable in registries or when running in environments with limited connectivity.

## Benefits

1. **Security Improvements**: Node.js 24 includes the latest security patches and improvements
2. **Performance Enhancements**: Newer versions of Node.js offer better performance and memory management
3. **Modern JavaScript Features**: Support for the latest ECMAScript features
4. **Dependency Compatibility**: Better compatibility with modern JavaScript libraries and frameworks

## Compatibility Considerations

When upgrading Node.js versions, consider the following:

1. **Package Compatibility**: Some packages may have specific Node.js version requirements
2. **Build Process**: Ensure your build process is compatible with Node.js 24
3. **CI/CD Pipelines**: Update CI/CD configurations to use Node.js 24 where applicable

## Testing

After upgrading Node.js, ensure that:

1. The application builds successfully
2. All tests pass
3. The application runs as expected in development and production environments

## References

- [Node.js 24 Release Notes](https://nodejs.org/en/blog/release/v24.0.0)
- [Node.js Release Schedule](https://nodejs.org/en/about/releases/)
