/**
 * Environment Detection Utility
 *
 * This module provides functions to detect and handle different environments:
 * - Operating Systems: Windows, macOS, Linux, WSL
 * - CI environments: GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines,
 *   TeamCity, Bitbucket, AppVeyor, Buildkite, Codefresh, Semaphore, Harness, and more
 * - Container environments: Docker, Kubernetes, rkt, containerd, CRI-O, Singularity
 * - Development vs Production vs Test vs Staging
 * - Browser vs Node.js
 * - Cloud environments: AWS, Azure, GCP, Alibaba Cloud, Tencent Cloud, Huawei Cloud, Oracle Cloud, IBM Cloud
 * - Serverless environments: AWS Lambda, Azure Functions, Google Cloud Functions
 *
 * It's designed to be used across the application to ensure consistent
 * environment detection and handling across all platforms and environments.
 */

/**
 * Detects the current environment
 * @returns {Object} Environment information
 */
export function detectEnvironment() {
  // Operating System Detection
  let platform = 'unknown';
  let isWindows = false;
  let isMacOS = false;
  let isLinux = false;
  let isBrowser = false;
  let isIOS = false;
  let isAndroid = false;
  let isMobile = false;
  let isElectron = false;
  let isWSL = false;

  // Browser Detection
  if (typeof window !== 'undefined' && typeof navigator !== 'undefined') {
    isBrowser = true;
    const userAgent = navigator.userAgent.toLowerCase();
    isWindows = userAgent.indexOf('windows') !== -1;
    isMacOS = userAgent.indexOf('macintosh') !== -1 || userAgent.indexOf('mac os') !== -1;
    isLinux = userAgent.indexOf('linux') !== -1 || userAgent.indexOf('x11') !== -1;
    isIOS = /ipad|iphone|ipod/.test(userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    isAndroid = userAgent.indexOf('android') !== -1;
    isMobile = isIOS || isAndroid || /mobile|tablet|ip(ad|hone|od)|android|silk|webos|blackberry|opera mini|windows (ce|phone)|iemobile|msie mobile|trident\/[678]\.0/i.test(userAgent);
    isElectron = userAgent.indexOf('electron') !== -1;

    // Set platform based on browser detection
    if (isWindows) platform = 'win32';
    else if (isMacOS) platform = 'darwin';
    else if (isLinux) platform = 'linux';
    else if (isIOS) platform = 'ios';
    else if (isAndroid) platform = 'android';
  }
  // Node.js Detection
  else if (typeof process !== 'undefined' && process.platform) {
    platform = process.platform;
    isWindows = platform === 'win32';
    isMacOS = platform === 'darwin';
    isLinux = platform === 'linux';

    // Electron detection in Node.js context
    isElectron = typeof process !== 'undefined' &&
                 process.versions &&
                 !!process.versions.electron;

    // WSL (Windows Subsystem for Linux) detection
    if (isLinux) {
      try {
        const fs = require('fs');
        const os = require('os');

        // Check for WSL-specific files or environment variables
        isWSL = fs.existsSync('/proc/version') &&
                fs.readFileSync('/proc/version', 'utf8').toLowerCase().includes('microsoft') ||
                os.release().toLowerCase().includes('microsoft') ||
                !!process.env.WSL_DISTRO_NAME;
      } catch (error) {
        // fs module not available or error reading file
        isWSL = false;
      }
    }
  }

  // CI Environment Detection
  const isCI = typeof process !== 'undefined' && (
    process.env.CI === 'true' || process.env.CI === true ||
    process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW ||
    !!process.env.JENKINS_URL || !!process.env.GITLAB_CI ||
    !!process.env.CIRCLECI || !!process.env.TRAVIS ||
    !!process.env.TF_BUILD || !!process.env.TEAMCITY_VERSION ||
    !!process.env.BITBUCKET_BUILD_NUMBER || !!process.env.APPVEYOR ||
    !!process.env.BUILDKITE || !!process.env.BUILDKITE_BUILD_ID ||
    !!process.env.CF_BUILD_ID || !!process.env.CODEFRESH_IO ||
    !!process.env.SEMAPHORE || !!process.env.SEMAPHORE_WORKFLOW_ID ||
    !!process.env.HARNESS_BUILD_ID || !!process.env.HARNESS_PIPELINE_ID
  );

  const isGitHubActions = typeof process !== 'undefined' && (
    process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW
  );

  const isJenkins = typeof process !== 'undefined' && !!process.env.JENKINS_URL;
  const isGitLabCI = typeof process !== 'undefined' && !!process.env.GITLAB_CI;
  const isCircleCI = typeof process !== 'undefined' && !!process.env.CIRCLECI;
  const isTravis = typeof process !== 'undefined' && !!process.env.TRAVIS;
  const isAzurePipelines = typeof process !== 'undefined' && !!process.env.TF_BUILD;
  const isTeamCity = typeof process !== 'undefined' && !!process.env.TEAMCITY_VERSION;
  const isBitbucket = typeof process !== 'undefined' && !!process.env.BITBUCKET_BUILD_NUMBER;
  const isAppVeyor = typeof process !== 'undefined' && !!process.env.APPVEYOR;

  // New CI platforms
  const isBuildkite = typeof process !== 'undefined' && (
    !!process.env.BUILDKITE || !!process.env.BUILDKITE_BUILD_ID
  );
  const isCodefresh = typeof process !== 'undefined' && (
    !!process.env.CF_BUILD_ID || !!process.env.CODEFRESH_IO
  );
  const isSemaphore = typeof process !== 'undefined' && (
    !!process.env.SEMAPHORE || !!process.env.SEMAPHORE_WORKFLOW_ID
  );
  const isHarness = typeof process !== 'undefined' && (
    !!process.env.HARNESS_BUILD_ID || !!process.env.HARNESS_PIPELINE_ID
  );

  // Container Environment Detection
  let isDocker = false;
  let isKubernetes = false;
  let isContainerized = false;
  let isRkt = false;
  let isContainerd = false;
  let isCRIO = false;
  let isSingularity = false;

  if (typeof process !== 'undefined') {
    try {
      const fs = require('fs');

      // Docker detection
      isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                process.env.DOCKER === 'true' ||
                fs.existsSync('/.dockerenv') ||
                fs.existsSync('/run/.containerenv') ||
                (fs.existsSync('/proc/1/cgroup') &&
                 fs.readFileSync('/proc/1/cgroup', 'utf8').includes('docker'));

      // Kubernetes detection
      isKubernetes = !!process.env.KUBERNETES_SERVICE_HOST ||
                    !!process.env.KUBERNETES_PORT ||
                    fs.existsSync('/var/run/secrets/kubernetes.io');

      // rkt detection
      isRkt = process.env.RKT_ENVIRONMENT === 'true' ||
             process.env.RKT === 'true' ||
             (fs.existsSync('/proc/1/cgroup') &&
              fs.readFileSync('/proc/1/cgroup', 'utf8').includes('rkt'));

      // containerd detection
      isContainerd = process.env.CONTAINERD_ENVIRONMENT === 'true' ||
                    process.env.CONTAINERD === 'true' ||
                    (fs.existsSync('/proc/1/cgroup') &&
                     fs.readFileSync('/proc/1/cgroup', 'utf8').includes('containerd'));

      // CRI-O detection
      isCRIO = process.env.CRIO_ENVIRONMENT === 'true' ||
              process.env.CRIO === 'true' ||
              (fs.existsSync('/proc/1/cgroup') &&
               fs.readFileSync('/proc/1/cgroup', 'utf8').includes('crio'));

      // Singularity detection
      isSingularity = process.env.SINGULARITY_ENVIRONMENT === 'true' ||
                     process.env.SINGULARITY === 'true' ||
                     !!process.env.SINGULARITY_CONTAINER ||
                     fs.existsSync('/.singularity.d') ||
                     fs.existsSync('/singularity');

      // General containerization detection
      isContainerized = isDocker || isKubernetes || isRkt || isContainerd || isCRIO || isSingularity ||
                       process.env.CONTAINER === 'true' ||
                       process.env.CONTAINERIZED === 'true';
    } catch (error) {
      // fs module not available in browser
      isDocker = process.env.DOCKER_ENVIRONMENT === 'true' || process.env.DOCKER === 'true';
      isKubernetes = !!process.env.KUBERNETES_SERVICE_HOST || !!process.env.KUBERNETES_PORT;
      isRkt = process.env.RKT_ENVIRONMENT === 'true' || process.env.RKT === 'true';
      isContainerd = process.env.CONTAINERD_ENVIRONMENT === 'true' || process.env.CONTAINERD === 'true';
      isCRIO = process.env.CRIO_ENVIRONMENT === 'true' || process.env.CRIO === 'true';
      isSingularity = process.env.SINGULARITY_ENVIRONMENT === 'true' ||
                     process.env.SINGULARITY === 'true' ||
                     !!process.env.SINGULARITY_CONTAINER;
      isContainerized = isDocker || isKubernetes || isRkt || isContainerd || isCRIO || isSingularity ||
                       process.env.CONTAINER === 'true' ||
                       process.env.CONTAINERIZED === 'true';
    }
  }

  // Cloud Environment Detection
  const isAWS = typeof process !== 'undefined' && (
    !!process.env.AWS_REGION ||
    !!process.env.AWS_LAMBDA_FUNCTION_NAME ||
    !!process.env.AWS_EXECUTION_ENV ||
    !!process.env.AWS_ACCESS_KEY_ID ||
    !!process.env.AWS_SECRET_ACCESS_KEY
  );

  const isAzure = typeof process !== 'undefined' && (
    !!process.env.AZURE_FUNCTIONS_ENVIRONMENT ||
    !!process.env.WEBSITE_SITE_NAME ||
    !!process.env.APPSETTING_WEBSITE_SITE_NAME ||
    !!process.env.AZURE_SUBSCRIPTION_ID ||
    !!process.env.AZURE_TENANT_ID
  );

  const isGCP = typeof process !== 'undefined' && (
    !!process.env.GOOGLE_CLOUD_PROJECT ||
    !!process.env.GCLOUD_PROJECT ||
    !!process.env.GCP_PROJECT ||
    !!process.env.FUNCTION_NAME && !!process.env.FUNCTION_REGION ||
    !!process.env.GOOGLE_APPLICATION_CREDENTIALS
  );

  // New cloud providers
  const isAlibabaCloud = typeof process !== 'undefined' && (
    !!process.env.ALIBABA_CLOUD_ACCESS_KEY_ID ||
    !!process.env.ALIBABA_CLOUD_ACCESS_KEY_SECRET ||
    !!process.env.ALICLOUD_ACCESS_KEY ||
    !!process.env.ALICLOUD_SECRET_KEY ||
    !!process.env.ALICLOUD_REGION
  );

  const isTencentCloud = typeof process !== 'undefined' && (
    !!process.env.TENCENTCLOUD_SECRET_ID ||
    !!process.env.TENCENTCLOUD_SECRET_KEY ||
    !!process.env.TENCENTCLOUD_REGION
  );

  const isHuaweiCloud = typeof process !== 'undefined' && (
    !!process.env.HUAWEICLOUD_ACCESS_KEY ||
    !!process.env.HUAWEICLOUD_SECRET_KEY ||
    !!process.env.HUAWEICLOUD_REGION
  );

  const isOracleCloud = typeof process !== 'undefined' && (
    !!process.env.OCI_RESOURCE_PRINCIPAL_VERSION ||
    !!process.env.OCI_COMPARTMENT_ID ||
    !!process.env.OCI_REGION ||
    !!process.env.OCI_TENANT_ID
  );

  const isIBMCloud = typeof process !== 'undefined' && (
    !!process.env.IBMCLOUD_API_KEY ||
    !!process.env.BLUEMIX_API_KEY ||
    !!process.env.BLUEMIX_REGION ||
    !!process.env.IBM_CLOUD_REGION
  );

  const isCloudEnvironment = isAWS || isAzure || isGCP ||
                            isAlibabaCloud || isTencentCloud || isHuaweiCloud ||
                            isOracleCloud || isIBMCloud;

  // Serverless Environment Detection
  const isLambda = typeof process !== 'undefined' && !!process.env.AWS_LAMBDA_FUNCTION_NAME;
  const isAzureFunctions = typeof process !== 'undefined' && !!process.env.AZURE_FUNCTIONS_ENVIRONMENT;
  const isCloudFunctions = typeof process !== 'undefined' &&
                          !!process.env.FUNCTION_NAME &&
                          !!process.env.FUNCTION_REGION;

  const isServerless = isLambda || isAzureFunctions || isCloudFunctions;

  // Node Environment Detection
  const isDevelopment = typeof process !== 'undefined' && process.env.NODE_ENV === 'development';
  const isProduction = typeof process !== 'undefined' && process.env.NODE_ENV === 'production';
  const isTest = typeof process !== 'undefined' && (
    process.env.NODE_ENV === 'test' ||
    process.env.JEST_WORKER_ID !== undefined ||
    process.env.VITEST !== undefined
  );
  const isStaging = typeof process !== 'undefined' && process.env.NODE_ENV === 'staging';

  // Verbose Logging
  const verboseLogging = typeof process !== 'undefined' && (
    process.env.VERBOSE_LOGGING === 'true' ||
    process.env.DEBUG === 'true' ||
    process.env.DEBUG_LEVEL === 'verbose' ||
    process.env.LOG_LEVEL === 'debug' ||
    process.env.LOG_LEVEL === 'trace'
  );

  // System Info
  const nodeVersion = typeof process !== 'undefined' ? process.version : 'N/A';
  const architecture = typeof process !== 'undefined' ? process.arch : 'N/A';

  // OS Info
  let osType = 'Unknown';
  let osRelease = 'Unknown';
  let tmpDir = '/tmp';
  let homeDir = '/home/user';
  let workingDir = '/';
  let hostname = 'localhost';
  let username = 'user';
  let memory = { total: 0, free: 0 };
  let cpus = [];

  if (typeof process !== 'undefined' && !isBrowser) {
    try {
      const os = require('os');
      osType = os.type();
      osRelease = os.release();
      tmpDir = os.tmpdir();
      homeDir = os.homedir();
      workingDir = process.cwd();
      hostname = os.hostname();
      username = os.userInfo().username;
      memory = {
        total: os.totalmem(),
        free: os.freemem()
      };
      cpus = os.cpus();
    } catch (error) {
      // os module not available
    }
  }

  return {
    // Operating System
    platform,
    isWindows,
    isMacOS,
    isLinux,
    isIOS,
    isAndroid,
    isMobile,
    isElectron,
    isWSL,

    // CI Environment
    isCI,
    isGitHubActions,
    isJenkins,
    isGitLabCI,
    isCircleCI,
    isTravis,
    isAzurePipelines,
    isTeamCity,
    isBitbucket,
    isAppVeyor,
    // New CI platforms
    isBuildkite,
    isCodefresh,
    isSemaphore,
    isHarness,

    // Container Environment
    isDocker,
    isKubernetes,
    isContainerized,
    // New container runtimes
    isRkt,
    isContainerd,
    isCRIO,
    isSingularity,

    // Cloud Environment
    isAWS,
    isAzure,
    isGCP,
    // New cloud providers
    isAlibabaCloud,
    isTencentCloud,
    isHuaweiCloud,
    isOracleCloud,
    isIBMCloud,
    isCloudEnvironment,

    // Serverless Environment
    isLambda,
    isAzureFunctions,
    isCloudFunctions,
    isServerless,

    // Node Environment
    isDevelopment,
    isProduction,
    isTest,
    isStaging,

    // Browser Environment
    isBrowser,

    // Logging
    verboseLogging,

    // System Info
    nodeVersion,
    architecture,
    osType,
    osRelease,
    tmpDir,
    homeDir,
    workingDir,
    hostname,
    username,
    memory,
    cpus
  };
}

/**
 * Creates a React hook for environment detection
 * @returns {Object} Environment information
 */
export function useEnvironment() {
  return detectEnvironment();
}

/**
 * Gets platform-specific path separator
 * @returns {string} Path separator ('/' or '\\')
 */
export function getPathSeparator() {
  const { isWindows } = detectEnvironment();
  return isWindows ? '\\' : '/';
}

/**
 * Converts a path to the current platform format
 * @param {string} inputPath - Path to convert
 * @returns {string} Platform-specific path
 */
export function getPlatformPath(inputPath) {
  const { isWindows } = detectEnvironment();

  if (isWindows && inputPath.includes('/')) {
    return inputPath.replace(/\//g, '\\');
  }

  if (!isWindows && inputPath.includes('\\')) {
    return inputPath.replace(/\\/g, '/');
  }

  return inputPath;
}

/**
 * Gets the current browser information
 * @returns {Object} Browser information
 */
export function getBrowserInfo() {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return {
      name: 'node',
      version: 'N/A',
      userAgent: 'N/A',
      isMobile: false,
      isTablet: false,
      isDesktop: true
    };
  }

  const userAgent = navigator.userAgent;
  const browsers = [
    { name: 'edge', regex: /Edge\/(\d+)/i },
    { name: 'edgeChromium', regex: /Edg\/(\d+)/i },
    { name: 'chrome', regex: /Chrome\/(\d+)/i },
    { name: 'firefox', regex: /Firefox\/(\d+)/i },
    { name: 'safari', regex: /Version\/(\d+).*Safari/i },
    { name: 'opera', regex: /OPR\/(\d+)/i },
    { name: 'ie', regex: /Trident.*rv:(\d+)/i }
  ];

  let name = 'unknown';
  let version = 'unknown';

  for (const browser of browsers) {
    const match = userAgent.match(browser.regex);
    if (match) {
      name = browser.name;
      version = match[1];
      break;
    }
  }

  // Mobile detection
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);

  // Tablet detection
  const isTablet = /iPad|Android(?!.*Mobile)/i.test(userAgent);

  // Desktop is neither mobile nor tablet
  const isDesktop = !isMobile && !isTablet;

  return {
    name,
    version,
    userAgent,
    isMobile,
    isTablet,
    isDesktop
  };
}

