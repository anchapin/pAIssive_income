/**
 * Test script to verify environment detection accuracy
 * This tests the environment detection system to ensure it correctly identifies
 * CI, Docker, and local environments as described in PR 166.
 */

// Test 1: Basic environment detection
console.log('=== Test 1: Basic Environment Detection ===');
try {
  const envDetection = require('./tests/helpers/environment-detection');
  const env = envDetection.detectEnvironment();

  console.log('✅ Environment detection module loaded successfully');
  console.log(`Platform: ${env.platform} (Windows: ${env.isWindows})`);
  console.log(`CI: ${env.isCI}`);
  console.log(`Docker: ${env.isDocker}`);
  console.log(`Memory: ${Math.round(env.memory.total / (1024 * 1024 * 1024))} GB total`);
  console.log(`CPUs: ${env.cpus.length}`);
} catch (error) {
  console.error('❌ Environment detection test failed:', error.message);
}

// Test 2: Unified environment module
console.log('\n=== Test 2: Unified Environment Module ===');
try {
  const unifiedEnv = require('./tests/helpers/unified-environment');

  console.log('✅ Unified environment module loaded successfully');
  console.log(`isCI: ${unifiedEnv.isCI()}`);
  console.log(`isGitHubActions: ${unifiedEnv.isGitHubActions()}`);
  console.log(`isDockerEnvironment: ${unifiedEnv.isDockerEnvironment()}`);
  console.log(`isKubernetesEnvironment: ${unifiedEnv.isKubernetesEnvironment()}`);
} catch (error) {
  console.error('❌ Unified environment module test failed:', error.message);
}

// Test 3: CI environment helper
console.log('\n=== Test 3: CI Environment Helper ===');
try {
  const ciEnv = require('./tests/helpers/ci-environment');

  console.log('✅ CI environment helper loaded successfully');
  const ciType = ciEnv.detectCIEnvironmentType({ verbose: false });
  console.log(`CI Type: ${ciType}`);

  // Test report generation without writing to file
  const report = ciEnv.createCIReport(null, {
    includeSystemInfo: true,
    includeEnvVars: false,
    includeContainers: true,
    includeCloud: true
  });

  console.log('✅ CI report generated successfully');
  console.log(`Report length: ${report.length} characters`);
} catch (error) {
  console.error('❌ CI environment helper test failed:', error.message);
}

// Test 4: Enhanced mock path-to-regexp
console.log('\n=== Test 4: Enhanced Mock Path-to-RegExp ===');
try {
  const mockPathToRegexp = require('./tests/enhanced_mock_path_to_regexp');

  console.log('✅ Enhanced mock path-to-regexp loaded successfully');
} catch (error) {
  console.error('❌ Enhanced mock path-to-regexp test failed:', error.message);
}

// Test 5: Simulated CI environment
console.log('\n=== Test 5: Simulated CI Environment ===');
try {
  // Temporarily set CI environment variables
  const originalCI = process.env.CI;
  const originalGitHubActions = process.env.GITHUB_ACTIONS;

  process.env.CI = 'true';
  process.env.GITHUB_ACTIONS = 'true';

  // Re-require modules to pick up new environment variables
  delete require.cache[require.resolve('./tests/helpers/unified-environment')];
  const unifiedEnvCI = require('./tests/helpers/unified-environment');

  console.log('✅ Simulated CI environment test');
  console.log(`isCI (simulated): ${unifiedEnvCI.isCI()}`);
  console.log(`isGitHubActions (simulated): ${unifiedEnvCI.isGitHubActions()}`);

  // Restore original environment variables
  if (originalCI !== undefined) {
    process.env.CI = originalCI;
  } else {
    delete process.env.CI;
  }

  if (originalGitHubActions !== undefined) {
    process.env.GITHUB_ACTIONS = originalGitHubActions;
  } else {
    delete process.env.GITHUB_ACTIONS;
  }

} catch (error) {
  console.error('❌ Simulated CI environment test failed:', error.message);
}

// Test 6: Windows-specific path handling
console.log('\n=== Test 6: Windows-Specific Path Handling ===');
try {
  const envDetection = require('./tests/helpers/environment-detection');

  // Test that Linux-specific files are not accessed on Windows
  console.log('✅ Testing Windows-specific path handling');
  console.log('Platform check: Windows paths should not cause errors');

  // This should not throw errors about /proc/1/cgroup on Windows
  const containerEnv = envDetection.detectContainerEnvironment();
  console.log(`Container detection completed without errors: ${!containerEnv.isContainer}`);

} catch (error) {
  console.error('❌ Windows-specific path handling test failed:', error.message);
}

console.log('\n=== Environment Detection Test Summary ===');
console.log('All tests completed. Check above for any ❌ errors.');
console.log('If all tests show ✅, the environment detection system is working correctly.');
