import js from '@eslint/js';
import pluginPrettier from "eslint-plugin-prettier";

export default [
  // 1. Base config
  js.configs.recommended,

  // 2. Ignores: node_modules, dist, build
  {
    ignores: ['**/node_modules/**', '**/dist/**', '**/build/**'],
  },

  // 3. Main JS file rules block
  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        navigator: 'readonly',
        screen: 'readonly',
        performance: 'readonly',
        fetch: 'readonly',
        URL: 'readonly',
        URLSearchParams: 'readonly',
        AbortController: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        Blob: 'readonly',
        FormData: 'readonly',
        Headers: 'readonly',
        Request: 'readonly',
        Response: 'readonly',

        // Node.js globals
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        global: 'readonly',
        require: 'readonly',
        module: 'readonly',
        exports: 'readonly',

        // Common library globals
        $: 'readonly',
        jQuery: 'readonly',
        bootstrap: 'readonly',
        Chart: 'readonly',

        // Mock/test globals
        verboseLogging: 'readonly',
        isDockerEnvironment: 'readonly',
        express: 'readonly',
        cors: 'readonly',
      },
    },
    rules: {
      // Relax some rules for development
      'no-unused-vars': ['warn', {
        argsIgnorePattern: '^_|^error$|^e$',
        varsIgnorePattern: '^_|^error$|^e$'
      }],
      'no-undef': 'warn',
      'no-control-regex': 'warn',
      'no-useless-escape': 'warn',
      'no-unreachable': 'warn',
    },
  },

  // 4. Test files globals block
  {
    files: [
      '**/*.test.js', '**/*.spec.js',
      '**/*.test.jsx', '**/*.spec.jsx',
      '**/*.test.ts', '**/*.spec.ts'
    ],
    languageOptions: {
      globals: {
        // Jest globals
        describe: 'readonly',
        it: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        jest: 'readonly',

        // Additional test globals
        assert: 'readonly',
        chai: 'readonly',
        sinon: 'readonly',
      },
    },
  },

  // 5. JSX/TSX file parser/global block
  {
    files: ['**/*.jsx', '**/*.tsx'],
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        React: 'readonly',
        ReactDOM: 'readonly',
      },
    },
  },

  // 6. tailwind_utils.js rule override block
  {
    files: ['ui/tailwind_utils.js'],
    rules: {
      // Allow reserved keywords in this specific file
      'no-unused-vars': 'off',
    },
  },

  // 7. Ignores list block (duplicates, broad patterns, etc.)
  {
    ignores: [
      'node_modules/',
      'dist/',
      'build/',
      'coverage/',
      '**/*.min.js',
      '.git/',
      'logs/',
      'playwright-report/',
      '__pycache__/',
      '*.bak',
      'tatus', // Seems to be a git status output file
    ],
  },

  // 8. Prettier integration block
  {
    plugins: { prettier: pluginPrettier },
    rules: { "prettier/prettier": "error" },
    extends: ["plugin:prettier/recommended"],
  },
];