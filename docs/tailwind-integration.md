# Tailwind CSS Integration

This document provides information about the Tailwind CSS integration in the pAIssive Income project.

## Overview

Tailwind CSS is a utility-first CSS framework that allows for rapid UI development through composable utility classes. It has been integrated into the project to enhance the styling capabilities and provide a more modern approach to CSS.

## Files and Structure

- **tailwind.config.js**: Root configuration file for Tailwind CSS that specifies content sources and theme extensions.
- **ui/tailwind.config.js**: Configuration file for the Flask UI components.
- **ui/react_frontend/tailwind.config.js**: Configuration file for the React frontend.
- **ui/static/css/tailwind.css**: Source file that includes Tailwind's base styles and imports legacy/custom styles.
- **ui/static/css/tailwind.output.css**: Generated CSS file that contains all the compiled Tailwind styles (this file is generated during the build process).
- **ui/templates/base.html**: Base HTML template that includes the link to the generated Tailwind CSS file.
- **ui/react_frontend/src/tailwind.output.css**: Generated CSS file for the React frontend.

## Build Process

The Tailwind CSS build process is integrated into the project's npm scripts:

```bash
# Build Tailwind CSS (minified)
npm run tailwind:build
# or
pnpm tailwind:build

# Build with custom configuration
pnpm tailwind:build:custom --config ./path/to/config.js --input ./path/to/input.css --output ./path/to/output.css

# Watch for changes and rebuild Tailwind CSS (both static and React)
npm run tailwind:watch
# or
pnpm tailwind:watch

# Watch only static CSS
pnpm tailwind:watch:static

# Watch only React frontend CSS
pnpm tailwind:watch:react

# Watch with custom configuration
node ui/tailwind_watch.js --static-config ./path/to/config.js --static-input ./path/to/input.css --static-output ./path/to/output.css --react-config ./path/to/react-config.js --react-input ./path/to/react-input.css --react-output ./path/to/react-output.css
```

## CI/CD Integration

The Tailwind CSS build process is integrated into the CI/CD pipeline:

1. The `js-coverage.yml` workflow builds Tailwind CSS before running tests.
2. The `frontend-vitest.yml` workflow builds Tailwind CSS before running unit tests.
3. The `frontend-e2e.yml` workflow builds Tailwind CSS before running end-to-end tests.
4. A dedicated `tailwind-build.yml` workflow ensures that Tailwind CSS is properly built and generates an artifact.

Each workflow is configured to handle errors gracefully, ensuring that the build process continues even if there are issues with the Tailwind CSS build.

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
# Standard tests
npm test
# or
pnpm test

# Run tests in parallel
pnpm test:parallel

# Run tests with custom configuration
pnpm test:custom "vitest run --passWithNoTests"

# React frontend tests with custom configuration
cd ui/react_frontend && node run_tests_with_tailwind.js --config ./tailwind.config.js --input ./src/index.css --output ./src/tailwind.output.css --parallel
```

## React Frontend Integration

The React frontend also uses Tailwind CSS for styling:

1. The React frontend has its own `tailwind.config.js` file in the `ui/react_frontend` directory.
2. The build process is integrated into the React frontend's build pipeline.
3. The Tailwind CSS output is generated in the `ui/react_frontend/src/tailwind.output.css` file.

To use Tailwind CSS in your React components:

```jsx
import React from 'react';
import './tailwind.output.css'; // Import the generated CSS

function MyComponent() {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-100 rounded-lg shadow">
      <h1 className="text-2xl font-bold text-gray-800">Hello, Tailwind!</h1>
      <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        Click me
      </button>
    </div>
  );
}

export default MyComponent;
```

## Troubleshooting

If you encounter issues with the Tailwind CSS integration:

1. Make sure all dependencies are installed: `npm install` or `pnpm install`
2. Rebuild the Tailwind CSS file: `npm run tailwind:build` or `pnpm tailwind:build`
3. Check that the output file is being generated in the correct location
4. Verify that the HTML templates are correctly linking to the output CSS file
5. For React frontend issues, check that the `tailwind.config.js` file in the `ui/react_frontend` directory is properly configured
6. Ensure that the `postcss.config.js` file is present in both the root directory and the `ui/react_frontend` directory
