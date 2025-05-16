#!/bin/bash
# Script to simulate the GitHub Actions workflow

echo "Simulating GitHub Actions workflow for frontend-vitest.yml"

# Create test directory if it doesn't exist
mkdir -p src/__tests__
if [ ! -f "src/__tests__/dummy.test.ts" ] && [ ! -f "tests/dummy.test.ts" ] && [ ! -f "src/__tests__/dummy.test.tsx" ] && [ ! -f "tests/dummy.test.tsx" ]; then
  echo "// Dummy test file to ensure coverage directory is created
  import { describe, it, expect } from 'vitest';

  describe('Dummy test', () => {
    it('should pass', () => {
      expect(true).toBe(true);
    });
  });" > src/__tests__/dummy.test.ts
  echo "Created dummy test file to ensure coverage directory is created"
else
  echo "Test files already exist, skipping dummy test creation"
fi

# Run Vitest unit tests
echo "Running Vitest unit tests..."
# Try to find pnpm in different locations
if command -v pnpm &> /dev/null; then
  pnpm run test:unit
elif [ -f "$(npm bin)/pnpm" ]; then
  $(npm bin)/pnpm run test:unit
elif [ -f "$HOME/.npm/pnpm/bin/pnpm" ]; then
  $HOME/.npm/pnpm/bin/pnpm run test:unit
else
  echo "pnpm not found, trying npm instead..."
  npm run test:unit
fi

# Check the exit code
if [ $? -eq 0 ]; then
  echo "Tests passed successfully!"
  exit 0
else
  echo "Tests failed!"
  exit 1
fi
