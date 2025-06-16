/**
 * Platform-Specific Helper
 * 
 * This module provides functions to handle platform-specific behavior:
 * - Path handling for Windows vs Unix
 * - Command execution for different platforms
 * - File system operations
 * 
 * It's designed to be used across the application to ensure consistent
 * platform-specific behavior.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const childProcess = require('child_process');
const { detectEnvironment } = require('./environment-detection');

/**
 * Get a platform-specific path
 * @param {...string} pathSegments - Path segments to join
 * @returns {string} Platform-specific path
 */
function getPlatformSpecificPath(...pathSegments) {
  const env = detectEnvironment();
  
  // If only one segment is provided, it might be a path with separators
  if (pathSegments.length === 1 && typeof pathSegments[0] === 'string') {
    const inputPath = pathSegments[0];
    
    // Convert Windows paths to Unix paths on Unix platforms
    if (!env.isWindows && inputPath.includes('\\')) {
      return inputPath.replace(/\\/g, '/');
    }
    
    // Convert Unix paths to Windows paths on Windows
    if (env.isWindows && inputPath.includes('/')) {
      return inputPath.replace(/\//g, '\\');
    }
    
    return inputPath;
  }
  
  // Join path segments using platform-specific separator
  return path.join(...pathSegments);
}

/**
 * Get platform-specific command
 * @param {string} commandType - Type of command (e.g., 'list-files', 'create-dir')
 * @returns {string} Platform-specific command
 */
function getPlatformSpecificCommand(commandType) {
  const env = detectEnvironment();
  
  const commands = {
    'list-files': {
      win32: 'dir',
      default: 'ls -la'
    },
    'create-dir': {
      win32: 'mkdir',
      default: 'mkdir -p'
    },
    'remove-file': {
      win32: 'del',
      default: 'rm'
    },
    'remove-dir': {
      win32: 'rmdir /s /q',
      default: 'rm -rf'
    },
    'copy-file': {
      win32: 'copy',
      default: 'cp'
    },
    'move-file': {
      win32: 'move',
      default: 'mv'
    },
    'error-command': {
      win32: 'invalid-command-windows',
      default: 'invalid-command-unix'
    }
  };
  
  const commandSet = commands[commandType] || { win32: commandType, default: commandType };
  return env.isWindows ? commandSet.win32 : commandSet.default;
}

/**
 * Execute a platform-specific command
 * @param {string} commandType - Type of command (e.g., 'list-files', 'create-dir')
 * @param {string} [args] - Command arguments
 * @param {Object} [options] - Child process options
 * @returns {string} Command output
 */
function executeCommand(commandType, args = '', options = {}) {
  const env = detectEnvironment();
  const command = getPlatformSpecificCommand(commandType);
  const fullCommand = args ? `${command} ${args}` : command;
  
  try {
    return childProcess.execSync(fullCommand, { encoding: 'utf8', ...options });
  } catch (error) {
    const platform = env.isWindows ? 'Windows' : env.isMacOS ? 'macOS' : 'Linux';
    throw new Error(`Command failed on ${platform}: ${error.message}`);
  }
}

/**
 * Create a directory with platform-specific handling
 * @param {string} dirPath - Directory path
 * @returns {boolean} Whether the directory was created successfully
 */
function createDirectory(dirPath) {
  const env = detectEnvironment();
  
  try {
    if (!fs.existsSync(dirPath)) {
      if (env.isWindows) {
        // Windows-specific directory creation
        fs.mkdirSync(dirPath, { recursive: true });
      } else {
        // Unix-specific directory creation
        fs.mkdirSync(dirPath, { recursive: true, mode: 0o755 });
      }
      return true;
    }
    return false; // Directory already exists
  } catch (error) {
    console.error(`Failed to create directory ${dirPath}: ${error.message}`);
    return false;
  }
}

/**
 * Write to a file with platform-specific handling
 * @param {string} filePath - File path
 * @param {string} content - File content
 * @param {Object} [options] - Options
 * @returns {boolean} Whether the file was written successfully
 */
function writeFile(filePath, content, options = {}) {
  const env = detectEnvironment();
  const { append = false, ensureDir = true } = options;
  
  try {
    // Ensure directory exists
    if (ensureDir) {
      const dirPath = path.dirname(filePath);
      createDirectory(dirPath);
    }
    
    // Write file with platform-specific handling
    if (append) {
      fs.appendFileSync(filePath, content, 'utf8');
    } else {
      fs.writeFileSync(filePath, content, 'utf8');
    }
    
    return true;
  } catch (error) {
    console.error(`Failed to write to file ${filePath}: ${error.message}`);
    
    // Try alternative approach for Windows
    if (env.isWindows) {
      try {
        const tempFile = path.join(os.tmpdir(), `temp-${Date.now()}.txt`);
        fs.writeFileSync(tempFile, content, 'utf8');
        childProcess.execSync(`copy /y "${tempFile}" "${filePath}"`);
        return true;
      } catch (winError) {
        console.error(`Windows fallback failed: ${winError.message}`);
      }
    }
    
    return false;
  }
}

module.exports = {
  getPlatformSpecificPath,
  getPlatformSpecificCommand,
  executeCommand,
  createDirectory,
  writeFile
};
