# UI Setup & Tailwind CSS Integration

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
   This generates `ui/static/css/tailwind.output.css` (including all Tailwind utilities and your legacy styles).

3. **Or watch for changes during development:**
   ```sh
   pnpm tailwind:watch
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

---

### CI/CD Integration

- The CI pipeline automatically installs dependencies and builds Tailwind CSS before tests and deployment. You do **not** need to commit generated CSS.
- If you add new templates or JS files, update `tailwind.config.js` to ensure Tailwind scans them for class usage.

---

### Notes

- `ui/static/css/tailwind.output.css` is **git-ignored** and should not be committed.
- For further customization, see the [Tailwind CSS documentation](https://tailwindcss.com/docs/installation).

---
