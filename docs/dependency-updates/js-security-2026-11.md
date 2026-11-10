# JavaScript lockfile security update (November 2026)

## Overview

The root, `ui/react_frontend` and `sdk/javascript` lockfiles were refreshed with `pnpm update`, staying inside the existing semver ranges, to pick up patched releases. Changes:

- **Root `package-lock.json`:** regenerated, because it was out of sync with `package.json`.
- **`ui/react_frontend` webpack pin:** 5.99.9 → 5.104.1.
- **`pnpm.overrides`:** move transitive `yaml` 2.x and `underscore` 1.13.x to patched versions.

- **PR:** [#425](https://github.com/anchapin/pAIssive_income/pull/425)

## Held back (fix needs a major upgrade)

- vitest 3 → 4 (root) and 1 → 3 (`ui/react_frontend`), which also holds back vite, esbuild and tinypool
- react-router 6 → 7 (via react-router-dom 6)
- react-scripts 5 transitive packages: postcss 7, svgo 1, nth-check 1, serialize-javascript, webpack-dev-server 4
- uuid 8 → 11
- zod 3 → 4

braces and deepmerge have no fixed release yet.
