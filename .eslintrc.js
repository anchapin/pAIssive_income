module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2022: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  ignorePatterns: [
    'dist/',
    'node_modules/',
    'build/',
    '.venv/',
    'venv/',
    '*.min.js',
  ],
  rules: {
    'quotes': ['error', 'single'],
    'no-console': 'warn',
    'no-unused-vars': 'warn',
  },
  overrides: [
    {
      files: ['**/*.test.js'],
      env: {
        jest: true,
      },
    },
    {
      files: ['ui/react_frontend/**/*.js'],
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      env: {
        browser: true,
      },
    },
  ],
};