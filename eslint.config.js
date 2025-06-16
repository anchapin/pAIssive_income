export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.venv/**',
      '**/venv/**',
      '**/__pycache__/**',
      '**/*.pyc',
      '**/migrations/**',
      '**/coverage/**',
      '**/junit/**',
      '**/logs/**',
      '**/security-reports/**',
      '**/.git/**',
      '**/ui/react_frontend/tests/verify_mock_path_to_regexp.js'
    ],
  },
  {
    files: ['**/*.js', '**/*.jsx'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      },
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        URL: 'readonly',
        URLSearchParams: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        AbortController: 'readonly',

        // Node.js globals
        process: 'readonly',
        module: 'readonly',
        require: 'readonly',
        __dirname: 'readonly',
        Buffer: 'readonly',
        global: 'readonly',

        // Testing globals
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        before: 'readonly',
        after: 'readonly',

        // Library globals
        $: 'readonly',
        bootstrap: 'readonly',
        Chart: 'readonly',
        React: 'readonly'
      }
    },
    rules: {
      'no-unused-vars': 'warn',
      'no-console': 'warn',
      'semi': ['error', 'always'],
      'quotes': ['error', 'single'],
    },
  },
];