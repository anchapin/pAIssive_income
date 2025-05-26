/**
 * Tests for mock path-to-regexp implementation
 * 
 * Validates the functionality of mock path-to-regexp implementation
 * used in CI environments. These tests ensure the mock provides
 * expected behavior for path matching and parameter extraction.
 */

const pathToRegexp = require('./mock_path_to_regexp_fixed');
const path = require('path');
const fs = require('fs');

describe('Mock path-to-regexp', () => {
  beforeEach(() => {
    // Set up test environment
    process.env.CI = 'true';
    process.env.VERBOSE_LOGGING = 'true';
  });

  describe('Basic functionality', () => {
    it('should return catch-all regex for null/undefined paths', () => {
      const regex = pathToRegexp(null);
      expect(regex.toString()).toBe('/.*/');
    });

    it('should handle RegExp objects directly', () => {
      const input = /test/;
      const regex = pathToRegexp(input);
      expect(regex).toBe(input);
    });

    it('should handle basic paths', () => {
      const keys = [];
      const regex = pathToRegexp('/test', keys);
      expect(regex.toString()).toBe('/.*/');
      expect(keys).toHaveLength(0);
    });
  });

  describe('Parameter extraction', () => {
    it('should extract parameters from path', () => {
      const keys = [];
      pathToRegexp('/users/:id/posts/:postId', keys);
      expect(keys).toHaveLength(2);
      expect(keys[0].name).toBe('id');
      expect(keys[1].name).toBe('postId');
    });

    it('should limit number of parameters', () => {
      const keys = [];
      const path = '/test/' + Array(25).fill(':param').join('/');
      pathToRegexp(path, keys);
      expect(keys).toHaveLength(20); // MAX_PARAMS limit
    });
  });

  describe('Parse function', () => {
    it('should parse path into tokens', () => {
      const tokens = pathToRegexp.parse('/users/:id');
      expect(Array.isArray(tokens)).toBe(true);
      expect(tokens).toHaveLength(2);
      expect(tokens[0]).toBe('users');
      expect(tokens[1].name).toBe('id');
    });

    it('should handle empty paths', () => {
      const tokens = pathToRegexp.parse('');
      expect(Array.isArray(tokens)).toBe(true);
      expect(tokens).toHaveLength(0);
    });
  });

  describe('Compile function', () => {
    it('should compile path with parameters', () => {
      const toPath = pathToRegexp.compile('/users/:id/posts/:postId');
      const result = toPath({ id: '123', postId: '456' });
      expect(result).toBe('/users/123/posts/456');
    });

    it('should handle missing parameters', () => {
      const toPath = pathToRegexp.compile('/users/:id');
      const result = toPath({});
      expect(result).toBe('/users/');
    });

    it('should sanitize parameter values', () => {
      const toPath = pathToRegexp.compile('/users/:id');
      const result = toPath({ id: '../../../etc/passwd' });
      expect(result).toContain(encodeURIComponent('../'));
    });
  });

  describe('Match function', () => {
    it('should match exact paths', () => {
      const match = pathToRegexp.match('/users/:id');
      const result = match('/users/123');
      expect(result.isExact).toBe(true);
      expect(result.params.id).toBe('123');
    });

    it('should handle non-matching paths', () => {
      const match = pathToRegexp.match('/users/:id');
      const result = match('/posts/123');
      expect(result.isExact).toBe(false);
      expect(result.params).toEqual({});
    });
  });

  describe('Windows path handling', () => {
    it('should normalize Windows paths', () => {
      const match = pathToRegexp.match('\\users\\:id');
      const result = match('/users/123');
      expect(result.params.id).toBe('123');
    });
  });

  describe('Security features', () => {
    it('should limit path length', () => {
      const longPath = '/' + 'a'.repeat(3000);
      const keys = [];
      pathToRegexp(longPath, keys);
      expect(keys).toHaveLength(0);
    });

    it('should prevent ReDoS attacks', () => {
      const start = Date.now();
      const maliciousPath = '/test/' + ':a'.repeat(1000);
      const keys = [];
      pathToRegexp(maliciousPath, keys);
      const duration = Date.now() - start;
      expect(duration).toBeLessThan(1000); // Should complete quickly
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
        expect(fs.existsSync(fullPath)).toBe(true);
      });
    });

    it('should set proper permissions in CI', () => {
      if (process.platform !== 'win32') {
        testDirs.forEach(dir => {
          const fullPath = path.join(process.cwd(), dir);
          const stats = fs.statSync(fullPath);
          const mode = stats.mode & 0o777;
          expect(mode).toBe(0o755);
        });
      }
    });
  });
});
