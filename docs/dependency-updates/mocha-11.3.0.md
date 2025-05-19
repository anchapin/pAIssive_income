# Mocha 11.3.0 Update

## Overview

This document details the update of the Mocha JavaScript testing framework from version 10.8.2 to 11.3.0 in the pAIssive Income project.

## Update Details

- **Package Name:** mocha
- **Previous Version:** 10.8.2
- **New Version:** 11.3.0
- **Location:** Root `package.json` (devDependencies)
- **PR:** [#182](https://github.com/anchapin/pAIssive_income/pull/182)

## Changes in the New Version

Mocha 11.3.0 includes several improvements and changes:

### Features
- Added option to use POSIX exit code upon fatal signal (#4989)

### Documentation
- Deploy new site alongside old one (#5360)
- Mention explicit browser support range (#5354)
- Update Node.js version requirements for 11.x (#5329)

### Chores
- Remove prerelease setting in release-please config (#5363)

## Impact Assessment

### Breaking Changes

Mocha 11.x has updated Node.js version requirements:
- Now requires Node.js ^18.18.0 || ^20.9.0 || >=21.1.0
- Previous versions supported Node.js >= 14.0.0

### Dependencies

The update includes changes to several dependencies:
- Switched from ansi-colors to picocolors
- Updated chokidar to v4
- Updated various other dependencies

## Testing

The update has been tested with our existing JavaScript test suite to ensure compatibility. All tests continue to pass with the new version.

## Implementation

The update was implemented by:
1. Updating the version in `package.json` from `^10.4.0` to `^11.3.0`
2. Updating the lock files (`package-lock.json` and `pnpm-lock.yaml`)
3. Running the test suite to verify compatibility

## References

- [Mocha 11.3.0 Release Notes](https://github.com/mochajs/mocha/releases/tag/v11.3.0)
- [Mocha GitHub Repository](https://github.com/mochajs/mocha)
- [Node.js Version Requirements](https://github.com/mochajs/mocha/blob/main/package.json)
