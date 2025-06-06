/**
 * Tests for mock path-to-regexp implementation
 * 
 * Validates that our mock implementation works correctly in CI environments
 */

const assert = require('assert').strict;
const pathToRegexp = require('./mock_path_to_regexp_fixed');
const path = require('path');
const fs = require('fs');

describe('Mock path-to-regexp', () => {
  beforeEach(() => {
    // Clear keys array before each test
    process.env.CI = 'true';
    process.env.VERBOSE_LOGGING = 'true';
  });

  describe('Basic functionality', () => {
    it('should return catch-all regex for null/undefined paths', () => {
      const regex = pathToRegexp(null);
      assert.equal(regex.toString(), '/.*/');
    });

    it('should handle RegExp objects directly', () => {
      const input = /test/;
      const regex = pathToRegexp(input);
      assert.equal(regex, input);
    });

    it('should handle basic paths', () => {
      const keys = [];
      const regex = pathToRegexp('/test', keys);
      assert.equal(regex.toString(), '/.*/');
      assert.equal(keys.length, 0);
    });
  });

  describe('Parameter extraction', () => {
    it('should extract parameters from path', () => {
      const keys = [];
      pathToRegexp('/users/:id/posts/:postId', keys);
      assert.equal(keys.length, 2);
      assert.equal(keys[0].name, 'id');
      assert.equal(keys[1].name, 'postId');
    });

    it('should limit number of parameters', () => {
      const keys = [];
      const path = '/test/' + Array(25).fill(':param').join('/');
      pathToRegexp(path, keys);
      assert.equal(keys.length, 20); // MAX_PARAMS limit
    });
  });

  describe('Parse function', () => {
    it('should parse path into tokens', () => {
      const tokens = pathToRegexp.parse('/users/:id');
      assert(Array.isArray(tokens));
      assert.equal(tokens.length, 2);
      assert.equal(tokens[0], 'users');
      assert.equal(tokens[1].name, 'id');
    });

    it('should handle empty paths', () => {
      const tokens = pathToRegexp.parse('');
      assert(Array.isArray(tokens));
      assert.equal(tokens.length, 0);
    });
  });

  describe('Compile function', () => {
    it('should compile path with parameters', () => {
      const toPath = pathToRegexp.compile('/users/:id/posts/:postId');
      const result = toPath({ id: '123', postId: '456' });
      assert.equal(result, '/users/123/posts/456');
    });

    it('should handle missing parameters', () => {
      const toPath = pathToRegexp.compile('/users/:id');
      const result = toPath({});
      assert.equal(result, '/users/');
    });

    it('should sanitize parameter values', () => {
      const toPath = pathToRegexp.compile('/users/:id');
      const result = toPath({ id: '../../../etc/passwd' });
      assert(result.includes(encodeURIComponent('../')));
    });
  });

  describe('Match function', () => {
    it('should match exact paths', () => {
      const match = pathToRegexp.match('/users/:id');
      const result = match('/users/123');
      assert.equal(result.isExact, true);
      assert.equal(result.params.id, '123');
    });

    it('should handle non-matching paths', () => {
      const match = pathToRegexp.match('/users/:id');
      const result = match('/posts/123');
      assert.equal(result.isExact, false);
      assert.deepEqual(result.params, {});
    });
  });

  describe('Windows path handling', () => {
    it('should normalize Windows paths', () => {
      const match = pathToRegexp.match('\\users\\:id');
      const result = match('/users/123');
      assert.equal(result.params.id, '123');
    });
  });

  describe('Security features', () => {
    it('should limit path length', () => {
      const longPath = '/' + 'a'.repeat(3000);
      const keys = [];
      pathToRegexp(longPath, keys);
      assert(keys.length === 0);
    });

    it('should prevent ReDoS attacks', () => {
      const start = Date.now();
      const maliciousPath = '/test/' + ':a'.repeat(1000);
      const keys = [];
      pathToRegexp(maliciousPath, keys);
      const duration = Date.now() - start;
      assert(duration < 1000); // Should complete quickly
    });
  });

  describe('CI compatibility', () => {
    const testDirs = [
      'logs',
      'test-results',
      'playwright-report'
    ];

    it('should create necessary directories', () => {
      testDirs.forEach(dir => {
        const fullPath = path.join(process.cwd(), dir);
        assert(fs.existsSync(fullPath));
      });
    });

    it('should set proper permissions in CI', () => {
      if (process.platform !== 'win32') {
        testDirs.forEach(dir => {
          const fullPath = path.join(process.cwd(), dir);
          const stats = fs.statSync(fullPath);
          const mode = stats.mode & 0o777;
          assert.equal(mode, 0o755);
        });
      }
    });
  });
});
