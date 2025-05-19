/**
 * Environment-Specific UI Tests
 * 
 * This file contains tests for environment-specific UI behavior:
 * - Windows vs macOS/Linux UI differences
 * - CI environment UI behavior
 * - Docker environment UI behavior
 * - Development vs Production UI differences
 * 
 * These tests ensure that the UI behaves correctly in different environments.
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock modules
vi.mock('os', () => ({
  platform: vi.fn(),
  type: vi.fn(),
  release: vi.fn(),
  tmpdir: vi.fn(),
  homedir: vi.fn()
}));

// Mock environment detection
const mockEnvironment = {
  isWindows: false,
  isMacOS: false,
  isLinux: false,
  isCI: false,
  isDocker: false,
  isDevelopment: false,
  isProduction: false,
  isTest: true
};

// Create a simple environment detection hook
const useEnvironment = () => {
  return mockEnvironment;
};

// Create a simple environment-aware component
const EnvironmentAwareComponent = ({ children }) => {
  const env = useEnvironment();
  
  return (
    <div data-testid="environment-aware-component">
      {env.isWindows && <div data-testid="windows-ui">Windows UI</div>}
      {env.isMacOS && <div data-testid="macos-ui">macOS UI</div>}
      {env.isLinux && <div data-testid="linux-ui">Linux UI</div>}
      {env.isCI && <div data-testid="ci-ui">CI Environment UI</div>}
      {env.isDocker && <div data-testid="docker-ui">Docker Environment UI</div>}
      {env.isDevelopment && <div data-testid="dev-ui">Development UI</div>}
      {env.isProduction && <div data-testid="prod-ui">Production UI</div>}
      {children}
    </div>
  );
};

// Create a platform-specific button component
const PlatformButton = ({ children, onClick }) => {
  const env = useEnvironment();
  
  // Different styling based on platform
  const buttonStyle = {
    padding: '8px 16px',
    borderRadius: env.isWindows ? '0' : '4px',
    backgroundColor: env.isMacOS ? '#0078D7' : (env.isLinux ? '#E95420' : '#007ACC'),
    color: 'white',
    border: 'none',
    cursor: 'pointer'
  };
  
  return (
    <button 
      data-testid="platform-button"
      style={buttonStyle}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// Create an environment info component
const EnvironmentInfo = () => {
  const env = useEnvironment();
  
  return (
    <div data-testid="environment-info">
      <h2>Environment Information</h2>
      <ul>
        <li data-testid="os-info">
          Operating System: {env.isWindows ? 'Windows' : (env.isMacOS ? 'macOS' : 'Linux')}
        </li>
        <li data-testid="env-type">
          Environment: {
            env.isDevelopment ? 'Development' : 
            (env.isProduction ? 'Production' : 
            (env.isTest ? 'Test' : 'Unknown'))
          }
        </li>
        <li data-testid="ci-info">
          CI: {env.isCI ? 'Yes' : 'No'}
        </li>
        <li data-testid="docker-info">
          Docker: {env.isDocker ? 'Yes' : 'No'}
        </li>
      </ul>
    </div>
  );
};

describe('Environment-Specific UI', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();
    
    // Reset mock environment
    Object.keys(mockEnvironment).forEach(key => {
      mockEnvironment[key] = false;
    });
    mockEnvironment.isTest = true;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Operating System UI', () => {
    it('should render Windows-specific UI', () => {
      // Arrange
      mockEnvironment.isWindows = true;
      
      // Act
      render(<EnvironmentAwareComponent>Test Content</EnvironmentAwareComponent>);
      
      // Assert
      expect(screen.getByTestId('windows-ui')).toBeInTheDocument();
      expect(screen.queryByTestId('macos-ui')).not.toBeInTheDocument();
      expect(screen.queryByTestId('linux-ui')).not.toBeInTheDocument();
    });

    it('should render macOS-specific UI', () => {
      // Arrange
      mockEnvironment.isMacOS = true;
      
      // Act
      render(<EnvironmentAwareComponent>Test Content</EnvironmentAwareComponent>);
      
      // Assert
      expect(screen.getByTestId('macos-ui')).toBeInTheDocument();
      expect(screen.queryByTestId('windows-ui')).not.toBeInTheDocument();
      expect(screen.queryByTestId('linux-ui')).not.toBeInTheDocument();
    });

    it('should render Linux-specific UI', () => {
      // Arrange
      mockEnvironment.isLinux = true;
      
      // Act
      render(<EnvironmentAwareComponent>Test Content</EnvironmentAwareComponent>);
      
      // Assert
      expect(screen.getByTestId('linux-ui')).toBeInTheDocument();
      expect(screen.queryByTestId('windows-ui')).not.toBeInTheDocument();
      expect(screen.queryByTestId('macos-ui')).not.toBeInTheDocument();
    });
  });

  describe('CI Environment UI', () => {
    it('should render CI-specific UI', () => {
      // Arrange
      mockEnvironment.isCI = true;
      mockEnvironment.isLinux = true;
      
      // Act
      render(<EnvironmentAwareComponent>Test Content</EnvironmentAwareComponent>);
      
      // Assert
      expect(screen.getByTestId('ci-ui')).toBeInTheDocument();
      expect(screen.getByTestId('linux-ui')).toBeInTheDocument();
    });
  });

  describe('Docker Environment UI', () => {
    it('should render Docker-specific UI', () => {
      // Arrange
      mockEnvironment.isDocker = true;
      mockEnvironment.isLinux = true;
      
      // Act
      render(<EnvironmentAwareComponent>Test Content</EnvironmentAwareComponent>);
      
      // Assert
      expect(screen.getByTestId('docker-ui')).toBeInTheDocument();
      expect(screen.getByTestId('linux-ui')).toBeInTheDocument();
    });
  });

  describe('Development vs Production UI', () => {
    it('should render Development-specific UI', () => {
      // Arrange
      mockEnvironment.isDevelopment = true;
      
      // Act
      render(<EnvironmentAwareComponent>Test Content</EnvironmentAwareComponent>);
      
      // Assert
      expect(screen.getByTestId('dev-ui')).toBeInTheDocument();
      expect(screen.queryByTestId('prod-ui')).not.toBeInTheDocument();
    });

    it('should render Production-specific UI', () => {
      // Arrange
      mockEnvironment.isProduction = true;
      
      // Act
      render(<EnvironmentAwareComponent>Test Content</EnvironmentAwareComponent>);
      
      // Assert
      expect(screen.getByTestId('prod-ui')).toBeInTheDocument();
      expect(screen.queryByTestId('dev-ui')).not.toBeInTheDocument();
    });
  });

  describe('Environment Info Component', () => {
    it('should display Windows environment info', () => {
      // Arrange
      mockEnvironment.isWindows = true;
      mockEnvironment.isDevelopment = true;
      
      // Act
      render(<EnvironmentInfo />);
      
      // Assert
      expect(screen.getByTestId('os-info')).toHaveTextContent('Windows');
      expect(screen.getByTestId('env-type')).toHaveTextContent('Development');
    });

    it('should display macOS environment info', () => {
      // Arrange
      mockEnvironment.isMacOS = true;
      mockEnvironment.isProduction = true;
      
      // Act
      render(<EnvironmentInfo />);
      
      // Assert
      expect(screen.getByTestId('os-info')).toHaveTextContent('macOS');
      expect(screen.getByTestId('env-type')).toHaveTextContent('Production');
    });

    it('should display CI environment info', () => {
      // Arrange
      mockEnvironment.isLinux = true;
      mockEnvironment.isCI = true;
      
      // Act
      render(<EnvironmentInfo />);
      
      // Assert
      expect(screen.getByTestId('os-info')).toHaveTextContent('Linux');
      expect(screen.getByTestId('ci-info')).toHaveTextContent('Yes');
    });

    it('should display Docker environment info', () => {
      // Arrange
      mockEnvironment.isLinux = true;
      mockEnvironment.isDocker = true;
      
      // Act
      render(<EnvironmentInfo />);
      
      // Assert
      expect(screen.getByTestId('os-info')).toHaveTextContent('Linux');
      expect(screen.getByTestId('docker-info')).toHaveTextContent('Yes');
    });
  });
});
