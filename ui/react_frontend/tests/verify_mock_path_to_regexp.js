/**
 * Script to verify that the mock path-to-regexp implementation is properly loaded
 * This script is used by the GitHub Actions workflow to verify that the mock
 * implementation of path-to-regexp is properly loaded and working.
 */

console.log('Starting verification of mock path-to-regexp implementation...');

try {
  // Try to load the path-to-regexp module
  const pathToRegexp = require('path-to-regexp');
  
  console.log('Successfully loaded path-to-regexp module');
  console.log('Available functions:', Object.keys(pathToRegexp).join(', '));
  
  // Test the basic functionality
  const keys = [];
  const regex = pathToRegexp('/users/:userId/posts/:postId', keys);
  
  console.log('Created regex:', regex);
  console.log('Extracted keys:', JSON.stringify(keys, null, 2));
  
  // Test the parse method
  const tokens = pathToRegexp.parse('/users/:userId/posts/:postId');
  console.log('Parse result:', JSON.stringify(tokens, null, 2));
  
  // Test the compile method
  const toPath = pathToRegexp.compile('/users/:userId/posts/:postId');
  const path = toPath({ userId: '123', postId: '456' });
  console.log('Compile result:', path);
  
  // Test the match method
  const matchFn = pathToRegexp.match('/users/:userId/posts/:postId');
  const matchResult = matchFn('/users/123/posts/456');
  console.log('Match result:', JSON.stringify(matchResult, null, 2));
  
  console.log('All tests passed successfully!');
  
  // Create a marker file to indicate success
  const fs = require('fs');
  const reportDir = './playwright-report';
  
  try {
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    fs.writeFileSync(
      `${reportDir}/path-to-regexp-verification-success.txt`,
      `Mock path-to-regexp verification successful at ${new Date().toISOString()}\n` +
      `Available functions: ${Object.keys(pathToRegexp).join(', ')}\n`
    );
  } catch (fsError) {
    console.error('Failed to create marker file:', fsError.message);
  }
} catch (error) {
  console.error('Failed to load or verify path-to-regexp:', error.message);
  console.error('Stack trace:', error.stack);
  
  // Create a marker file to indicate failure
  const fs = require('fs');
  const reportDir = './playwright-report';
  
  try {
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    fs.writeFileSync(
      `${reportDir}/path-to-regexp-verification-failure.txt`,
      `Mock path-to-regexp verification failed at ${new Date().toISOString()}\n` +
      `Error: ${error.message}\n` +
      `Stack: ${error.stack || 'No stack trace available'}\n`
    );
  } catch (fsError) {
    console.error('Failed to create marker file:', fsError.message);
  }
  
  // Exit with a non-zero status code to indicate failure
  process.exit(1);
}