/**
 * Gets the current network information
 * @returns {Object} Network information
 */
export function getNetworkInfo() {
  if (typeof navigator === 'undefined' || !navigator.connection) {
    return {
      online: typeof navigator !== 'undefined' ? navigator.onLine : false,
      effectiveType: 'unknown',
      downlink: 0,
      rtt: 0,
      saveData: false
    };
  }

  const connection = navigator.connection;

  return {
    online: navigator.onLine,
    effectiveType: connection.effectiveType || 'unknown',
    downlink: connection.downlink || 0,
    rtt: connection.rtt || 0,
    saveData: connection.saveData || false
  };
}

/**
 * Gets the current screen information
 * @returns {Object} Screen information
 */
export function getScreenInfo() {
  if (typeof window === 'undefined' || typeof screen === 'undefined') {
    return {
      width: 0,
      height: 0,
      availWidth: 0,
      availHeight: 0,
      colorDepth: 0,
      orientation: 'unknown',
      pixelRatio: 1
    };
  }

  return {
    width: screen.width,
    height: screen.height,
    availWidth: screen.availWidth,
    availHeight: screen.availHeight,
    colorDepth: screen.colorDepth,
    orientation: screen.orientation ? screen.orientation.type : 'unknown',
    pixelRatio: window.devicePixelRatio || 1
  };
}

