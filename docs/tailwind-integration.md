# Tailwind CSS Integration

This document provides information about the Tailwind CSS integration in the pAIssive Income project.

## Overview

Tailwind CSS is a utility-first CSS framework that allows for rapid UI development through composable utility classes. It has been integrated into the project to enhance the styling capabilities and provide a more modern approach to CSS.

## Files and Structure

- **tailwind.config.js**: Configuration file for Tailwind CSS that specifies content sources and theme extensions.
- **ui/static/css/tailwind.css**: Source file that includes Tailwind's base styles and imports legacy/custom styles.
- **ui/static/css/tailwind.output.css**: Generated CSS file that contains all the compiled Tailwind styles (this file is generated during the build process).
- **ui/templates/base.html**: Base HTML template that includes the link to the generated Tailwind CSS file.

## Build Process

The Tailwind CSS build process is integrated into the project's npm scripts:

```bash
# Build Tailwind CSS (minified)
npm run tailwind:build
# or
pnpm tailwind:build

# Watch for changes and rebuild Tailwind CSS
npm run tailwind:watch
# or
pnpm tailwind:watch
```

## CI/CD Integration

The Tailwind CSS build process is integrated into the CI/CD pipeline:

1. The `js-coverage.yml` workflow builds Tailwind CSS before running tests.
2. A dedicated `tailwind-build.yml` workflow ensures that Tailwind CSS is properly built and generates an artifact.

## Usage

To use Tailwind CSS in your HTML templates:

1. Make sure the Tailwind CSS output file is linked in your HTML:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/tailwind.output.css') }}">
```

2. Use Tailwind utility classes in your HTML elements:

```html
<div class="flex items-center justify-between p-4 bg-gray-100 rounded-lg shadow">
  <h1 class="text-2xl font-bold text-gray-800">Hello, Tailwind!</h1>
  <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Click me
  </button>
</div>
```

## Customization

To customize Tailwind CSS, edit the `tailwind.config.js` file. You can extend the theme, add plugins, or modify the content sources.

## Testing

The integration includes tests to ensure that Tailwind CSS is properly set up:

- Verifies the existence of configuration and source files
- Checks that the build process generates the output CSS file
- Validates that the source file contains the required Tailwind directives

Run the tests with:

```bash
npm test
# or
pnpm test
```

## Troubleshooting

If you encounter issues with the Tailwind CSS integration:

1. Make sure all dependencies are installed: `npm install` or `pnpm install`
2. Rebuild the Tailwind CSS file: `npm run tailwind:build` or `pnpm tailwind:build`
3. Check that the output file is being generated in the correct location
4. Verify that the HTML templates are correctly linking to the output CSS file
