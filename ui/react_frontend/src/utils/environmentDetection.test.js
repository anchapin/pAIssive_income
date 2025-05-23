/**
 * Environment Detection Tests
 *
 * This file contains tests for the environment detection functionality.
 * It tests detection of different environments and platforms.
 */

// Mock the global objects
jest.mock('os', () => ({
  platform: jest.fn(),
  release: jest.fn(),
  tmpdir: jest.fn(),
  homedir: jest.fn(),
  hostname: jest.fn(),
  userInfo: jest.fn(),
  totalmem: jest.fn(),
  freemem: jest.fn(),
  cpus: jest.fn(),
  type: jest.fn()
}));

// Import the module to test
import {
  detectEnvironment,
  useEnvironment,
  getPathSeparator,
  getPlatformPath,
  getEnvironmentInfo
} from './environmentDetection';

describe('Environment Detection Module', () => {
  // Store original environment variables and window object
  const originalEnv = { ...process.env };
  const originalWindow = global.window;
  const originalNavigator = global.navigator;

  // Setup before each test
  beforeEach(() => {
    // Reset environment variables
    process.env = { ...originalEnv };

    // Mock window and navigator for browser tests
    global.window = {
      devicePixelRatio: 2,
      localStorage: {},
      sessionStorage: {}
    };

    global.navigator = {
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      platform: 'Win32',
      maxTouchPoints: 0,
      connection: {
        effectiveType: '4g',
        downlink: 10,
        rtt: 50,
        saveData: false
      }
    };

    // Mock document for browser tests
    global.document = {
      cookie: '',
      createElement: jest.fn().mockImplementation(() => ({
        getContext: jest.fn().mockReturnValue({})
      }))
    };

    // Mock performance for browser tests
    global.performance = {
      memory: {
        jsHeapSizeLimit: 2000000000,
        totalJSHeapSize: 1000000000,
        usedJSHeapSize: 500000000
      },
      navigation: {
        redirectCount: 0,
        type: 0
      },
      timing: {
        navigationStart: 1625000000000,
        loadEventEnd: 1625000001000
      }
    };

    // Mock screen for browser tests
    global.screen = {
      width: 1920,
      height: 1080,
      availWidth: 1920,
      availHeight: 1040,
      colorDepth: 24,
      orientation: {
        type: 'landscape-primary'
      }
    };

    // Mock WebGL objects
    global.WebGLRenderingContext = {};
    global.RTCPeerConnection = {};
    global.WebAssembly = {};
  });

  // Cleanup after each test
  afterEach(() => {
    // Restore environment variables
    process.env = { ...originalEnv };

    // Restore window and navigator
    global.window = originalWindow;
    global.navigator = originalNavigator;

    // Clean up other global mocks
    delete global.document;
    delete global.performance;
    delete global.screen;
    delete global.WebGLRenderingContext;
    delete global.RTCPeerConnection;
    delete global.WebAssembly;
  });

  describe('detectEnvironment Function', () => {
    it('should detect browser environment', () => {
      // Act
      const result = detectEnvironment();

      // Assert
      expect(result.isBrowser).toBe(true);
      expect(result.isWindows).toBe(true);
      expect(result.isMacOS).toBe(false);
      expect(result.isLinux).toBe(false);
    });

    it('should detect macOS in browser environment', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

      // Act
      const result = detectEnvironment();

      // Assert
      expect(result.isBrowser).toBe(true);
      expect(result.isWindows).toBe(false);
      expect(result.isMacOS).toBe(true);
      expect(result.isLinux).toBe(false);
    });

    it('should detect Linux in browser environment', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

      // Act
      const result = detectEnvironment();

      // Assert
      expect(result.isBrowser).toBe(true);
      expect(result.isWindows).toBe(false);
      expect(result.isMacOS).toBe(false);
      expect(result.isLinux).toBe(true);
    });

    it('should detect mobile devices', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1';

      // Act
      const result = detectEnvironment();

      // Assert
      expect(result.isBrowser).toBe(true);
      expect(result.isMobile).toBe(true);
      expect(result.isIOS).toBe(true);
      expect(result.isAndroid).toBe(false);
    });

    it('should detect Android devices', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36';

      // Act
      const result = detectEnvironment();

      // Assert
      expect(result.isBrowser).toBe(true);
      expect(result.isMobile).toBe(true);
      expect(result.isIOS).toBe(false);
      expect(result.isAndroid).toBe(true);
    });

    it('should detect Electron environment', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) electron/13.1.7 Chrome/91.0.4472.124 Electron/13.1.7 Safari/537.36';

      // Act
      const result = detectEnvironment();

      // Assert
      expect(result.isBrowser).toBe(true);
      expect(result.isElectron).toBe(true);
    });
  });

  describe('getPathSeparator Function', () => {
    it('should return backslash for Windows', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

      // Act
      const result = getPathSeparator();

      // Assert
      expect(result).toBe('\\');
    });

    it('should return forward slash for non-Windows', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

      // Act
      const result = getPathSeparator();

      // Assert
      expect(result).toBe('/');
    });
  });

  describe('getPlatformPath Function', () => {
    it('should convert paths for Windows', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

      // Act
      const result = getPlatformPath('/path/to/file');

      // Assert
      expect(result).toBe('\\path\\to\\file');
    });

    it('should convert paths for non-Windows', () => {
      // Arrange
      global.navigator.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

      // Act
      const result = getPlatformPath('\\path\\to\\file');

      // Assert
      expect(result).toBe('/path/to/file');
    });
  });

  describe('getEnvironmentInfo Function', () => {
    it('should return comprehensive environment information', () => {
      // Act
      const result = getEnvironmentInfo();

      // Assert
      expect(result).toBeDefined();
      expect(result.browser).toBeDefined();
      expect(result.network).toBeDefined();
      expect(result.screen).toBeDefined();
      expect(result.features).toBeDefined();
      expect(result.performance).toBeDefined();
    });
  });
});
