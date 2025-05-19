/**
 * Enhanced Environment Detection Helper
 *
 * This module provides comprehensive functions to detect and handle different environments:
 * - Operating Systems: Windows, macOS, Linux, WSL
 * - CI environments: GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines,
 *   TeamCity, Bitbucket, AppVeyor, Drone, Buddy, Buildkite, AWS CodeBuild, Vercel, Netlify,
 *   Heroku, Semaphore, Codefresh, Woodpecker, Harness, Render, Railway, Fly.io, Codemagic,
 *   GitHub Codespaces, Google Cloud Build, Alibaba Cloud DevOps, Huawei Cloud DevCloud,
 *   Tencent Cloud CODING, Baidu Cloud CICD, Sourcegraph, Gitpod, Replit, Stackblitz, Glitch, etc.
 * - Container environments: Docker, Podman, LXC/LXD, Containerd, CRI-O, Docker Compose, Kubernetes, Docker Swarm
 * - Cloud environments: AWS, Azure, GCP, Oracle Cloud, IBM Cloud, DigitalOcean, Linode, Vultr, Cloudflare
 * - Node.js environments: Development, Production, Test, Staging
 *
 * It's designed to be used across the application to ensure consistent
 * environment detection and handling with proper fallbacks.
 *
 * @version 2.2.0
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

/**
 * Safely check if a file exists with error handling
 * @param {string} filePath - Path to check
 * @returns {boolean} True if file exists, false otherwise
 */
function safeFileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (error) {
    console.warn(`Error checking if file exists at ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * Safely read a file with error handling
 * @param {string} filePath - Path to read
 * @param {string} [encoding='utf8'] - File encoding
 * @returns {string|null} File contents or null if error
 */
function safeReadFile(filePath, encoding = 'utf8') {
  try {
    return fs.readFileSync(filePath, encoding);
  } catch (error) {
    console.warn(`Error reading file at ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Detect the current environment with enhanced detection and fallbacks
 * @returns {Object} Comprehensive environment information
 */
function detectEnvironment() {
  // Operating System Detection with enhanced WSL detection
  const platform = os.platform();
  const isWindows = platform === 'win32';
  const isMacOS = platform === 'darwin';
  const isLinux = platform === 'linux';

  // WSL (Windows Subsystem for Linux) detection
  let isWSL = false;
  if (isLinux) {
    // Multiple detection methods for WSL with fallbacks
    isWSL = !!process.env.WSL_DISTRO_NAME ||
            !!process.env.WSLENV ||
            (safeFileExists('/proc/version') &&
             safeReadFile('/proc/version')?.toLowerCase().includes('microsoft')) ||
            os.release().toLowerCase().includes('microsoft');
  }

  // CI Environment Detection - enhanced with more CI platforms and improved detection methods
  const isCI = process.env.CI === 'true' || process.env.CI === '1' || process.env.CI === true ||
               process.env.CI_ENVIRONMENT === 'true' || process.env.CI_ENVIRONMENT === true ||
               process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW ||
               !!process.env.JENKINS_URL || !!process.env.GITLAB_CI ||
               !!process.env.CIRCLECI || !!process.env.TRAVIS ||
               !!process.env.TF_BUILD || !!process.env.TEAMCITY_VERSION ||
               !!process.env.BITBUCKET_COMMIT || !!process.env.BITBUCKET_BUILD_NUMBER ||
               !!process.env.APPVEYOR || !!process.env.DRONE ||
               !!process.env.BUDDY || !!process.env.BUDDY_WORKSPACE_ID ||
               !!process.env.BUILDKITE || !!process.env.CODEBUILD_BUILD_ID ||
               !!process.env.VERCEL || !!process.env.NOW_BUILDER ||
               !!process.env.NETLIFY || !!process.env.HEROKU_TEST_RUN_ID ||
               !!process.env.SEMAPHORE || !!process.env.CF_BUILD_ID ||
               (!!process.env.CI_PIPELINE_ID && !!process.env.CI_REPO) ||
               !!process.env.HARNESS_BUILD_ID || !!process.env.RENDER ||
               !!process.env.RAILWAY_ENVIRONMENT_ID || !!process.env.FLY_APP_NAME ||
               !!process.env.GITHUB_RUN_ID || !!process.env.JENKINS_HOME ||
               !!process.env.CIRCLE_BUILD_NUM || !!process.env.TRAVIS_JOB_ID ||
               !!process.env.AZURE_HTTP_USER_AGENT || !!process.env.SYSTEM_TEAMFOUNDATIONCOLLECTIONURI ||
               !!process.env.TEAMCITY_BUILD_PROPERTIES_FILE || !!process.env.APPVEYOR_BUILD_ID ||
               !!process.env.DRONE_BUILD_NUMBER || !!process.env.BUDDY_PIPELINE_ID ||
               !!process.env.BUILDKITE_BUILD_ID || !!process.env.CODEBUILD_BUILD_ARN ||
               !!process.env.HEROKU_APP_ID || !!process.env.SEMAPHORE_WORKFLOW_ID ||
               !!process.env.CI_TYPE || !!process.env.CI_PLATFORM || !!process.env.CI_RUNNER_OS ||
               // New CI platforms
               !!process.env.CM_BUILD_ID || !!process.env.CODEMAGIC_ID ||
               !!process.env.CODESPACE_NAME || !!process.env.GITHUB_CODESPACE_NAME ||
               !!process.env.CLOUD_BUILD || !!process.env.CLOUD_BUILD_ID ||
               !!process.env.ALIBABA_CLOUD || !!process.env.ALICLOUD_ACCOUNT_ID ||
               !!process.env.DEVCLOUD_PIPELINE_ID || !!process.env.HUAWEICLOUD_PIPELINE ||
               !!process.env.CODING_PIPELINE_ID || !!process.env.TENCENT_CLOUD_CI ||
               !!process.env.BAIDU_CLOUD_CI || !!process.env.BAIDU_PIPELINE_ID ||
               !!process.env.SOURCEGRAPH_EXECUTOR || !!process.env.SRC_EXECUTOR_NAME ||
               !!process.env.GITPOD_WORKSPACE_ID || !!process.env.GITPOD_WORKSPACE_URL ||
               !!process.env.REPL_ID || !!process.env.REPL_OWNER ||
               !!process.env.STACKBLITZ_ENV || !!process.env.STACKBLITZ_PROJECT_ID ||
               !!process.env.GLITCH_EDITOR_URL || !!process.env.GLITCH_PROJECT_ID;

  // Specific CI platform detection with improved detection methods
  const isGitHubActions = process.env.GITHUB_ACTIONS === 'true' ||
                         !!process.env.GITHUB_WORKFLOW ||
                         !!process.env.GITHUB_RUN_ID ||
                         !!process.env.GITHUB_REPOSITORY ||
                         !!process.env.GITHUB_WORKSPACE ||
                         !!process.env.GITHUB_SHA ||
                         (process.env.CI_PLATFORM === 'github') ||
                         (process.env.CI_TYPE === 'github');

  const isJenkins = !!process.env.JENKINS_URL ||
                   !!process.env.JENKINS_HOME ||
                   !!process.env.BUILD_ID && !!process.env.BUILD_URL && process.env.BUILD_URL.includes('jenkins') ||
                   (process.env.CI_PLATFORM === 'jenkins') ||
                   (process.env.CI_TYPE === 'jenkins');

  const isGitLabCI = !!process.env.GITLAB_CI ||
                    (!!process.env.CI_SERVER_NAME && process.env.CI_SERVER_NAME.includes('GitLab')) ||
                    !!process.env.CI_PROJECT_ID ||
                    !!process.env.CI_PIPELINE_ID ||
                    !!process.env.CI_COMMIT_SHA ||
                    (process.env.CI_PLATFORM === 'gitlab') ||
                    (process.env.CI_TYPE === 'gitlab');

  const isCircleCI = !!process.env.CIRCLECI ||
                    !!process.env.CIRCLE_BUILD_NUM ||
                    !!process.env.CIRCLE_JOB ||
                    !!process.env.CIRCLE_PROJECT_REPONAME ||
                    (process.env.CI_PLATFORM === 'circle') ||
                    (process.env.CI_TYPE === 'circle');

  const isTravis = !!process.env.TRAVIS ||
                  !!process.env.TRAVIS_JOB_ID ||
                  !!process.env.TRAVIS_BUILD_ID ||
                  !!process.env.TRAVIS_REPO_SLUG ||
                  (process.env.CI_PLATFORM === 'travis') ||
                  (process.env.CI_TYPE === 'travis');

  const isAzurePipelines = !!process.env.TF_BUILD ||
                          !!process.env.AZURE_HTTP_USER_AGENT ||
                          !!process.env.SYSTEM_TEAMFOUNDATIONCOLLECTIONURI ||
                          !!process.env.AGENT_JOBNAME ||
                          !!process.env.BUILD_BUILDID ||
                          (process.env.CI_PLATFORM === 'azure') ||
                          (process.env.CI_TYPE === 'azure');

  const isTeamCity = !!process.env.TEAMCITY_VERSION ||
                    !!process.env.TEAMCITY_BUILD_PROPERTIES_FILE ||
                    !!process.env.TEAMCITY_BUILDCONF_NAME ||
                    (process.env.CI_PLATFORM === 'teamcity') ||
                    (process.env.CI_TYPE === 'teamcity');

  const isBitbucket = !!process.env.BITBUCKET_COMMIT ||
                     !!process.env.BITBUCKET_BUILD_NUMBER ||
                     !!process.env.BITBUCKET_WORKSPACE ||
                     !!process.env.BITBUCKET_REPO_SLUG ||
                     (process.env.CI_PLATFORM === 'bitbucket') ||
                     (process.env.CI_TYPE === 'bitbucket');

  const isAppVeyor = !!process.env.APPVEYOR ||
                    !!process.env.APPVEYOR_BUILD_ID ||
                    !!process.env.APPVEYOR_BUILD_NUMBER ||
                    !!process.env.APPVEYOR_PROJECT_SLUG ||
                    (process.env.CI_PLATFORM === 'appveyor') ||
                    (process.env.CI_TYPE === 'appveyor');

  const isDroneCI = !!process.env.DRONE ||
                   !!process.env.DRONE_BUILD_NUMBER ||
                   !!process.env.DRONE_BRANCH ||
                   !!process.env.DRONE_COMMIT ||
                   (process.env.CI_PLATFORM === 'drone') ||
                   (process.env.CI_TYPE === 'drone');

  const isBuddyCI = !!process.env.BUDDY ||
                   !!process.env.BUDDY_PIPELINE_ID ||
                   !!process.env.BUDDY_WORKSPACE_ID ||
                   !!process.env.BUDDY_EXECUTION_ID ||
                   (process.env.CI_PLATFORM === 'buddy') ||
                   (process.env.CI_TYPE === 'buddy');

  const isBuildkite = !!process.env.BUILDKITE ||
                     !!process.env.BUILDKITE_BUILD_ID ||
                     !!process.env.BUILDKITE_PIPELINE_SLUG ||
                     !!process.env.BUILDKITE_COMMIT ||
                     (process.env.CI_PLATFORM === 'buildkite') ||
                     (process.env.CI_TYPE === 'buildkite');

  const isCodeBuild = !!process.env.CODEBUILD_BUILD_ID ||
                     !!process.env.CODEBUILD_BUILD_ARN ||
                     !!process.env.CODEBUILD_INITIATOR ||
                     (process.env.CI_PLATFORM === 'codebuild') ||
                     (process.env.CI_TYPE === 'codebuild');

  const isVercel = !!process.env.VERCEL ||
                  !!process.env.NOW_BUILDER ||
                  !!process.env.VERCEL_ENV ||
                  !!process.env.VERCEL_URL ||
                  (process.env.CI_PLATFORM === 'vercel') ||
                  (process.env.CI_TYPE === 'vercel');

  const isNetlify = !!process.env.NETLIFY ||
                   !!process.env.NETLIFY_IMAGES_CDN_DOMAIN ||
                   !!process.env.NETLIFY_SITE_ID ||
                   (process.env.CI_PLATFORM === 'netlify') ||
                   (process.env.CI_TYPE === 'netlify');

  const isHeroku = !!process.env.HEROKU_TEST_RUN_ID ||
                  !!process.env.HEROKU_APP_ID ||
                  !!process.env.HEROKU_APP_NAME ||
                  !!process.env.HEROKU_DYNO_ID ||
                  (process.env.CI_PLATFORM === 'heroku') ||
                  (process.env.CI_TYPE === 'heroku');

  const isSemaphore = !!process.env.SEMAPHORE ||
                     !!process.env.SEMAPHORE_WORKFLOW_ID ||
                     !!process.env.SEMAPHORE_GIT_BRANCH ||
                     !!process.env.SEMAPHORE_GIT_SHA ||
                     (process.env.CI_PLATFORM === 'semaphore') ||
                     (process.env.CI_TYPE === 'semaphore');

  const isCodefresh = !!process.env.CF_BUILD_ID ||
                     !!process.env.CF_PIPELINE_NAME ||
                     !!process.env.CF_BRANCH ||
                     (process.env.CI_PLATFORM === 'codefresh') ||
                     (process.env.CI_TYPE === 'codefresh');

  const isWoodpecker = (!!process.env.CI_PIPELINE_ID && !!process.env.CI_REPO) ||
                      !!process.env.CI_PIPELINE_NAME ||
                      !!process.env.CI_PIPELINE_NUMBER ||
                      (process.env.CI_PLATFORM === 'woodpecker') ||
                      (process.env.CI_TYPE === 'woodpecker');

  const isHarness = !!process.env.HARNESS_BUILD_ID ||
                   !!process.env.HARNESS_ACCOUNT_ID ||
                   !!process.env.HARNESS_PIPELINE_ID ||
                   (process.env.CI_PLATFORM === 'harness') ||
                   (process.env.CI_TYPE === 'harness');

  const isRender = !!process.env.RENDER ||
                  !!process.env.RENDER_SERVICE_ID ||
                  !!process.env.RENDER_INSTANCE_ID ||
                  (process.env.CI_PLATFORM === 'render') ||
                  (process.env.CI_TYPE === 'render');

  const isRailway = !!process.env.RAILWAY_ENVIRONMENT_ID ||
                   !!process.env.RAILWAY_PROJECT_ID ||
                   !!process.env.RAILWAY_SERVICE_ID ||
                   (process.env.CI_PLATFORM === 'railway') ||
                   (process.env.CI_TYPE === 'railway');

  const isFlyio = !!process.env.FLY_APP_NAME ||
                 !!process.env.FLY_REGION ||
                 !!process.env.FLY_ALLOC_ID ||
                 (process.env.CI_PLATFORM === 'flyio') ||
                 (process.env.CI_TYPE === 'flyio');

  // New CI platforms

  // Codemagic CI/CD for mobile apps
  const isCodemagic = !!process.env.CM_BUILD_ID ||
                     !!process.env.CODEMAGIC_ID ||
                     !!process.env.CM_BUILD_DIR ||
                     !!process.env.CM_REPO_SLUG ||
                     (process.env.CI_PLATFORM === 'codemagic') ||
                     (process.env.CI_TYPE === 'codemagic');

  // GitHub Codespaces
  const isGitHubCodespaces = !!process.env.CODESPACE_NAME ||
                            !!process.env.GITHUB_CODESPACE_NAME ||
                            !!process.env.CODESPACES ||
                            !!process.env.GITHUB_CODESPACES ||
                            (process.env.CI_PLATFORM === 'github-codespaces') ||
                            (process.env.CI_TYPE === 'github-codespaces');

  // Google Cloud Build
  const isGoogleCloudBuild = !!process.env.CLOUD_BUILD ||
                            !!process.env.CLOUD_BUILD_ID ||
                            !!process.env.CLOUD_BUILD_PROJECT_ID ||
                            !!process.env.CLOUD_BUILD_TRIGGER_ID ||
                            (process.env.CI_PLATFORM === 'google-cloud-build') ||
                            (process.env.CI_TYPE === 'google-cloud-build');

  // Alibaba Cloud DevOps
  const isAlibabaCloud = !!process.env.ALIBABA_CLOUD ||
                        !!process.env.ALICLOUD_ACCOUNT_ID ||
                        !!process.env.ALICLOUD_PIPELINE_ID ||
                        !!process.env.ALICLOUD_BUILD_ID ||
                        (process.env.CI_PLATFORM === 'alibaba-cloud') ||
                        (process.env.CI_TYPE === 'alibaba-cloud');

  // Huawei Cloud DevCloud
  const isHuaweiCloud = !!process.env.DEVCLOUD_PIPELINE_ID ||
                       !!process.env.HUAWEICLOUD_PIPELINE ||
                       !!process.env.HUAWEICLOUD_BUILD_ID ||
                       !!process.env.HUAWEICLOUD_PROJECT_ID ||
                       (process.env.CI_PLATFORM === 'huawei-cloud') ||
                       (process.env.CI_TYPE === 'huawei-cloud');

  // Tencent Cloud CODING
  const isTencentCloud = !!process.env.CODING_PIPELINE_ID ||
                        !!process.env.TENCENT_CLOUD_CI ||
                        !!process.env.CODING_BUILD_ID ||
                        !!process.env.CODING_PROJECT_NAME ||
                        (process.env.CI_PLATFORM === 'tencent-cloud') ||
                        (process.env.CI_TYPE === 'tencent-cloud');

  // Baidu Cloud CICD
  const isBaiduCloud = !!process.env.BAIDU_CLOUD_CI ||
                      !!process.env.BAIDU_PIPELINE_ID ||
                      !!process.env.BAIDU_BUILD_ID ||
                      !!process.env.BAIDU_PROJECT_ID ||
                      (process.env.CI_PLATFORM === 'baidu-cloud') ||
                      (process.env.CI_TYPE === 'baidu-cloud');

  // Sourcegraph
  const isSourcegraph = !!process.env.SOURCEGRAPH_EXECUTOR ||
                       !!process.env.SRC_EXECUTOR_NAME ||
                       !!process.env.SOURCEGRAPH_REPO ||
                       !!process.env.SOURCEGRAPH_COMMIT ||
                       (process.env.CI_PLATFORM === 'sourcegraph') ||
                       (process.env.CI_TYPE === 'sourcegraph');

  // Gitpod
  const isGitpod = !!process.env.GITPOD_WORKSPACE_ID ||
                  !!process.env.GITPOD_WORKSPACE_URL ||
                  !!process.env.GITPOD_REPO_ROOT ||
                  !!process.env.GITPOD_INSTANCE_ID ||
                  (process.env.CI_PLATFORM === 'gitpod') ||
                  (process.env.CI_TYPE === 'gitpod');

  // Replit
  const isReplit = !!process.env.REPL_ID ||
                  !!process.env.REPL_OWNER ||
                  !!process.env.REPL_SLUG ||
                  !!process.env.REPL_PUBKEYS ||
                  (process.env.CI_PLATFORM === 'replit') ||
                  (process.env.CI_TYPE === 'replit');

  // Stackblitz
  const isStackblitz = !!process.env.STACKBLITZ_ENV ||
                      !!process.env.STACKBLITZ_PROJECT_ID ||
                      !!process.env.STACKBLITZ_WORKSPACE_ID ||
                      !!process.env.STACKBLITZ_USER_ID ||
                      (process.env.CI_PLATFORM === 'stackblitz') ||
                      (process.env.CI_TYPE === 'stackblitz');

  // Glitch
  const isGlitch = !!process.env.GLITCH_EDITOR_URL ||
                  !!process.env.GLITCH_PROJECT_ID ||
                  !!process.env.GLITCH_PROJECT_DOMAIN ||
                  !!process.env.PROJECT_DOMAIN ||
                  !!process.env.PROJECT_ID ||
                  (process.env.CI_PLATFORM === 'glitch') ||
                  (process.env.CI_TYPE === 'glitch');

  // Container Environment Detection - enhanced with more container platforms and improved detection methods
  // Docker detection with multiple methods and fallbacks
  const isDockerEnvironment = process.env.DOCKER_ENVIRONMENT === 'true' ||
                             process.env.DOCKER === 'true' ||
                             process.env.CONTAINER === 'true' ||
                             process.env.CONTAINERIZED === 'true' ||
                             process.env.DOCKER_CONTAINER === 'true' ||
                             process.env.DOCKER_CONTAINER_ID !== undefined ||
                             process.env.DOCKER_IMAGE !== undefined ||
                             process.env.DOCKER_IMAGE_ID !== undefined ||
                             safeFileExists('/.dockerenv') ||
                             safeFileExists('/run/.containerenv') ||
                             (safeFileExists('/proc/1/cgroup') && safeReadFile('/proc/1/cgroup')?.includes('docker')) ||
                             (safeFileExists('/proc/self/cgroup') && safeReadFile('/proc/self/cgroup')?.includes('docker')) ||
                             (process.env.CI_PLATFORM === 'docker') ||
                             (process.env.CI_TYPE === 'docker') ||
                             (process.env.TEMP_DOCKER_DIR !== undefined); // For testing purposes

  // Podman detection
  const isPodman = process.env.PODMAN_ENVIRONMENT === 'true' ||
                  process.env.PODMAN === 'true' ||
                  (safeFileExists('/proc/1/cgroup') && safeReadFile('/proc/1/cgroup')?.includes('podman')) ||
                  (safeFileExists('/proc/self/cgroup') && safeReadFile('/proc/self/cgroup')?.includes('podman')) ||
                  (process.env.CI_PLATFORM === 'podman') ||
                  (process.env.CI_TYPE === 'podman');

  // LXC/LXD detection
  const isLXC = process.env.LXC_ENVIRONMENT === 'true' ||
               process.env.LXC === 'true' ||
               process.env.LXD === 'true' ||
               (safeFileExists('/proc/1/cgroup') && safeReadFile('/proc/1/cgroup')?.includes('lxc')) ||
               (safeFileExists('/proc/self/cgroup') && safeReadFile('/proc/self/cgroup')?.includes('lxc')) ||
               safeFileExists('/dev/.lxc') ||
               safeFileExists('/dev/.lxd') ||
               (process.env.CI_PLATFORM === 'lxc') ||
               (process.env.CI_TYPE === 'lxc');

  // Containerd detection
  const isContainerd = process.env.CONTAINERD_ENVIRONMENT === 'true' ||
                      process.env.CONTAINERD === 'true' ||
                      (safeFileExists('/proc/1/cgroup') && safeReadFile('/proc/1/cgroup')?.includes('containerd')) ||
                      (safeFileExists('/proc/self/cgroup') && safeReadFile('/proc/self/cgroup')?.includes('containerd')) ||
                      (process.env.CI_PLATFORM === 'containerd') ||
                      (process.env.CI_TYPE === 'containerd');

  // CRI-O detection
  const isCRIO = process.env.CRIO_ENVIRONMENT === 'true' ||
                process.env.CRIO === 'true' ||
                (safeFileExists('/proc/1/cgroup') && safeReadFile('/proc/1/cgroup')?.includes('crio')) ||
                (safeFileExists('/proc/self/cgroup') && safeReadFile('/proc/self/cgroup')?.includes('crio')) ||
                (process.env.CI_PLATFORM === 'crio') ||
                (process.env.CI_TYPE === 'crio');

  // Kubernetes detection with improved methods
  const isKubernetesEnv = !!process.env.KUBERNETES_SERVICE_HOST ||
                         !!process.env.KUBERNETES_PORT ||
                         !!process.env.KUBERNETES_NAMESPACE ||
                         !!process.env.KUBERNETES_NODE_NAME ||
                         !!process.env.KUBERNETES_POD_NAME ||
                         !!process.env.K8S_SERVICE_HOST ||
                         !!process.env.K8S_NAMESPACE ||
                         !!process.env.K8S_POD_NAME ||
                         safeFileExists('/var/run/secrets/kubernetes.io') ||
                         safeFileExists('/var/run/secrets/kubernetes.io/serviceaccount/token') ||
                         safeFileExists('/var/run/secrets/kubernetes.io/serviceaccount/namespace') ||
                         (process.env.CI_PLATFORM === 'kubernetes') ||
                         (process.env.CI_TYPE === 'kubernetes') ||
                         (process.env.TEMP_K8S_DIR !== undefined); // For testing purposes

  // Kubernetes distribution detection
  const isOpenShift = !!process.env.OPENSHIFT_BUILD_NAME ||
                     !!process.env.OPENSHIFT_BUILD_NAMESPACE ||
                     safeFileExists('/var/run/secrets/kubernetes.io/serviceaccount/namespace') &&
                     safeReadFile('/var/run/secrets/kubernetes.io/serviceaccount/namespace')?.includes('openshift');

  const isGKE = !!process.env.KUBERNETES_SERVICE_HOST &&
               (!!process.env.GKE_CLUSTER_NAME ||
                !!process.env.GKE_CLUSTER_REGION ||
                !!process.env.GCLOUD_PROJECT);

  const isEKS = !!process.env.KUBERNETES_SERVICE_HOST &&
               (!!process.env.AWS_REGION ||
                !!process.env.AWS_CLUSTER_NAME ||
                !!process.env.EKS_CLUSTER_NAME);

  const isAKS = !!process.env.KUBERNETES_SERVICE_HOST &&
               (!!process.env.AKS_CLUSTER_NAME ||
                !!process.env.AZURE_SUBSCRIPTION_ID);

  // Docker Compose detection with improved methods
  const isDockerCompose = !!process.env.COMPOSE_PROJECT_NAME ||
                         !!process.env.COMPOSE_FILE ||
                         !!process.env.COMPOSE_PATH_SEPARATOR ||
                         !!process.env.COMPOSE_SERVICE_NAME ||
                         !!process.env.COMPOSE_API_VERSION ||
                         !!process.env.COMPOSE_PROFILES ||
                         (process.env.CI_PLATFORM === 'docker-compose') ||
                         (process.env.CI_TYPE === 'docker-compose');

  // Docker Swarm detection with improved methods
  const isDockerSwarm = !!process.env.DOCKER_SWARM ||
                       !!process.env.SWARM_NODE_ID ||
                       !!process.env.SWARM_MANAGER ||
                       !!process.env.SWARM_SERVICE_ID ||
                       !!process.env.SWARM_SERVICE_NAME ||
                       !!process.env.SWARM_TASK_ID ||
                       (process.env.CI_PLATFORM === 'docker-swarm') ||
                       (process.env.CI_TYPE === 'docker-swarm');

  // Cloud Environment Detection with improved methods and additional cloud providers
  const isAWSEnv = !!process.env.AWS_REGION ||
                  !!process.env.AWS_DEFAULT_REGION ||
                  !!process.env.AWS_LAMBDA_FUNCTION_NAME ||
                  !!process.env.AWS_EXECUTION_ENV ||
                  !!process.env.AWS_ACCESS_KEY_ID ||
                  !!process.env.AWS_SECRET_ACCESS_KEY ||
                  !!process.env.AWS_SESSION_TOKEN ||
                  !!process.env.AWS_ACCOUNT_ID ||
                  !!process.env.EC2_INSTANCE_ID ||
                  !!process.env.AWS_CONTAINER_CREDENTIALS_RELATIVE_URI ||
                  !!process.env.AWS_ECS_CONTAINER_METADATA_URI ||
                  !!process.env.AWS_INSTANCE_ID ||
                  (process.env.CI_PLATFORM === 'aws') ||
                  (process.env.CI_TYPE === 'aws');

  // AWS Lambda detection
  const isAWSLambda = !!process.env.AWS_LAMBDA_FUNCTION_NAME ||
                     !!process.env.AWS_LAMBDA_FUNCTION_VERSION ||
                     !!process.env.AWS_LAMBDA_FUNCTION_MEMORY_SIZE ||
                     !!process.env.AWS_EXECUTION_ENV?.includes('Lambda') ||
                     !!process.env.LAMBDA_TASK_ROOT ||
                     !!process.env.LAMBDA_RUNTIME_DIR ||
                     (process.env.CI_PLATFORM === 'aws-lambda') ||
                     (process.env.CI_TYPE === 'aws-lambda');

  // AWS ECS detection
  const isAWSECS = !!process.env.ECS_CONTAINER_METADATA_URI ||
                  !!process.env.AWS_EXECUTION_ENV?.includes('ECS') ||
                  !!process.env.ECS_CLUSTER ||
                  !!process.env.ECS_TASK_DEFINITION ||
                  (process.env.CI_PLATFORM === 'aws-ecs') ||
                  (process.env.CI_TYPE === 'aws-ecs');

  // AWS Fargate detection
  const isAWSFargate = !!process.env.AWS_EXECUTION_ENV?.includes('Fargate') ||
                      (!!process.env.ECS_CONTAINER_METADATA_URI && !!process.env.AWS_EXECUTION_ENV) ||
                      (process.env.CI_PLATFORM === 'aws-fargate') ||
                      (process.env.CI_TYPE === 'aws-fargate');

  // Azure Environment detection with improved methods
  const isAzureEnv = !!process.env.AZURE_FUNCTIONS_ENVIRONMENT ||
                    !!process.env.WEBSITE_SITE_NAME ||
                    !!process.env.APPSETTING_WEBSITE_SITE_NAME ||
                    !!process.env.AZURE_SUBSCRIPTION_ID ||
                    !!process.env.AZURE_TENANT_ID ||
                    !!process.env.AZURE_RESOURCE_GROUP ||
                    !!process.env.AZURE_LOCATION ||
                    !!process.env.AZURE_WEBAPP_NAME ||
                    (process.env.CI_PLATFORM === 'azure') ||
                    (process.env.CI_TYPE === 'azure');

  // Azure Functions detection
  const isAzureFunctions = !!process.env.AZURE_FUNCTIONS_ENVIRONMENT ||
                          !!process.env.FUNCTIONS_WORKER_RUNTIME ||
                          !!process.env.FUNCTIONS_EXTENSION_VERSION ||
                          !!process.env.AzureWebJobsStorage ||
                          (process.env.CI_PLATFORM === 'azure-functions') ||
                          (process.env.CI_TYPE === 'azure-functions');

  // Azure App Service detection
  const isAzureAppService = !!process.env.WEBSITE_SITE_NAME ||
                           !!process.env.WEBSITE_INSTANCE_ID ||
                           !!process.env.WEBSITE_RESOURCE_GROUP ||
                           (process.env.CI_PLATFORM === 'azure-app-service') ||
                           (process.env.CI_TYPE === 'azure-app-service');

  // GCP Environment detection with improved methods
  const isGCPEnv = !!process.env.GOOGLE_CLOUD_PROJECT ||
                  !!process.env.GCLOUD_PROJECT ||
                  !!process.env.GCP_PROJECT ||
                  !!process.env.GOOGLE_COMPUTE_ZONE ||
                  !!process.env.GOOGLE_COMPUTE_REGION ||
                  (!!process.env.FUNCTION_NAME && !!process.env.FUNCTION_REGION) ||
                  (process.env.CI_PLATFORM === 'gcp') ||
                  (process.env.CI_TYPE === 'gcp');

  // GCP Cloud Functions detection
  const isGCPCloudFunctions = (!!process.env.FUNCTION_NAME && !!process.env.FUNCTION_REGION) ||
                             !!process.env.FUNCTION_MEMORY_MB ||
                             !!process.env.FUNCTION_TIMEOUT_SEC ||
                             !!process.env.FUNCTION_IDENTITY ||
                             (process.env.CI_PLATFORM === 'gcp-cloud-functions') ||
                             (process.env.CI_TYPE === 'gcp-cloud-functions');

  // GCP Cloud Run detection
  const isGCPCloudRun = !!process.env.K_SERVICE ||
                       !!process.env.K_REVISION ||
                       !!process.env.K_CONFIGURATION ||
                       !!process.env.PORT && !!process.env.GOOGLE_CLOUD_PROJECT ||
                       (process.env.CI_PLATFORM === 'gcp-cloud-run') ||
                       (process.env.CI_TYPE === 'gcp-cloud-run');

  // Additional Cloud Providers

  // Oracle Cloud Infrastructure (OCI) detection
  const isOCI = !!process.env.OCI_RESOURCE_PRINCIPAL_VERSION ||
               !!process.env.OCI_COMPARTMENT_ID ||
               !!process.env.OCI_REGION ||
               !!process.env.OCI_TENANT_ID ||
               (process.env.CI_PLATFORM === 'oci') ||
               (process.env.CI_TYPE === 'oci');

  // IBM Cloud detection
  const isIBMCloud = !!process.env.BLUEMIX_REGION ||
                    !!process.env.BLUEMIX_API_KEY ||
                    !!process.env.IBM_CLOUD_API_KEY ||
                    !!process.env.VCAP_SERVICES ||
                    (process.env.CI_PLATFORM === 'ibm-cloud') ||
                    (process.env.CI_TYPE === 'ibm-cloud');

  // DigitalOcean detection
  const isDigitalOcean = !!process.env.DIGITALOCEAN_ACCESS_TOKEN ||
                        !!process.env.DIGITALOCEAN_REGION ||
                        !!process.env.DIGITALOCEAN_DROPLET_ID ||
                        (process.env.CI_PLATFORM === 'digitalocean') ||
                        (process.env.CI_TYPE === 'digitalocean');

  // Linode detection
  const isLinode = !!process.env.LINODE_API_TOKEN ||
                  !!process.env.LINODE_REGION ||
                  !!process.env.LINODE_INSTANCE_ID ||
                  (process.env.CI_PLATFORM === 'linode') ||
                  (process.env.CI_TYPE === 'linode');

  // Vultr detection
  const isVultr = !!process.env.VULTR_API_KEY ||
                 !!process.env.VULTR_REGION ||
                 !!process.env.VULTR_INSTANCE_ID ||
                 (process.env.CI_PLATFORM === 'vultr') ||
                 (process.env.CI_TYPE === 'vultr');

  // Cloudflare detection
  const isCloudflare = !!process.env.CLOUDFLARE_API_TOKEN ||
                      !!process.env.CLOUDFLARE_ZONE_ID ||
                      !!process.env.CLOUDFLARE_ACCOUNT_ID ||
                      !!process.env.CF_PAGES ||
                      (process.env.CI_PLATFORM === 'cloudflare') ||
                      (process.env.CI_TYPE === 'cloudflare');

  // Serverless environment detection
  const isServerless = isAWSLambda || isAzureFunctions || isGCPCloudFunctions ||
                      !!process.env.SERVERLESS ||
                      !!process.env.SERVERLESS_PLATFORM ||
                      !!process.env.SERVERLESS_SERVICE ||
                      (process.env.CI_PLATFORM === 'serverless') ||
                      (process.env.CI_TYPE === 'serverless');

  // Node Environment Detection - enhanced with staging and test frameworks
  const isDevelopment = process.env.NODE_ENV === 'development';
  const isProduction = process.env.NODE_ENV === 'production';
  const isTest = process.env.NODE_ENV === 'test' ||
                process.env.NODE_ENV === 'testing' ||
                !!process.env.JEST_WORKER_ID ||
                !!process.env.VITEST !== undefined;
  const isStaging = process.env.NODE_ENV === 'staging';

  // Browser Detection (only valid in browser environment)
  const isBrowser = typeof window !== 'undefined' && typeof window.document !== 'undefined';

  // Verbose Logging
  const verboseLogging = process.env.VERBOSE_LOGGING === 'true' ||
                        process.env.DEBUG === 'true' ||
                        process.env.DEBUG_LEVEL === 'verbose' ||
                        process.env.LOG_LEVEL === 'debug' ||
                        process.env.LOG_LEVEL === 'trace' ||
                        isCI;

  // System Info with enhanced error handling
  let osType = 'Unknown';
  let osRelease = 'Unknown';
  let tmpDir = '/tmp';
  let homeDir = '/home/user';
  let workingDir = '/';
  let hostname = 'localhost';
  let username = 'user';
  let memory = { total: 0, free: 0 };
  let cpus = [];

  try {
    osType = os.type();
    osRelease = os.release();
    tmpDir = os.tmpdir();
    homeDir = os.homedir();
    workingDir = process.cwd();
    hostname = os.hostname();

    try {
      username = os.userInfo().username;
    } catch (userError) {
      console.warn(`Error getting username: ${userError.message}`);
      username = process.env.USER || process.env.USERNAME || 'unknown';
    }

    memory = {
      total: os.totalmem(),
      free: os.freemem()
    };

    cpus = os.cpus();
  } catch (osError) {
    console.warn(`Error getting system info: ${osError.message}`);
  }

  return {
    // Operating System
    platform,
    isWindows,
    isMacOS,
    isLinux,
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
    isDroneCI,
    isBuddyCI,
    isBuildkite,
    isCodeBuild,
    isVercel,
    isNetlify,
    isHeroku,
    isSemaphore,
    isCodefresh,
    isWoodpecker,
    isHarness,
    isRender,
    isRailway,
    isFlyio,
    // New CI platforms
    isCodemagic,
    isGitHubCodespaces,
    isGoogleCloudBuild,
    isAlibabaCloud,
    isHuaweiCloud,
    isTencentCloud,
    isBaiduCloud,
    isSourcegraph,
    isGitpod,
    isReplit,
    isStackblitz,
    isGlitch,

    // Container Environment
    isDocker: isDockerEnvironment,
    isPodman,
    isLXC,
    isContainerd,
    isCRIO,
    isKubernetes: isKubernetesEnv,
    isDockerCompose,
    isDockerSwarm,
    isContainerized: isDockerEnvironment || isKubernetesEnv || isDockerCompose || isDockerSwarm ||
                     isPodman || isLXC || isContainerd || isCRIO,

    // Kubernetes Distributions
    isOpenShift,
    isGKE,
    isEKS,
    isAKS,

    // Cloud Environment
    isAWS: isAWSEnv,
    isAzure: isAzureEnv,
    isGCP: isGCPEnv,
    isOCI,
    isIBMCloud,
    isDigitalOcean,
    isLinode,
    isVultr,
    isCloudflare,
    isCloudEnvironment: isAWSEnv || isAzureEnv || isGCPEnv || isOCI || isIBMCloud ||
                        isDigitalOcean || isLinode || isVultr || isCloudflare,

    // AWS Services
    isAWSLambda,
    isAWSECS,
    isAWSFargate,

    // Azure Services
    isAzureFunctions,
    isAzureAppService,

    // GCP Services
    isGCPCloudFunctions,
    isGCPCloudRun,

    // Serverless
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
    nodeVersion: process.version,
    architecture: process.arch,
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
 * Create a comprehensive environment report with all detected information
 * @param {string} [filePath] - Optional file path to write the report to
 * @param {Object} [options] - Report options
 * @param {boolean} [options.includeEnvVars=false] - Whether to include all environment variables
 * @param {boolean} [options.includeSystemInfo=true] - Whether to include detailed system info
 * @param {boolean} [options.formatJson=false] - Whether to format as JSON instead of text
 * @returns {string} Environment report
 */
function createEnvironmentReport(filePath, options = {}) {
  const env = detectEnvironment();
  const {
    includeEnvVars = false,
    includeSystemInfo = true,
    formatJson = false
  } = options;

  // If JSON format is requested, return JSON
  if (formatJson) {
    const reportObj = {
      timestamp: new Date().toISOString(),
      operatingSystem: {
        platform: env.platform,
        type: env.osType,
        release: env.osRelease,
        isWindows: env.isWindows,
        isMacOS: env.isMacOS,
        isLinux: env.isLinux,
        isWSL: env.isWSL
      },
      ciEnvironment: {
        isCI: env.isCI,
        isGitHubActions: env.isGitHubActions,
        isJenkins: env.isJenkins,
        isGitLabCI: env.isGitLabCI,
        isCircleCI: env.isCircleCI,
        isTravis: env.isTravis,
        isAzurePipelines: env.isAzurePipelines,
        isTeamCity: env.isTeamCity,
        isBitbucket: env.isBitbucket,
        isAppVeyor: env.isAppVeyor,
        isDroneCI: env.isDroneCI,
        isBuddyCI: env.isBuddyCI,
        isBuildkite: env.isBuildkite,
        isCodeBuild: env.isCodeBuild,
        isVercel: env.isVercel,
        isNetlify: env.isNetlify,
        isHeroku: env.isHeroku,
        isSemaphore: env.isSemaphore,
        isCodefresh: env.isCodefresh,
        isWoodpecker: env.isWoodpecker,
        isHarness: env.isHarness,
        isRender: env.isRender,
        isRailway: env.isRailway,
        isFlyio: env.isFlyio,
        // New CI platforms
        isCodemagic: env.isCodemagic,
        isGitHubCodespaces: env.isGitHubCodespaces,
        isGoogleCloudBuild: env.isGoogleCloudBuild,
        isAlibabaCloud: env.isAlibabaCloud,
        isHuaweiCloud: env.isHuaweiCloud,
        isTencentCloud: env.isTencentCloud,
        isBaiduCloud: env.isBaiduCloud,
        isSourcegraph: env.isSourcegraph,
        isGitpod: env.isGitpod,
        isReplit: env.isReplit,
        isStackblitz: env.isStackblitz,
        isGlitch: env.isGlitch
      },
      containerEnvironment: {
        isDocker: env.isDocker,
        isPodman: env.isPodman,
        isLXC: env.isLXC,
        isContainerd: env.isContainerd,
        isCRIO: env.isCRIO,
        isKubernetes: env.isKubernetes,
        isDockerCompose: env.isDockerCompose,
        isDockerSwarm: env.isDockerSwarm,
        isContainerized: env.isContainerized,
        kubernetesDistributions: {
          isOpenShift: env.isOpenShift,
          isGKE: env.isGKE,
          isEKS: env.isEKS,
          isAKS: env.isAKS
        }
      },
      cloudEnvironment: {
        isAWS: env.isAWS,
        isAzure: env.isAzure,
        isGCP: env.isGCP,
        isOCI: env.isOCI,
        isIBMCloud: env.isIBMCloud,
        isDigitalOcean: env.isDigitalOcean,
        isLinode: env.isLinode,
        isVultr: env.isVultr,
        isCloudflare: env.isCloudflare,
        isCloudEnvironment: env.isCloudEnvironment,
        isServerless: env.isServerless,
        aws: {
          isLambda: env.isAWSLambda,
          isECS: env.isAWSECS,
          isFargate: env.isAWSFargate
        },
        azure: {
          isFunctions: env.isAzureFunctions,
          isAppService: env.isAzureAppService
        },
        gcp: {
          isCloudFunctions: env.isGCPCloudFunctions,
          isCloudRun: env.isGCPCloudRun
        }
      },
      nodeEnvironment: {
        nodeVersion: env.nodeVersion,
        architecture: env.architecture,
        isDevelopment: env.isDevelopment,
        isProduction: env.isProduction,
        isTest: env.isTest,
        isStaging: env.isStaging
      },
      paths: {
        workingDirectory: env.workingDir,
        tempDirectory: env.tmpDir,
        homeDirectory: env.homeDir
      }
    };

    // Include system info if requested
    if (includeSystemInfo) {
      reportObj.systemInfo = {
        hostname: env.hostname,
        username: env.username,
        memory: env.memory,
        cpus: env.cpus
      };
    }

    // Include environment variables if requested
    if (includeEnvVars) {
      reportObj.environmentVariables = process.env;
    } else {
      // Include only relevant environment variables
      reportObj.environmentVariables = {
        // Node Environment
        NODE_ENV: process.env.NODE_ENV || 'not set',

        // CI Environment
        CI: process.env.CI || 'not set',
        CI_ENVIRONMENT: process.env.CI_ENVIRONMENT || 'not set',
        CI_TYPE: process.env.CI_TYPE || 'not set',
        CI_PLATFORM: process.env.CI_PLATFORM || 'not set',
        CI_RUNNER_OS: process.env.CI_RUNNER_OS || 'not set',
        CI_WORKSPACE: process.env.CI_WORKSPACE || 'not set',

        // GitHub Actions
        GITHUB_ACTIONS: process.env.GITHUB_ACTIONS || 'not set',
        GITHUB_WORKFLOW: process.env.GITHUB_WORKFLOW || 'not set',
        GITHUB_RUN_ID: process.env.GITHUB_RUN_ID || 'not set',

        // Container Environment
        DOCKER_ENVIRONMENT: process.env.DOCKER_ENVIRONMENT || 'not set',
        DOCKER: process.env.DOCKER || 'not set',
        CONTAINER: process.env.CONTAINER || 'not set',
        CONTAINERIZED: process.env.CONTAINERIZED || 'not set',

        // Kubernetes
        KUBERNETES_SERVICE_HOST: process.env.KUBERNETES_SERVICE_HOST || 'not set',
        KUBERNETES_NAMESPACE: process.env.KUBERNETES_NAMESPACE || 'not set',
        K8S_NAMESPACE: process.env.K8S_NAMESPACE || 'not set',

        // Docker Compose
        COMPOSE_PROJECT_NAME: process.env.COMPOSE_PROJECT_NAME || 'not set',
        COMPOSE_FILE: process.env.COMPOSE_FILE || 'not set',

        // Docker Swarm
        DOCKER_SWARM: process.env.DOCKER_SWARM || 'not set',
        SWARM_NODE_ID: process.env.SWARM_NODE_ID || 'not set',

        // Cloud Providers
        AWS_REGION: process.env.AWS_REGION || 'not set',
        AWS_LAMBDA_FUNCTION_NAME: process.env.AWS_LAMBDA_FUNCTION_NAME || 'not set',
        AZURE_FUNCTIONS_ENVIRONMENT: process.env.AZURE_FUNCTIONS_ENVIRONMENT || 'not set',
        WEBSITE_SITE_NAME: process.env.WEBSITE_SITE_NAME || 'not set',
        GOOGLE_CLOUD_PROJECT: process.env.GOOGLE_CLOUD_PROJECT || 'not set',
        FUNCTION_NAME: process.env.FUNCTION_NAME || 'not set',

        // CI Platforms
        VERCEL: process.env.VERCEL || 'not set',
        NETLIFY: process.env.NETLIFY || 'not set',
        HEROKU_TEST_RUN_ID: process.env.HEROKU_TEST_RUN_ID || 'not set',
        SEMAPHORE: process.env.SEMAPHORE || 'not set',
        CF_BUILD_ID: process.env.CF_BUILD_ID || 'not set',
        CI_PIPELINE_ID: process.env.CI_PIPELINE_ID || 'not set',
        HARNESS_BUILD_ID: process.env.HARNESS_BUILD_ID || 'not set',
        RENDER: process.env.RENDER || 'not set',
        RAILWAY_ENVIRONMENT_ID: process.env.RAILWAY_ENVIRONMENT_ID || 'not set',
        FLY_APP_NAME: process.env.FLY_APP_NAME || 'not set'
      };
    }

    const jsonReport = JSON.stringify(reportObj, null, 2);

    // Write report to file if path is provided
    if (filePath) {
      try {
        const dir = path.dirname(filePath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        fs.writeFileSync(filePath, jsonReport);
      } catch (error) {
        console.error(`Failed to write environment report to ${filePath}: ${error.message}`);
      }
    }

    return jsonReport;
  }

  // Create text report content
  const report = `Environment Report
=================
Generated at: ${new Date().toISOString()}

Operating System:
- Platform: ${env.platform}
- Type: ${env.osType}
- Release: ${env.osRelease}
- Windows: ${env.isWindows ? 'Yes' : 'No'}
- macOS: ${env.isMacOS ? 'Yes' : 'No'}
- Linux: ${env.isLinux ? 'Yes' : 'No'}
- WSL: ${env.isWSL ? 'Yes' : 'No'}

CI Environment:
- CI: ${env.isCI ? 'Yes' : 'No'}
- GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}
- Jenkins: ${env.isJenkins ? 'Yes' : 'No'}
- GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}
- Circle CI: ${env.isCircleCI ? 'Yes' : 'No'}
- Travis CI: ${env.isTravis ? 'Yes' : 'No'}
- Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}
- TeamCity: ${env.isTeamCity ? 'Yes' : 'No'}
- Bitbucket: ${env.isBitbucket ? 'Yes' : 'No'}
- AppVeyor: ${env.isAppVeyor ? 'Yes' : 'No'}
- Drone CI: ${env.isDroneCI ? 'Yes' : 'No'}
- Buddy CI: ${env.isBuddyCI ? 'Yes' : 'No'}
- Buildkite: ${env.isBuildkite ? 'Yes' : 'No'}
- CodeBuild: ${env.isCodeBuild ? 'Yes' : 'No'}
- Vercel: ${env.isVercel ? 'Yes' : 'No'}
- Netlify: ${env.isNetlify ? 'Yes' : 'No'}
- Heroku: ${env.isHeroku ? 'Yes' : 'No'}
- Semaphore: ${env.isSemaphore ? 'Yes' : 'No'}
- Codefresh: ${env.isCodefresh ? 'Yes' : 'No'}
- Woodpecker: ${env.isWoodpecker ? 'Yes' : 'No'}
- Harness: ${env.isHarness ? 'Yes' : 'No'}
- Render: ${env.isRender ? 'Yes' : 'No'}
- Railway: ${env.isRailway ? 'Yes' : 'No'}
- Fly.io: ${env.isFlyio ? 'Yes' : 'No'}
- Codemagic: ${env.isCodemagic ? 'Yes' : 'No'}
- GitHub Codespaces: ${env.isGitHubCodespaces ? 'Yes' : 'No'}
- Google Cloud Build: ${env.isGoogleCloudBuild ? 'Yes' : 'No'}
- Alibaba Cloud: ${env.isAlibabaCloud ? 'Yes' : 'No'}
- Huawei Cloud: ${env.isHuaweiCloud ? 'Yes' : 'No'}
- Tencent Cloud: ${env.isTencentCloud ? 'Yes' : 'No'}
- Baidu Cloud: ${env.isBaiduCloud ? 'Yes' : 'No'}
- Sourcegraph: ${env.isSourcegraph ? 'Yes' : 'No'}
- Gitpod: ${env.isGitpod ? 'Yes' : 'No'}
- Replit: ${env.isReplit ? 'Yes' : 'No'}
- Stackblitz: ${env.isStackblitz ? 'Yes' : 'No'}
- Glitch: ${env.isGlitch ? 'Yes' : 'No'}

Container Environment:
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Podman: ${env.isPodman ? 'Yes' : 'No'}
- LXC/LXD: ${env.isLXC ? 'Yes' : 'No'}
- Containerd: ${env.isContainerd ? 'Yes' : 'No'}
- CRI-O: ${env.isCRIO ? 'Yes' : 'No'}
- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}
- Containerized: ${env.isContainerized ? 'Yes' : 'No'}

Kubernetes Distributions:
- OpenShift: ${env.isOpenShift ? 'Yes' : 'No'}
- GKE: ${env.isGKE ? 'Yes' : 'No'}
- EKS: ${env.isEKS ? 'Yes' : 'No'}
- AKS: ${env.isAKS ? 'Yes' : 'No'}

Cloud Environment:
- AWS: ${env.isAWS ? 'Yes' : 'No'}
- Azure: ${env.isAzure ? 'Yes' : 'No'}
- GCP: ${env.isGCP ? 'Yes' : 'No'}
- Oracle Cloud: ${env.isOCI ? 'Yes' : 'No'}
- IBM Cloud: ${env.isIBMCloud ? 'Yes' : 'No'}
- DigitalOcean: ${env.isDigitalOcean ? 'Yes' : 'No'}
- Linode: ${env.isLinode ? 'Yes' : 'No'}
- Vultr: ${env.isVultr ? 'Yes' : 'No'}
- Cloudflare: ${env.isCloudflare ? 'Yes' : 'No'}
- Cloud Environment: ${env.isCloudEnvironment ? 'Yes' : 'No'}
- Serverless: ${env.isServerless ? 'Yes' : 'No'}

AWS Services:
- Lambda: ${env.isAWSLambda ? 'Yes' : 'No'}
- ECS: ${env.isAWSECS ? 'Yes' : 'No'}
- Fargate: ${env.isAWSFargate ? 'Yes' : 'No'}

Azure Services:
- Functions: ${env.isAzureFunctions ? 'Yes' : 'No'}
- App Service: ${env.isAzureAppService ? 'Yes' : 'No'}

GCP Services:
- Cloud Functions: ${env.isGCPCloudFunctions ? 'Yes' : 'No'}
- Cloud Run: ${env.isGCPCloudRun ? 'Yes' : 'No'}

Node Environment:
- Node Version: ${env.nodeVersion}
- Architecture: ${env.architecture}
- Development: ${env.isDevelopment ? 'Yes' : 'No'}
- Production: ${env.isProduction ? 'Yes' : 'No'}
- Test: ${env.isTest ? 'Yes' : 'No'}
- Staging: ${env.isStaging ? 'Yes' : 'No'}

Paths:
- Working Directory: ${env.workingDir}
- Temp Directory: ${env.tmpDir}
- Home Directory: ${env.homeDir}
${includeSystemInfo ? `
System Information:
- Hostname: ${env.hostname}
- Username: ${env.username}
- Memory Total: ${formatBytes(env.memory.total)}
- Memory Free: ${formatBytes(env.memory.free)}
- CPUs: ${env.cpus.length}
` : ''}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- CI: ${process.env.CI || 'not set'}
- CI_ENVIRONMENT: ${process.env.CI_ENVIRONMENT || 'not set'}
- CI_TYPE: ${process.env.CI_TYPE || 'not set'}
- GITHUB_ACTIONS: ${process.env.GITHUB_ACTIONS || 'not set'}
- DOCKER_ENVIRONMENT: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
- KUBERNETES_SERVICE_HOST: ${process.env.KUBERNETES_SERVICE_HOST || 'not set'}
- COMPOSE_PROJECT_NAME: ${process.env.COMPOSE_PROJECT_NAME || 'not set'}
- VERCEL: ${process.env.VERCEL || 'not set'}
- NETLIFY: ${process.env.NETLIFY || 'not set'}
- HEROKU_TEST_RUN_ID: ${process.env.HEROKU_TEST_RUN_ID || 'not set'}
- SEMAPHORE: ${process.env.SEMAPHORE || 'not set'}
- CF_BUILD_ID: ${process.env.CF_BUILD_ID || 'not set'}
- CI_PIPELINE_ID: ${process.env.CI_PIPELINE_ID || 'not set'}
- HARNESS_BUILD_ID: ${process.env.HARNESS_BUILD_ID || 'not set'}
- RENDER: ${process.env.RENDER || 'not set'}
- RAILWAY_ENVIRONMENT_ID: ${process.env.RAILWAY_ENVIRONMENT_ID || 'not set'}
- FLY_APP_NAME: ${process.env.FLY_APP_NAME || 'not set'}
${includeEnvVars ? formatEnvironmentVariables() : ''}
`;

  // Write report to file if path is provided
  if (filePath) {
    try {
      const dir = path.dirname(filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(filePath, report);
    } catch (error) {
      console.error(`Failed to write environment report to ${filePath}: ${error.message}`);
    }
  }

  return report;
}

/**
 * Format bytes to a human-readable string
 * @param {number} bytes - Bytes to format
 * @returns {string} Formatted string
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format environment variables for the report
 * @returns {string} Formatted environment variables
 */
function formatEnvironmentVariables() {
  let result = '\nAll Environment Variables:\n';

  // Get all environment variables and sort them
  const envVars = Object.keys(process.env).sort();

  // Format each variable
  for (const key of envVars) {
    // Skip sensitive variables
    if (key.includes('KEY') || key.includes('SECRET') || key.includes('TOKEN') || key.includes('PASSWORD')) {
      result += `- ${key}: [REDACTED]\n`;
    } else {
      result += `- ${key}: ${process.env[key]}\n`;
    }
  }

  return result;
}

/**
 * Safely create a directory with error handling
 * @param {string} dirPath - Directory path to create
 * @returns {boolean} True if successful, false otherwise
 */
function safelyCreateDirectory(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      return true;
    }
    return true;
  } catch (error) {
    console.error(`Failed to create directory at ${dirPath}: ${error.message}`);
    return false;
  }
}

/**
 * Safely write a file with error handling
 * @param {string} filePath - File path to write to
 * @param {string} content - Content to write
 * @returns {boolean} True if successful, false otherwise
 */
function safelyWriteFile(filePath, content) {
  try {
    const dir = path.dirname(filePath);
    safelyCreateDirectory(dir);
    fs.writeFileSync(filePath, content);
    return true;
  } catch (error) {
    console.error(`Failed to write file at ${filePath}: ${error.message}`);
    return false;
  }
}

module.exports = {
  detectEnvironment,
  createEnvironmentReport,
  safeFileExists,
  safeReadFile,
  safelyCreateDirectory,
  safelyWriteFile
};
