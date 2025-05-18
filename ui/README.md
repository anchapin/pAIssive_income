# UI Setup & Tailwind CSS Integration

## Tailwind CSS

This project uses [Tailwind CSS](https://tailwindcss.com/) for modern utility-first styling.

### How to Build Tailwind CSS

1. **Install Node dependencies (using pnpm):**

   ```
   pnpm install
   ```

2. **Build Tailwind CSS once:**

   ```
   pnpm tailwind:build
   ```

   This will generate `ui/static/css/tailwind.output.css`.

3. **Or watch for changes during development:**

   ```
   pnpm tailwind:watch
   ```

### How to Use Tailwind CSS in Templates

- In your HTML/Jinja templates in `ui/templates/`, include the generated CSS:

  ```html
  <link rel="stylesheet" href="{{ url_for('static', filename='css/tailwind.output.css') }}">
  ```

- You can use Tailwind utility classes directly in your templates.

- The original `style.css` remains available for custom or legacy styles.

### Customizing Tailwind

- Edit `ui/static/css/tailwind.css` to add custom CSS or import additional Tailwind plugins.
- Edit `tailwind.config.js` to configure content sources, themes, or plugins.

### Notes

- Do **not** commit `tailwind.output.css` if your `.gitignore` is set up to ignore built assets.
- If you add new templates or JS files, make sure their paths are included in `tailwind.config.js` under `content`.

---
