/**
 * CI Environment Detection Tests
 * 
 * This file contains tests for the CI environment detection functionality.
 * It verifies that the CI environment detection works correctly for all supported CI platforms.
 */

const { detectCIEnvironmentType } = require('./helpers/ci-environment');
const { detectEnvironment } = require('./helpers/environment-detection');

describe('CI Environment Detection', () => {
  // Store original environment variables
  const originalEnv = { ...process.env };
  
  // Reset environment variables after each test
  afterEach(() => {
    process.env = { ...originalEnv };
  });
  
  test('should detect no CI environment when no CI variables are set', () => {
    // Clear CI-related environment variables
    delete process.env.CI;
    delete process.env.CI_ENVIRONMENT;
    delete process.env.GITHUB_ACTIONS;
    delete process.env.JENKINS_URL;
    delete process.env.GITLAB_CI;
    
    expect(detectCIEnvironmentType()).toBe('none');
  });
  
  test('should detect GitHub Actions', () => {
    process.env.CI = 'true';
    process.env.GITHUB_ACTIONS = 'true';
    
    expect(detectCIEnvironmentType()).toBe('github');
  });
  
  test('should detect Jenkins', () => {
    process.env.CI = 'true';
    process.env.JENKINS_URL = 'http://jenkins.example.com';
    
    expect(detectCIEnvironmentType()).toBe('jenkins');
  });
  
  test('should detect GitLab CI', () => {
    process.env.CI = 'true';
    process.env.GITLAB_CI = 'true';
    
    expect(detectCIEnvironmentType()).toBe('gitlab');
  });
  
  test('should detect CircleCI', () => {
    process.env.CI = 'true';
    process.env.CIRCLECI = 'true';
    
    expect(detectCIEnvironmentType()).toBe('circle');
  });
  
  test('should detect Travis CI', () => {
    process.env.CI = 'true';
    process.env.TRAVIS = 'true';
    
    expect(detectCIEnvironmentType()).toBe('travis');
  });
  
  test('should detect Azure Pipelines', () => {
    process.env.CI = 'true';
    process.env.TF_BUILD = 'true';
    
    expect(detectCIEnvironmentType()).toBe('azure');
  });
  
  test('should detect Vercel', () => {
    process.env.CI = 'true';
    process.env.VERCEL = '1';
    
    expect(detectCIEnvironmentType()).toBe('vercel');
  });
  
  test('should detect Netlify', () => {
    process.env.CI = 'true';
    process.env.NETLIFY = 'true';
    
    expect(detectCIEnvironmentType()).toBe('netlify');
  });
  
  test('should detect Heroku CI', () => {
    process.env.CI = 'true';
    process.env.HEROKU_TEST_RUN_ID = 'test-run-id';
    
    expect(detectCIEnvironmentType()).toBe('heroku');
  });
  
  test('should detect Semaphore CI', () => {
    process.env.CI = 'true';
    process.env.SEMAPHORE = 'true';
    
    expect(detectCIEnvironmentType()).toBe('semaphore');
  });
  
  test('should detect Codefresh', () => {
    process.env.CI = 'true';
    process.env.CF_BUILD_ID = 'build-id';
    
    expect(detectCIEnvironmentType()).toBe('codefresh');
  });
  
  test('should detect Woodpecker CI', () => {
    process.env.CI = 'true';
    process.env.CI_PIPELINE_ID = 'pipeline-id';
    process.env.CI_REPO = 'repo';
    
    expect(detectCIEnvironmentType()).toBe('woodpecker');
  });
  
  test('should detect Harness CI', () => {
    process.env.CI = 'true';
    process.env.HARNESS_BUILD_ID = 'build-id';
    
    expect(detectCIEnvironmentType()).toBe('harness');
  });
  
  test('should detect Render', () => {
    process.env.CI = 'true';
    process.env.RENDER = 'true';
    
    expect(detectCIEnvironmentType()).toBe('render');
  });
  
  test('should detect Railway', () => {
    process.env.CI = 'true';
    process.env.RAILWAY_ENVIRONMENT_ID = 'env-id';
    
    expect(detectCIEnvironmentType()).toBe('railway');
  });
  
  test('should detect Fly.io', () => {
    process.env.CI = 'true';
    process.env.FLY_APP_NAME = 'app-name';
    
    expect(detectCIEnvironmentType()).toBe('flyio');
  });
  
  test('should respect CI_TYPE environment variable', () => {
    process.env.CI = 'true';
    process.env.CI_TYPE = 'custom-ci';
    
    expect(detectCIEnvironmentType()).toBe('custom-ci');
  });
  
  test('should respect forceCIType option', () => {
    process.env.CI = 'true';
    process.env.GITHUB_ACTIONS = 'true';
    
    expect(detectCIEnvironmentType({ forceCIType: 'custom-ci' })).toBe('custom-ci');
  });
  
  test('should detect generic CI environment when CI is true but no specific platform is detected', () => {
    process.env.CI = 'true';
    
    expect(detectCIEnvironmentType()).toBe('generic');
  });
  
  test('should detect CI environment when CI_ENVIRONMENT is set', () => {
    delete process.env.CI;
    process.env.CI_ENVIRONMENT = 'true';
    
    expect(detectCIEnvironmentType()).not.toBe('none');
  });
});
