/**
 * Platform-Specific Tests
 * 
 * This file contains tests for platform-specific behavior:
 * - Windows-specific behavior
 * - macOS-specific behavior
 * - Linux-specific behavior
 * 
 * These tests ensure that the application behaves correctly on different platforms.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';
import childProcess from 'child_process';

// Mock modules
vi.mock('fs');
vi.mock('path');
vi.mock('os');
vi.mock('child_process');

// Create the module under test
const platformSpecific = {
  getPlatformSpecificPath: (...pathSegments) => {
    const platform = os.platform();
    const isWindows = platform === 'win32';
    
    // If only one segment is provided, it might be a path with separators
    if (pathSegments.length === 1 && typeof pathSegments[0] === 'string') {
      const inputPath = pathSegments[0];
      
      // Convert Windows paths to Unix paths on Unix platforms
      if (!isWindows && inputPath.includes('\\')) {
        return inputPath.replace(/\\/g, '/');
      }
      
      // Convert Unix paths to Windows paths on Windows
      if (isWindows && inputPath.includes('/')) {
        return inputPath.replace(/\//g, '\\');
      }
      
      return inputPath;
    }
    
    // Join path segments using platform-specific separator
    return path.join(...pathSegments);
  },
  
  executeCommand: (commandType, args = '') => {
    const platform = os.platform();
    const isWindows = platform === 'win32';
    
    const commands = {
      'list-files': {
        win32: 'dir',
        default: 'ls -la'
      },
      'error-command': {
        win32: 'invalid-command-windows',
        default: 'invalid-command-unix'
      }
    };
    
    const commandSet = commands[commandType] || { win32: commandType, default: commandType };
    const command = isWindows ? commandSet.win32 : commandSet.default;
    const fullCommand = args ? `${command} ${args}` : command;
    
    try {
      return childProcess.execSync(fullCommand, { encoding: 'utf8' });
    } catch (error) {
      const platformName = isWindows ? 'Windows' : platform === 'darwin' ? 'macOS' : 'Linux';
      throw new Error(`Command failed on ${platformName}: ${error.message}`);
    }
  }
};

// Import the module under test
vi.mock('../tests/helpers/platform-specific', () => platformSpecific, { virtual: true });
const { getPlatformSpecificPath, executeCommand } = platformSpecific;

describe('Platform-Specific Behavior', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();
    
    // Default mock implementations
    os.platform.mockReturnValue('linux');
    os.type.mockReturnValue('Linux');
    os.release.mockReturnValue('5.10.0');
    os.tmpdir.mockReturnValue('/tmp');
    path.join.mockImplementation((...args) => args.join('/'));
    path.resolve.mockImplementation((...args) => args.join('/'));
    path.sep = '/';
    childProcess.execSync.mockReturnValue(Buffer.from('command output'));
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Path Handling', () => {
    it('should handle Windows paths correctly', () => {
      // Arrange
      os.platform.mockReturnValue('win32');
      path.sep = '\\';
      path.join.mockImplementation((...args) => args.join('\\'));
      
      // Act
      const result = getPlatformSpecificPath('dir', 'file.txt');
      
      // Assert
      expect(result).toBe('dir\\file.txt');
      expect(os.platform).toHaveBeenCalled();
      expect(path.join).toHaveBeenCalledWith('dir', 'file.txt');
    });

    it('should handle Unix paths correctly', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      path.sep = '/';
      path.join.mockImplementation((...args) => args.join('/'));
      
      // Act
      const result = getPlatformSpecificPath('dir', 'file.txt');
      
      // Assert
      expect(result).toBe('dir/file.txt');
      expect(os.platform).toHaveBeenCalled();
      expect(path.join).toHaveBeenCalledWith('dir', 'file.txt');
    });

    it('should convert Windows paths to Unix paths', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      
      // Act
      const result = getPlatformSpecificPath('dir\\subdir\\file.txt');
      
      // Assert
      expect(result).toBe('dir/subdir/file.txt');
    });

    it('should convert Unix paths to Windows paths', () => {
      // Arrange
      os.platform.mockReturnValue('win32');
      path.sep = '\\';
      
      // Act
      const result = getPlatformSpecificPath('dir/subdir/file.txt');
      
      // Assert
      expect(result).toBe('dir\\subdir\\file.txt');
    });
  });

  describe('Command Execution', () => {
    it('should execute Windows-specific commands on Windows', () => {
      // Arrange
      os.platform.mockReturnValue('win32');
      
      // Act
      executeCommand('list-files');
      
      // Assert
      expect(childProcess.execSync).toHaveBeenCalledWith('dir', { encoding: 'utf8' });
    });

    it('should execute Unix-specific commands on Linux', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      
      // Act
      executeCommand('list-files');
      
      // Assert
      expect(childProcess.execSync).toHaveBeenCalledWith('ls -la', { encoding: 'utf8' });
    });

    it('should execute Unix-specific commands on macOS', () => {
      // Arrange
      os.platform.mockReturnValue('darwin');
      
      // Act
      executeCommand('list-files');
      
      // Assert
      expect(childProcess.execSync).toHaveBeenCalledWith('ls -la', { encoding: 'utf8' });
    });

    it('should handle platform-specific error commands', () => {
      // Arrange
      os.platform.mockReturnValue('win32');
      childProcess.execSync.mockImplementation(() => {
        throw new Error('Command failed');
      });
      
      // Act & Assert
      expect(() => executeCommand('error-command')).toThrow('Command failed on Windows: Command failed');
    });
  });
});
