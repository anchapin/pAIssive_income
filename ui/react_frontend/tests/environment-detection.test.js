/**
 * Environment Detection Tests
 * 
 * This file contains tests for the environment detection functionality.
 * It tests the detection of various environments:
 * - Operating Systems
 * - CI environments
 * - Container environments
 * - Cloud environments
 * - Node.js environments
 */

const { detectEnvironment, createEnvironmentReport } = require('./helpers/environment-detection');

describe('Environment Detection', () => {
  // Save original environment variables
  const originalEnv = { ...process.env };
  
  // Clean up after each test
  afterEach(() => {
    // Restore original environment variables
    process.env = { ...originalEnv };
  });
  
  describe('Operating System Detection', () => {
    test('should detect the current operating system', () => {
      const env = detectEnvironment();
      
      // One of these should be true
      expect(env.isWindows || env.isMacOS || env.isLinux).toBe(true);
      
      // Platform should match the detected OS
      if (env.isWindows) {
        expect(env.platform).toBe('win32');
      } else if (env.isMacOS) {
        expect(env.platform).toBe('darwin');
      } else if (env.isLinux) {
        expect(env.platform).toBe('linux');
      }
    });
    
    test('should detect WSL environment when appropriate', () => {
      // Mock WSL environment
      process.env.WSL_DISTRO_NAME = 'Ubuntu';
      
      const env = detectEnvironment();
      
      // Should detect WSL
      expect(env.isWSL).toBe(true);
    });
  });
  
  describe('CI Environment Detection', () => {
    test('should detect GitHub Actions environment', () => {
      // Mock GitHub Actions environment
      process.env.CI = 'true';
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test';
      process.env.GITHUB_RUN_ID = '12345';
      
      const env = detectEnvironment();
      
      // Should detect CI and GitHub Actions
      expect(env.isCI).toBe(true);
      expect(env.isGitHubActions).toBe(true);
    });
    
    test('should detect Jenkins environment', () => {
      // Mock Jenkins environment
      process.env.CI = 'true';
      process.env.JENKINS_URL = 'http://jenkins.example.com/';
      
      const env = detectEnvironment();
      
      // Should detect CI and Jenkins
      expect(env.isCI).toBe(true);
      expect(env.isJenkins).toBe(true);
    });
    
    test('should detect GitLab CI environment', () => {
      // Mock GitLab CI environment
      process.env.CI = 'true';
      process.env.GITLAB_CI = 'true';
      
      const env = detectEnvironment();
      
      // Should detect CI and GitLab CI
      expect(env.isCI).toBe(true);
      expect(env.isGitLabCI).toBe(true);
    });
    
    test('should detect CI environment with CI_TYPE and CI_PLATFORM', () => {
      // Mock CI environment with CI_TYPE and CI_PLATFORM
      process.env.CI = 'true';
      process.env.CI_TYPE = 'github';
      process.env.CI_PLATFORM = 'github';
      
      const env = detectEnvironment();
      
      // Should detect CI and GitHub Actions
      expect(env.isCI).toBe(true);
      expect(env.isGitHubActions).toBe(true);
    });
  });
  
  describe('Container Environment Detection', () => {
    test('should detect Docker environment', () => {
      // Mock Docker environment
      process.env.DOCKER_ENVIRONMENT = 'true';
      
      const env = detectEnvironment();
      
      // Should detect Docker
      expect(env.isDocker).toBe(true);
      expect(env.isContainerized).toBe(true);
    });
    
    test('should detect Kubernetes environment', () => {
      // Mock Kubernetes environment
      process.env.KUBERNETES_SERVICE_HOST = '10.0.0.1';
      process.env.KUBERNETES_PORT = '443';
      
      const env = detectEnvironment();
      
      // Should detect Kubernetes
      expect(env.isKubernetes).toBe(true);
      expect(env.isContainerized).toBe(true);
    });
    
    test('should detect Docker Compose environment', () => {
      // Mock Docker Compose environment
      process.env.COMPOSE_PROJECT_NAME = 'test';
      
      const env = detectEnvironment();
      
      // Should detect Docker Compose
      expect(env.isDockerCompose).toBe(true);
      expect(env.isContainerized).toBe(true);
    });
    
    test('should detect Docker Swarm environment', () => {
      // Mock Docker Swarm environment
      process.env.DOCKER_SWARM = 'true';
      
      const env = detectEnvironment();
      
      // Should detect Docker Swarm
      expect(env.isDockerSwarm).toBe(true);
      expect(env.isContainerized).toBe(true);
    });
    
    test('should detect Kubernetes distributions', () => {
      // Mock GKE environment
      process.env.KUBERNETES_SERVICE_HOST = '10.0.0.1';
      process.env.GKE_CLUSTER_NAME = 'test-cluster';
      
      const env = detectEnvironment();
      
      // Should detect Kubernetes and GKE
      expect(env.isKubernetes).toBe(true);
      expect(env.isGKE).toBe(true);
    });
  });
  
  describe('Cloud Environment Detection', () => {
    test('should detect AWS environment', () => {
      // Mock AWS environment
      process.env.AWS_REGION = 'us-west-2';
      
      const env = detectEnvironment();
      
      // Should detect AWS
      expect(env.isAWS).toBe(true);
      expect(env.isCloudEnvironment).toBe(true);
    });
    
    test('should detect AWS Lambda environment', () => {
      // Mock AWS Lambda environment
      process.env.AWS_REGION = 'us-west-2';
      process.env.AWS_LAMBDA_FUNCTION_NAME = 'test-function';
      
      const env = detectEnvironment();
      
      // Should detect AWS and AWS Lambda
      expect(env.isAWS).toBe(true);
      expect(env.isAWSLambda).toBe(true);
      expect(env.isServerless).toBe(true);
    });
    
    test('should detect Azure environment', () => {
      // Mock Azure environment
      process.env.AZURE_SUBSCRIPTION_ID = '12345';
      
      const env = detectEnvironment();
      
      // Should detect Azure
      expect(env.isAzure).toBe(true);
      expect(env.isCloudEnvironment).toBe(true);
    });
    
    test('should detect Azure Functions environment', () => {
      // Mock Azure Functions environment
      process.env.AZURE_FUNCTIONS_ENVIRONMENT = 'Development';
      
      const env = detectEnvironment();
      
      // Should detect Azure and Azure Functions
      expect(env.isAzure).toBe(true);
      expect(env.isAzureFunctions).toBe(true);
      expect(env.isServerless).toBe(true);
    });
    
    test('should detect GCP environment', () => {
      // Mock GCP environment
      process.env.GOOGLE_CLOUD_PROJECT = 'test-project';
      
      const env = detectEnvironment();
      
      // Should detect GCP
      expect(env.isGCP).toBe(true);
      expect(env.isCloudEnvironment).toBe(true);
    });
    
    test('should detect GCP Cloud Functions environment', () => {
      // Mock GCP Cloud Functions environment
      process.env.GOOGLE_CLOUD_PROJECT = 'test-project';
      process.env.FUNCTION_NAME = 'test-function';
      process.env.FUNCTION_REGION = 'us-central1';
      
      const env = detectEnvironment();
      
      // Should detect GCP and GCP Cloud Functions
      expect(env.isGCP).toBe(true);
      expect(env.isGCPCloudFunctions).toBe(true);
      expect(env.isServerless).toBe(true);
    });
  });
  
  describe('Node Environment Detection', () => {
    test('should detect development environment', () => {
      // Mock development environment
      process.env.NODE_ENV = 'development';
      
      const env = detectEnvironment();
      
      // Should detect development
      expect(env.isDevelopment).toBe(true);
      expect(env.isProduction).toBe(false);
      expect(env.isTest).toBe(false);
    });
    
    test('should detect production environment', () => {
      // Mock production environment
      process.env.NODE_ENV = 'production';
      
      const env = detectEnvironment();
      
      // Should detect production
      expect(env.isDevelopment).toBe(false);
      expect(env.isProduction).toBe(true);
      expect(env.isTest).toBe(false);
    });
    
    test('should detect test environment', () => {
      // Mock test environment
      process.env.NODE_ENV = 'test';
      
      const env = detectEnvironment();
      
      // Should detect test
      expect(env.isDevelopment).toBe(false);
      expect(env.isProduction).toBe(false);
      expect(env.isTest).toBe(true);
    });
  });
  
  describe('Environment Report', () => {
    test('should create a JSON environment report', () => {
      // Mock environment
      process.env.CI = 'true';
      process.env.GITHUB_ACTIONS = 'true';
      
      const report = createEnvironmentReport(null, { formatJson: true });
      
      // Should be valid JSON
      const reportObj = JSON.parse(report);
      
      // Should contain expected sections
      expect(reportObj).toHaveProperty('operatingSystem');
      expect(reportObj).toHaveProperty('ciEnvironment');
      expect(reportObj).toHaveProperty('containerEnvironment');
      expect(reportObj).toHaveProperty('cloudEnvironment');
      expect(reportObj).toHaveProperty('nodeEnvironment');
      
      // Should detect GitHub Actions
      expect(reportObj.ciEnvironment.isGitHubActions).toBe(true);
    });
    
    test('should create a text environment report', () => {
      // Mock environment
      process.env.CI = 'true';
      process.env.GITHUB_ACTIONS = 'true';
      
      const report = createEnvironmentReport();
      
      // Should be a string
      expect(typeof report).toBe('string');
      
      // Should contain expected sections
      expect(report).toContain('Operating System:');
      expect(report).toContain('CI Environment:');
      expect(report).toContain('Container Environment:');
      expect(report).toContain('Cloud Environment:');
      expect(report).toContain('Node Environment:');
      
      // Should detect GitHub Actions
      expect(report).toContain('GitHub Actions: Yes');
    });
  });
});
