# TailwindCSS v4 Migration Guide

This guide covers the migration from TailwindCSS v3 to v4 in the pAIssive Income project.

## Migration Status

✅ **COMPLETED**: The project has been successfully upgraded to TailwindCSS v4.1.10 (December 2024)

## Overview

TailwindCSS v4 introduces a new architecture with separate packages for the CLI and PostCSS integration, providing improved performance and better developer experience.

## What Changed

### Package Structure
- **Old (v3)**: Single `tailwindcss` package
- **New (v4)**: Separate packages:
  - `tailwindcss@^4.1.10` - Core framework
  - `@tailwindcss/cli@^4.1.10` - Command-line interface
  - `@tailwindcss/postcss@^4.1.10` - PostCSS plugin

### PostCSS Configuration
**Before (v3):**
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**After (v4):**
```javascript
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};
```

### CLI Commands
**Before (v3):**
```bash
npx tailwindcss -c tailwind.config.js -i input.css -o output.css
```

**After (v4):**
```bash
npx @tailwindcss/cli -c tailwind.config.js -i input.css -o output.css
```

## Migration Steps

✅ **COMPLETED**: All migration steps have been successfully implemented.

### 1. Update Dependencies ✅
```bash
# Install new v4 packages
pnpm add -D tailwindcss@^4.1.10 @tailwindcss/cli@^4.1.10 @tailwindcss/postcss@^4.1.10

# Remove old v3 package if needed
pnpm remove tailwindcss@3.x
```

**Status**: Dependencies updated in package.json and pnpm-lock.yaml

### 2. Update PostCSS Configuration ✅
Update your `postcss.config.js` file:
```javascript
// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};
```

**Status**: PostCSS configuration updated to use @tailwindcss/postcss plugin

### 3. Update Build Scripts ✅
Update any build scripts or npm scripts that use the TailwindCSS CLI:

**package.json:**
```json
{
  "scripts": {
    "tailwind:build": "npx @tailwindcss/cli -c tailwind.config.js -i ./ui/static/css/tailwind.css -o ./ui/static/css/tailwind.output.css --minify",
    "tailwind:watch": "npx @tailwindcss/cli -c tailwind.config.js -i ./ui/static/css/tailwind.css -o ./ui/static/css/tailwind.output.css --watch"
  }
}
```

**Status**: Build scripts updated in package.json to use @tailwindcss/cli

### 4. Update Build Tools ✅
If using custom build tools or scripts, update them to use the new CLI:

**ui/tailwind_utils.js** (example):
```javascript
// Use @tailwindcss/cli instead of tailwindcss
const command = `npx @tailwindcss/cli -c ${configPath} -i ${inputPath} -o ${outputPath}`;
```

**Status**: Build utilities updated in ui/tailwind_utils.js to use new CLI commands

## Benefits of v4

### Performance Improvements
- **Faster Builds**: Improved build performance with better caching
- **Reduced Bundle Size**: More efficient CSS generation
- **Better Tree Shaking**: Improved dead code elimination

### Developer Experience
- **Better Error Messages**: More helpful error reporting
- **Improved Watch Mode**: Faster file watching and rebuilding
- **Enhanced CLI**: More powerful command-line interface

### Architecture Benefits
- **Modular Design**: Separate packages for different use cases
- **Better Integration**: Improved integration with build tools
- **Future-Proof**: Better foundation for future features

## Compatibility

### Configuration Files
- Most TailwindCSS v3 configuration files work with v4
- No changes needed to `tailwind.config.js` in most cases
- CSS files and HTML templates remain unchanged

### CSS Classes
- All existing TailwindCSS classes continue to work
- No breaking changes to utility classes
- Existing styles remain compatible

## Troubleshooting

### Common Issues

**1. CLI Not Found**
```bash
Error: Cannot find module '@tailwindcss/cli'
```
**Solution:** Install the CLI package: `pnpm add -D @tailwindcss/cli`

**2. PostCSS Plugin Error**
```bash
Error: Cannot find module '@tailwindcss/postcss'
```
**Solution:** Update `postcss.config.js` to use `@tailwindcss/postcss`

**3. Build Script Fails**
```bash
Error: 'tailwindcss' is not recognized
```
**Solution:** Update build scripts to use `@tailwindcss/cli`

### Verification Steps

1. **Check Dependencies:**
   ```bash
   pnpm list tailwindcss @tailwindcss/cli @tailwindcss/postcss
   ```

2. **Test Build:**
   ```bash
   pnpm tailwind:build
   ```

3. **Verify Output:**
   Check that CSS files are generated correctly

## Resources

- [TailwindCSS v4 Documentation](https://tailwindcss.com/docs)
- [Migration Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Project TailwindCSS Integration](./tailwind-integration.md)

## Support

If you encounter issues during migration:
1. Check the [troubleshooting section](./tailwind-integration.md#troubleshooting)
2. Review the [FAQ](../07_troubleshooting_and_faq/faq.md)
3. Open an issue with details about the problem
