/**
 * Mock Environment Integration Layer
 * Provides consistent environment access for mock implementations
 * @version 1.0.0
 */

const { detectEnvironment } = require('./environment-detection');

/**
 * Get a standardized environment object for mock implementations
 * @returns {Object} Standardized environment information
 */
function getMockEnvironment() {
  const env = detectEnvironment();
  
  return {
    // Core CI information
    isCI: env.isCI,
    platform: env.platform,
    
    // Enhanced CI provider detection
    ciPlatform: {
      isGitHubActions: env.ciProviders.gitHubActions,
      isJenkins: env.ciProviders.jenkins,
      isGitLabCI: env.ciProviders.gitLabCI,
      isCircleCI: env.ciProviders.circleCI,
      isAzure: env.ciProviders.azure,
      isTravis: env.ciProviders.travis,
      isTeamCity: env.ciProviders.teamCity,
      isVercel: env.ciProviders.vercel,
      isNetlify: env.ciProviders.netlify,
      provider: Object.entries(env.ciProviders)
        .find(([_, isActive]) => isActive)?.[0] || 'unknown'
    },
    
    // Container information
    container: {
      isContainer: env.container.isContainer,
      isDocker: env.container.type.docker,
      isPodman: env.container.type.podman,
      isKubernetes: env.container.type.kubernetes,
      type: Object.entries(env.container.type)
        .find(([_, isActive]) => isActive)?.[0] || 'none'
    },
    
    // Directory paths
    paths: {
      workspace: env.directories.workspace,
      temp: env.directories.temp,
      cache: env.directories.cache,
      home: env.directories.home
    },
    
    // Platform details
    system: {
      platform: env.platform.platform,
      isWindows: env.platform.isWindows,
      isMac: env.platform.isMac,
      isLinux: env.platform.isLinux,
      arch: env.platform.arch,
      nodeVersion: env.platform.nodeVersion
    },
    
    // Environment settings
    settings: {
      nodeEnv: env.env,
      verbose: process.env.VERBOSE_LOGGING === 'true'
    }
  };
}

module.exports = {
  getMockEnvironment
};
