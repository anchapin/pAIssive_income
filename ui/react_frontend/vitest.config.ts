import { defineConfig } from "vitest/config";
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./tests/setup.ts",
    include: ["src/**/*.{test,spec}.{js,ts,jsx,tsx}", "tests/**/*.{test,spec}.{js,ts,jsx,tsx}"],
    exclude: ["**/tests/e2e/**", "**/node_modules/**", "**/tests/mock_api_server.test.js"],
    coverage: {
      reporter: ["text", "json", "html"],
    },
  },
});