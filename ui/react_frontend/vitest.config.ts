import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./tests/setup.ts",
    include: ["src/**/*.{test,spec}.{js,ts,jsx,tsx}", "tests/**/*.{test,spec}.{js,ts,jsx,tsx}"],
    exclude: ["**/tests/e2e/**", "**/node_modules/**"],
    coverage: {
      reporter: ["text", "json", "html"],
    },
  },
});