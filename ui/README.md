# UI Setup & Tailwind CSS Integration

## Overview

The UI module is responsible for managing the user interface of the project. It includes templates, styles, and scripts that define the look and feel of the application. This README focuses on integrating and customizing Tailwind CSS for styling.

For a detailed overview of the UI module's structure and components, see the [UI Module Documentation](../docs/ui-overview.md).

## Tailwind CSS

This project uses [Tailwind CSS](https://tailwindcss.com/) for modern utility-first styling. **Legacy styles from `style.css` are now automatically merged into Tailwind's build output.**

---

### How to Build Tailwind CSS Locally

1. **Install Node dependencies (using pnpm):**
   ```sh
   pnpm install
   ```

2. **Build Tailwind CSS once:**
   ```sh
   pnpm tailwind:build
   ```
   This generates `ui/static/css/tailwind.output.css` and `ui/react_frontend/src/tailwind.output.css` (including all Tailwind utilities and your legacy styles).

3. **Build with custom configuration:**
   ```sh
   pnpm tailwind:build:custom --config ./path/to/config.js --input ./path/to/input.css --output ./path/to/output.css
   ```

4. **Build multiple files in parallel:**
   ```sh
   pnpm tailwind:build:parallel
   ```

5. **Build with a configuration file:**
   ```sh
   pnpm tailwind:config
   ```

6. **Build with custom PostCSS plugins:**
   ```sh
   pnpm tailwind:build:postcss
   ```

7. **Build with webpack integration:**
   ```sh
   pnpm tailwind:build:webpack
   ```

8. **Build with Vite integration:**
   ```sh
   pnpm tailwind:build:vite
   ```

9. **Build multiple input/output pairs:**
   ```sh
   pnpm tailwind:build:multi
   ```

10. **Watch for changes during development (both static and React):**
    ```sh
    pnpm tailwind:watch
    ```

11. **Watch only static CSS:**
    ```sh
    pnpm tailwind:watch:static
    ```

12. **Watch only React frontend CSS:**
    ```sh
    pnpm tailwind:watch:react
    ```

13. **Advanced usage with multiple options:**
    ```sh
    node ui/tailwind_utils.js --config-file ./ui/tailwind.config.json --log-level debug --parallel --add-file ./tailwind.config.js ./ui/static/css/tailwind.css ./ui/static/css/tailwind.output.css --add-file ./ui/react_frontend/tailwind.config.js ./ui/react_frontend/src/index.css ./ui/react_frontend/src/tailwind.output.css
    ```

---

### How Tailwind & Legacy Styles Work

- The **Tailwind build output** (`tailwind.output.css`) now contains all Tailwind utility classes **plus** your custom styles from `style.css`.
- You only need to include `tailwind.output.css` in your templates:
  ```html
  <link rel="stylesheet" href="{{ url_for('static', filename='css/tailwind.output.css') }}">
  ```
- Use Tailwind classes and your custom CSS together in your HTML/Jinja templates.
- **Do not** reference `style.css` directly in templates unless you have a special reason.

---

### Customizing Tailwind

- Edit `ui/static/css/tailwind.css` to add custom CSS or enable/disable the `@import './style.css';` line as needed.
- Edit `tailwind.config.js` to configure content sources, themes, or plugins.
- Use custom configuration paths with the `tailwind:build:custom` script.
- For React frontend, use the `tailwind:build:custom` script in the `ui/react_frontend` directory.
- Create or edit `ui/tailwind.config.json` to customize default settings, logging, error handling, and more.
- Add custom PostCSS plugins in `ui/postcss.config.js` or through the configuration file.
- Integrate with webpack or Vite using the appropriate build scripts.

---

### CI/CD Integration

- The CI pipeline automatically installs dependencies and builds Tailwind CSS before tests and deployment. You do **not** need to commit generated CSS.
- If you add new templates or JS files, update `tailwind.config.js` to ensure Tailwind scans them for class usage.

---

### Testing with Tailwind

- Run tests with Tailwind CSS build:
  ```sh
  pnpm test
  ```

- Run tests in parallel:
  ```sh
  pnpm test:parallel
  ```

- Run tests with custom configuration:
  ```sh
  pnpm test:custom "your custom test command"
  ```

- For React frontend, use the `run_tests_with_tailwind.js` script with custom options:
  ```sh
  cd ui/react_frontend && node run_tests_with_tailwind.js --config ./tailwind.config.js --input ./src/index.css --output ./src/tailwind.output.css --parallel
  ```

---

### Notes

- `ui/static/css/tailwind.output.css` is **git-ignored** and should not be committed.
- For further customization, see the [Tailwind CSS documentation](https://tailwindcss.com/docs/installation).
- For more details on Tailwind CSS integration, see the [Tailwind Integration Documentation](../docs/tailwind-integration.md).
- For information on the enhanced features, see the [Tailwind Enhanced Features Documentation](../docs/tailwind-enhanced-features.md).

### Advanced Features

- **Configuration File**: Use a JSON configuration file to store default settings.
- **Error Handling**: Robust error handling with retries and detailed logging.
- **Multiple Files**: Process multiple input/output file pairs in a single run.
- **Build Tool Integration**: Integrate with webpack or Vite for advanced build pipelines.
- **Custom PostCSS Plugins**: Add custom PostCSS plugins for advanced CSS processing.
- **Parallel Processing**: Build multiple files in parallel for better performance.

---