/**
 * Gets the current feature support information
 * @returns {Object} Feature support information
 */
export function getFeatureSupport() {
  if (typeof window === 'undefined') {
    return {
      localStorage: false,
      sessionStorage: false,
      cookies: false,
      webWorkers: false,
      serviceWorkers: false,
      webGL: false,
      canvas: false,
      webAssembly: false,
      geolocation: false,
      webRTC: false
    };
  }

  return {
    localStorage: !!window.localStorage,
    sessionStorage: !!window.sessionStorage,
    cookies: typeof document !== 'undefined' && 'cookie' in document,
    webWorkers: !!window.Worker,
    serviceWorkers: 'serviceWorker' in navigator,
    webGL: (function() {
      try {
        const canvas = document.createElement('canvas');
        return !!(window.WebGLRenderingContext &&
                 (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
      } catch (e) {
        return false;
      }
    })(),
    canvas: (function() {
      try {
        const canvas = document.createElement('canvas');
        return !!(canvas.getContext && canvas.getContext('2d'));
      } catch (e) {
        return false;
      }
    })(),
    webAssembly: typeof WebAssembly === 'object',
    geolocation: 'geolocation' in navigator,
    webRTC: !!(window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection)
  };
}

/**
 * Gets the current performance information
 * @returns {Object} Performance information
 */
export function getPerformanceInfo() {
  if (typeof performance === 'undefined') {
    return {
      memory: null,
      navigation: null,
      timing: null
    };
  }

  return {
    memory: performance.memory ? {
      jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
      totalJSHeapSize: performance.memory.totalJSHeapSize,
      usedJSHeapSize: performance.memory.usedJSHeapSize
    } : null,
    navigation: performance.navigation ? {
      redirectCount: performance.navigation.redirectCount,
      type: performance.navigation.type
    } : null,
    timing: performance.timing ? {
      connectEnd: performance.timing.connectEnd,
      connectStart: performance.timing.connectStart,
      domComplete: performance.timing.domComplete,
      domContentLoadedEventEnd: performance.timing.domContentLoadedEventEnd,
      domContentLoadedEventStart: performance.timing.domContentLoadedEventStart,
      domInteractive: performance.timing.domInteractive,
      domLoading: performance.timing.domLoading,
      domainLookupEnd: performance.timing.domainLookupEnd,
      domainLookupStart: performance.timing.domainLookupStart,
      fetchStart: performance.timing.fetchStart,
      loadEventEnd: performance.timing.loadEventEnd,
      loadEventStart: performance.timing.loadEventStart,
      navigationStart: performance.timing.navigationStart,
      redirectEnd: performance.timing.redirectEnd,
      redirectStart: performance.timing.redirectStart,
      requestStart: performance.timing.requestStart,
      responseEnd: performance.timing.responseEnd,
      responseStart: performance.timing.responseStart,
      secureConnectionStart: performance.timing.secureConnectionStart,
      unloadEventEnd: performance.timing.unloadEventEnd,
      unloadEventStart: performance.timing.unloadEventStart
    } : null
  };
}

/**
 * Gets the current environment information
 * @returns {Object} Complete environment information
 */
export function getEnvironmentInfo() {
  const env = detectEnvironment();

  // Add browser-specific information if in browser environment
  if (env.isBrowser) {
    return {
      ...env,
      browser: getBrowserInfo(),
      network: getNetworkInfo(),
      screen: getScreenInfo(),
      features: getFeatureSupport(),
      performance: getPerformanceInfo()
    };
  }

  return env;
}

// Export all functions
export default {
  detectEnvironment,
  useEnvironment,
  getPathSeparator,
  getPlatformPath,
  getBrowserInfo,
  getNetworkInfo,
  getScreenInfo,
  getFeatureSupport,
  getPerformanceInfo,
  getEnvironmentInfo
};
