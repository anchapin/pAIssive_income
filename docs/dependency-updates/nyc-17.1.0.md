# nyc 17.1.0 Update

## Overview

This document describes the update of the nyc (Istanbul) code coverage tool from version 15.1.0 to 17.1.0.

## Changes

### Breaking Changes

- **Node.js Version Requirement**: nyc 17.1.0 requires Node.js 18 or higher (previously 8.9+)
- **Updated Dependencies**:
  - `foreground-child` updated from ^2.0.0 to ^3.3.0
  - `istanbul-lib-instrument` updated from ^4.0.0 to ^6.0.2

### Bug Fixes

- Reduced size of serialized JSON output
- Addressed security alerts in dependencies

## Implementation

The following changes were made to support nyc 17.1.0:

1. Updated package.json and package-lock.json to use nyc 17.1.0
2. Added Node.js version requirement to package.json engines field
3. Created .nvmrc and .node-version files to specify Node.js 18
4. Updated GitHub Actions workflows to use Node.js 18 or higher
5. Added documentation about the Node.js version requirement

## Testing

The update has been tested with our existing JavaScript test suite to ensure compatibility. All tests continue to pass with the new version.

## References

- [nyc GitHub Repository](https://github.com/istanbuljs/nyc)
- [nyc 17.1.0 Release Notes](https://github.com/istanbuljs/nyc/releases/tag/nyc-v17.1.0)
- [nyc 17.0.0 Release Notes](https://github.com/istanbuljs/nyc/releases/tag/nyc-v17.0.0)
