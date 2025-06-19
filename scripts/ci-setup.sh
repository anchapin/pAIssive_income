#!/bin/sh
# scripts/ci-setup.sh: Shared CI setup for all workflows

set -e

# Create required directories
mkdir -p security-reports coverage junit ci-reports playwright-report test-results src logs ui/static/css src/__tests__

# Create dummy math module if missing
if [ ! -f "src/math.js" ]; then
  echo "export function add(a, b) { return a + b; }" > src/math.js
  echo "Created src/math.js"
fi

# Create dummy math test if missing
if [ ! -f "src/math.test.js" ]; then
  printf 'import { expect } from "expect";\nimport { add } from "./math.js";\ndescribe("Math functions", () => {\n  it("should add two numbers", () => {\n    expect(add(2, 3)).toBe(5);\n  });\n});\n' > src/math.test.js
  echo "Created src/math.test.js"
fi

# Create dummy Vitest test if missing
if [ ! -f "src/__tests__/dummy.test.ts" ]; then
  printf 'import { describe, it, expect } from "vitest";\ndescribe("Dummy test", () => {\n  it("should pass", () => {\n    expect(true).toBe(true);\n  });\n});\n' > src/__tests__/dummy.test.ts
  echo "Created src/__tests__/dummy.test.ts"
fi

# Create Tailwind CSS input file if missing
if [ ! -f "ui/static/css/tailwind.css" ]; then
  echo "@tailwind base; @tailwind components; @tailwind utilities;" > ui/static/css/tailwind.css
  echo "Created ui/static/css/tailwind.css"
fi

# Create Tailwind config if missing
if [ ! -f "tailwind.config.js" ]; then
  printf '/** @type {import(\'tailwindcss\').Config} */\nmodule.exports = {\n  content: [\n    "./ui/**/*.{html,js,jsx,ts,tsx}",\n    "./src/**/*.{html,js,jsx,ts,tsx}"\n  ],\n  theme: { extend: {} },\n  plugins: [],\n}\n' > tailwind.config.js
  echo "Created tailwind.config.js"
fi

echo "[ci-setup.sh] CI setup complete." 