/**
 * Enhanced Environment Report Generator
 *
 * This script generates comprehensive environment reports with detailed information about:
 * - CI environments (GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines,
 *   TeamCity, Bitbucket, AppVeyor, Buildkite, Codefresh, Semaphore, Harness, etc.)
 * - Container environments (Docker, Kubernetes, rkt, containerd, CRI-O, Singularity, etc.)
 * - Cloud environments (AWS, Azure, GCP, Alibaba, Tencent, Huawei, Oracle, IBM, etc.)
 * - System information (OS, Node.js version, architecture, etc.)
 *
 * The report can be generated in both text and JSON formats.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Import environment detection modules
const environmentDetection = require('./environment-detection');
// Fallback if unified-environment module is not available
let unifiedEnvironment;
try {
  unifiedEnvironment = require('./unified-environment');
} catch (error) {
  console.log('Unified environment module not found, using fallback');
  // Create a fallback object with basic functions
  unifiedEnvironment = {
    getEnvironment: () => ({}),
    isCI: () => environmentDetection.detectEnvironment().isCI,
    isGitHubActions: () => environmentDetection.detectEnvironment().isGitHubActions,
    isDockerEnvironment: () => environmentDetection.detectEnvironment().isDocker,
    isKubernetesEnvironment: () => environmentDetection.detectEnvironment().isKubernetes,
    getCIType: () => {
      const env = environmentDetection.detectEnvironment();
      if (env.isGitHubActions) return 'github';
      if (env.isJenkins) return 'jenkins';
      if (env.isGitLabCI) return 'gitlab';
      if (env.isCircleCI) return 'circleci';
      if (env.isTravis) return 'travis';
      if (env.isAzurePipelines) return 'azure';
      if (env.isTeamCity) return 'teamcity';
      if (env.isBitbucket) return 'bitbucket';
      if (env.isAppVeyor) return 'appveyor';
      if (env.isBuildkite) return 'buildkite';
      return 'unknown';
    }
  };
}

/**
 * Generate a comprehensive environment report
 * @param {Object} options - Report options
 * @param {string} [options.outputPath] - Path to save the report (if not provided, returns the report as a string)
 * @param {boolean} [options.formatJson=false] - Whether to format as JSON
 * @param {boolean} [options.includeEnvVars=false] - Whether to include environment variables
 * @param {boolean} [options.includeSystemInfo=true] - Whether to include detailed system info
 * @param {boolean} [options.includeContainers=true] - Whether to include container runtime details
 * @param {boolean} [options.includeCloud=true] - Whether to include cloud provider details
 * @param {boolean} [options.verbose=false] - Whether to include verbose details
 * @returns {string} The generated report
 */
