/**
 * CI Environment Verification Script
 * 
 * This script verifies the CI environment detection functionality.
 * It can be run in any environment to check if the CI environment is correctly detected.
 */

const { detectCIEnvironmentType, createCIReport } = require('./helpers/ci-environment');
const { detectEnvironment } = require('./helpers/environment-detection');
const fs = require('fs');
const path = require('path');

// Create output directory if it doesn't exist
const outputDir = path.join(process.cwd(), 'ci-reports');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Detect environment
const env = detectEnvironment();
const ciType = detectCIEnvironmentType({ verbose: true });

// Create report
console.log(`Detected CI environment: ${ciType}`);
console.log(`CI: ${env.isCI ? 'Yes' : 'No'}`);
console.log(`GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}`);
console.log(`Jenkins: ${env.isJenkins ? 'Yes' : 'No'}`);
console.log(`GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}`);
console.log(`Circle CI: ${env.isCircleCI ? 'Yes' : 'No'}`);
console.log(`Travis CI: ${env.isTravis ? 'Yes' : 'No'}`);
console.log(`Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}`);
console.log(`TeamCity: ${env.isTeamCity ? 'Yes' : 'No'}`);
console.log(`Bitbucket: ${env.isBitbucket ? 'Yes' : 'No'}`);
console.log(`AppVeyor: ${env.isAppVeyor ? 'Yes' : 'No'}`);
console.log(`Drone CI: ${env.isDroneCI ? 'Yes' : 'No'}`);
console.log(`Buddy CI: ${env.isBuddyCI ? 'Yes' : 'No'}`);
console.log(`Buildkite: ${env.isBuildkite ? 'Yes' : 'No'}`);
console.log(`CodeBuild: ${env.isCodeBuild ? 'Yes' : 'No'}`);
console.log(`Vercel: ${env.isVercel ? 'Yes' : 'No'}`);
console.log(`Netlify: ${env.isNetlify ? 'Yes' : 'No'}`);
console.log(`Heroku: ${env.isHeroku ? 'Yes' : 'No'}`);
console.log(`Semaphore: ${env.isSemaphore ? 'Yes' : 'No'}`);
console.log(`Codefresh: ${env.isCodefresh ? 'Yes' : 'No'}`);
console.log(`Woodpecker: ${env.isWoodpecker ? 'Yes' : 'No'}`);
console.log(`Harness: ${env.isHarness ? 'Yes' : 'No'}`);
console.log(`Render: ${env.isRender ? 'Yes' : 'No'}`);
console.log(`Railway: ${env.isRailway ? 'Yes' : 'No'}`);
console.log(`Fly.io: ${env.isFlyio ? 'Yes' : 'No'}`);

// Create text report
const textReportPath = path.join(outputDir, 'ci-environment-report.txt');
createCIReport(textReportPath, {
  includeSystemInfo: true,
  includeEnvVars: false,
  verbose: true,
  includeContainers: true,
  includeCloud: true
});
console.log(`Text report created at ${textReportPath}`);

// Create JSON report
const jsonReportPath = path.join(outputDir, 'ci-environment-report.json');
createCIReport(jsonReportPath, {
  includeSystemInfo: true,
  includeEnvVars: true,
  verbose: true,
  formatJson: true
});
console.log(`JSON report created at ${jsonReportPath}`);

// Create CI-specific report
if (ciType !== 'none') {
  const ciSpecificDir = path.join(outputDir, ciType);
  if (!fs.existsSync(ciSpecificDir)) {
    fs.mkdirSync(ciSpecificDir, { recursive: true });
  }
  
  const ciSpecificReportPath = path.join(ciSpecificDir, 'environment-report.txt');
  createCIReport(ciSpecificReportPath, {
    includeSystemInfo: true,
    includeEnvVars: true,
    verbose: true
  });
  console.log(`CI-specific report created at ${ciSpecificReportPath}`);
}

console.log('CI environment verification complete');