function generateEnvironmentReport(options = {}) {
  const {
    outputPath,
    formatJson = false,
    includeEnvVars = false,
    includeSystemInfo = true,
    includeContainers = true,
    includeCloud = true,
    verbose = false
  } = options;

  // Get environment information from both detection modules for maximum coverage
  const env = environmentDetection.detectEnvironment();
  const unifiedEnv = unifiedEnvironment.getEnvironment ? unifiedEnvironment.getEnvironment() : {};

  // Create timestamp
  const timestamp = new Date().toISOString();

  // Build the report data object
  const reportData = {
    timestamp,
    generated: {
      date: new Date().toLocaleString(),
      timestamp
    },
    operatingSystem: {
      platform: env.platform,
      isWindows: env.isWindows,
      isMacOS: env.isMacOS,
      isLinux: env.isLinux,
      isWSL: env.isWSL,
      osType: env.osType,
      osRelease: env.osRelease,
      architecture: env.architecture
    },
    ciEnvironment: {
      isCI: env.isCI,
      ciType: unifiedEnvironment.getCIType ? unifiedEnvironment.getCIType() : 'unknown',
      isGitHubActions: env.isGitHubActions,
      isJenkins: env.isJenkins,
      isGitLabCI: env.isGitLabCI,
      isCircleCI: env.isCircleCI,
      isTravis: env.isTravis,
      isAzurePipelines: env.isAzurePipelines,
      isTeamCity: env.isTeamCity,
      isBitbucket: env.isBitbucket,
      isAppVeyor: env.isAppVeyor,
      // New CI platforms
      isBuildkite: env.isBuildkite,
      isCodefresh: env.isCodefresh,
      isSemaphore: env.isSemaphore,
      isHarness: env.isHarness
    }
  };

  // Add container environment details if requested
  if (includeContainers) {
    reportData.containerEnvironment = {
      isDocker: env.isDocker,
      isKubernetes: env.isKubernetes,
      isContainerized: env.isContainerized,
      // New container runtimes
      isRkt: env.isRkt,
      isContainerd: env.isContainerd,
      isCRIO: env.isCRIO,
      isSingularity: env.isSingularity,
      // Additional container info from unified environment
      isPodman: unifiedEnv.isPodman && unifiedEnv.isPodman(),
      isLXC: unifiedEnv.isLXC && unifiedEnv.isLXC(),
      isDockerCompose: unifiedEnv.isDockerCompose && unifiedEnv.isDockerCompose(),
      isDockerSwarm: unifiedEnv.isDockerSwarm && unifiedEnv.isDockerSwarm(),
      // Detection methods (if available)
      detectionMethod: unifiedEnv.getContainerDetectionMethod && unifiedEnv.getContainerDetectionMethod()
    };
  }

  // Add cloud environment details if requested
  if (includeCloud) {
    reportData.cloudEnvironment = {
      isAWS: env.isAWS,
      isAzure: env.isAzure,
      isGCP: env.isGCP,
      // New cloud providers
      isAlibabaCloud: env.isAlibabaCloud,
      isTencentCloud: env.isTencentCloud,
      isHuaweiCloud: env.isHuaweiCloud,
      isOracleCloud: env.isOracleCloud,
      isIBMCloud: env.isIBMCloud,
      isCloudEnvironment: env.isCloudEnvironment,
      // Serverless
      isLambda: env.isLambda,
      isAzureFunctions: env.isAzureFunctions,
      isCloudFunctions: env.isCloudFunctions,
      isServerless: env.isServerless
    };
  }

  // Add system information if requested
  if (includeSystemInfo) {
    reportData.systemInfo = {
      nodeVersion: env.nodeVersion,
      architecture: env.architecture,
      hostname: env.hostname,
      username: env.username,
      tmpDir: env.tmpDir,
      homeDir: env.homeDir,
      workingDir: env.workingDir,
      memory: env.memory,
      cpus: env.cpus
    };
  }

  // Add environment variables if requested
  if (includeEnvVars) {
    // Filter out sensitive environment variables
    const sensitiveVarPatterns = [
      /token/i, /key/i, /secret/i, /password/i, /credential/i, /auth/i,
      /cert/i, /private/i, /signature/i, /license/i
    ];

    const filteredEnvVars = {};
    Object.keys(process.env).forEach(key => {
      const isSensitive = sensitiveVarPatterns.some(pattern => pattern.test(key));
      filteredEnvVars[key] = isSensitive ? '[REDACTED]' : process.env[key];
    });

    reportData.environmentVariables = filteredEnvVars;
  }

  // Add verbose information if requested
  if (verbose) {
    reportData.verbose = {
      processId: process.pid,
      processTitle: process.title,
      processArgv: process.argv,
      processExecPath: process.execPath,
      processVersion: process.version,
      processVersions: process.versions,
      processArch: process.arch,
      processPlatform: process.platform,
      processRelease: process.release,
      processUptime: process.uptime(),
      processMemoryUsage: process.memoryUsage(),
      processResourceUsage: process.resourceUsage && process.resourceUsage(),
      processFeatures: process.features,
      processConfig: process.config,
      processReport: process.report && {
        directory: process.report.directory,
        filename: process.report.filename,
        compact: process.report.compact,
        signal: process.report.signal,
        reportOnFatalError: process.report.reportOnFatalError,
        reportOnSignal: process.report.reportOnSignal,
        reportOnUncaughtException: process.report.reportOnUncaughtException
      }
    };
  }

  // Format the report
  let report;
  if (formatJson) {
    report = JSON.stringify(reportData, null, 2);
  } else {
    // Create a text report
    report = `Environment Report
=================
Generated at: ${timestamp}

Operating System:
  Platform: ${env.platform}
  Windows: ${env.isWindows ? 'Yes' : 'No'}
  macOS: ${env.isMacOS ? 'Yes' : 'No'}
  Linux: ${env.isLinux ? 'Yes' : 'No'}
  WSL: ${env.isWSL ? 'Yes' : 'No'}
  OS Type: ${env.osType}
  OS Release: ${env.osRelease}
  Architecture: ${env.architecture}

CI Environment:
  CI: ${env.isCI ? 'Yes' : 'No'}
  CI Type: ${unifiedEnvironment.getCIType ? unifiedEnvironment.getCIType() : 'Unknown'}
  GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}
  Jenkins: ${env.isJenkins ? 'Yes' : 'No'}
  GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}
  CircleCI: ${env.isCircleCI ? 'Yes' : 'No'}
  Travis CI: ${env.isTravis ? 'Yes' : 'No'}
  Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}
  TeamCity: ${env.isTeamCity ? 'Yes' : 'No'}
  Bitbucket: ${env.isBitbucket ? 'Yes' : 'No'}
  AppVeyor: ${env.isAppVeyor ? 'Yes' : 'No'}
  Buildkite: ${env.isBuildkite ? 'Yes' : 'No'}
  Codefresh: ${env.isCodefresh ? 'Yes' : 'No'}
  Semaphore: ${env.isSemaphore ? 'Yes' : 'No'}
  Harness: ${env.isHarness ? 'Yes' : 'No'}`;

    // Add container environment details if requested
    if (includeContainers) {
      report += `

Container Environment:
  Docker: ${env.isDocker ? 'Yes' : 'No'}
  Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
  Containerized: ${env.isContainerized ? 'Yes' : 'No'}
  rkt: ${env.isRkt ? 'Yes' : 'No'}
  containerd: ${env.isContainerd ? 'Yes' : 'No'}
  CRI-O: ${env.isCRIO ? 'Yes' : 'No'}
  Singularity: ${env.isSingularity ? 'Yes' : 'No'}`;

      // Add additional container info from unified environment if available
      if (unifiedEnv.isPodman) {
        report += `\n  Podman: ${unifiedEnv.isPodman() ? 'Yes' : 'No'}`;
      }
      if (unifiedEnv.isLXC) {
        report += `\n  LXC: ${unifiedEnv.isLXC() ? 'Yes' : 'No'}`;
      }
      if (unifiedEnv.isDockerCompose) {
        report += `\n  Docker Compose: ${unifiedEnv.isDockerCompose() ? 'Yes' : 'No'}`;
      }
      if (unifiedEnv.isDockerSwarm) {
        report += `\n  Docker Swarm: ${unifiedEnv.isDockerSwarm() ? 'Yes' : 'No'}`;
      }
      if (unifiedEnv.getContainerDetectionMethod) {
        report += `\n  Detection Method: ${unifiedEnv.getContainerDetectionMethod() || 'Unknown'}`;
      }
    }

    // Add cloud environment details if requested
    if (includeCloud) {
      report += `

Cloud Environment:
  AWS: ${env.isAWS ? 'Yes' : 'No'}
  Azure: ${env.isAzure ? 'Yes' : 'No'}
  GCP: ${env.isGCP ? 'Yes' : 'No'}
  Alibaba Cloud: ${env.isAlibabaCloud ? 'Yes' : 'No'}
  Tencent Cloud: ${env.isTencentCloud ? 'Yes' : 'No'}
  Huawei Cloud: ${env.isHuaweiCloud ? 'Yes' : 'No'}
  Oracle Cloud: ${env.isOracleCloud ? 'Yes' : 'No'}
  IBM Cloud: ${env.isIBMCloud ? 'Yes' : 'No'}
  Cloud Environment: ${env.isCloudEnvironment ? 'Yes' : 'No'}

Serverless:
  Lambda: ${env.isLambda ? 'Yes' : 'No'}
  Azure Functions: ${env.isAzureFunctions ? 'Yes' : 'No'}
  Cloud Functions: ${env.isCloudFunctions ? 'Yes' : 'No'}
  Serverless: ${env.isServerless ? 'Yes' : 'No'}`;
    }

    // Add system information if requested
    if (includeSystemInfo) {
      report += `

System Information:
  Node.js Version: ${env.nodeVersion}
  Architecture: ${env.architecture}
  Hostname: ${env.hostname}
  Username: ${env.username}
  Temp Directory: ${env.tmpDir}
  Home Directory: ${env.homeDir}
  Working Directory: ${env.workingDir}`;

      // Add memory information if available
      if (env.memory && env.memory.total) {
        const totalMemGB = (env.memory.total / (1024 * 1024 * 1024)).toFixed(2);
        const freeMemGB = (env.memory.free / (1024 * 1024 * 1024)).toFixed(2);
        report += `\n  Memory: ${totalMemGB} GB total, ${freeMemGB} GB free`;
      }

      // Add CPU information if available
      if (env.cpus && env.cpus.length) {
        report += `\n  CPUs: ${env.cpus.length} x ${env.cpus[0].model}`;
      }
    }
  }

  // Save the report to a file if outputPath is provided
  if (outputPath) {
    try {
      // Ensure the directory exists
      const dir = path.dirname(outputPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      // Write the report to the file
      fs.writeFileSync(outputPath, report);
      console.log(`Environment report saved to ${outputPath}`);
    } catch (error) {
      console.error(`Failed to save environment report to ${outputPath}: ${error.message}`);
    }
  }

  return report;
}

// Export the function
module.exports = {
  generateEnvironmentReport
};

// If this script is run directly, generate a report
if (require.main === module) {
  const args = process.argv.slice(2);
  const outputPath = args[0] || 'environment-report.txt';
  const formatJson = args.includes('--json');
  const includeEnvVars = args.includes('--env-vars');
  const verbose = args.includes('--verbose');

  generateEnvironmentReport({
    outputPath,
    formatJson,
    includeEnvVars,
    verbose
  });
}
