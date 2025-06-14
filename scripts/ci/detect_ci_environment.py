#!/usr/bin/env python3
"""
CI Environment Detection Script.

This script detects the current CI environment and outputs detailed information about it.
It supports a wide range of CI platforms including:
- GitHub Actions
- Jenkins
- GitLab CI
- CircleCI
- Travis CI
- Azure Pipelines
- TeamCity
- Bitbucket Pipelines
- AppVeyor
- Drone CI
- Buddy
- Buildkite
- AWS CodeBuild
- Vercel
- Netlify
- Heroku CI
- Semaphore
- Codefresh
- Woodpecker
- Harness
- Render
- Railway
- Fly.io
- Codemagic
- GitHub Codespaces
- Google Cloud Build
- Alibaba Cloud DevOps
- Huawei Cloud DevCloud
- Tencent Cloud CODING
- Baidu Cloud CICD
- Sourcegraph
- Gitpod
- Replit
- Stackblitz
- Glitch

It also detects container environments:
- Docker
- Podman
- LXC/LXD
- Containerd
- CRI-O
- Docker Compose
- Docker Swarm
- Kubernetes

And cloud environments:
- AWS
- Azure
- GCP
- Oracle Cloud (OCI)
- IBM Cloud
- DigitalOcean
- Linode
- Vultr
- Cloudflare
- Serverless (Lambda, Azure Functions, Cloud Functions)

Usage:
    python detect_ci_environment.py [--json] [--verbose]

Options:
    --json      Output in JSON format
    --verbose   Include verbose output.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import sys
from pathlib import Path
from typing import Any


def safe_file_exists(file_path: str) -> bool:
    """
    Safely check if a file exists without raising exceptions.

    Args:
        file_path: Path to the file to check

    Returns:
        bool: True if the file exists, False otherwise

    """
    try:
        return Path(file_path).exists()
    except OSError:
        return False


def safe_read_file(file_path: str) -> str | None:
    """
    Safely read a file without raising exceptions.

    Args:
        file_path: Path to the file to read

    Returns:
        str: File contents or None if the file doesn't exist or can't be read

    """
    try:
        if safe_file_exists(file_path):
<<<<<<< HEAD
            with Path(file_path).open(encoding="utf-8") as f:
=======
            with open(file_path, encoding="utf-8") as f:
>>>>>>> origin/main
                return f.read()
        else:
            return None
    except (OSError, UnicodeDecodeError):
        return None


def detect_ci_environment() -> dict[str, Any]:  # noqa: C901, PLR0912, PLR0915
    """
    Detect the current CI environment.

    Returns:
        Dict[str, Any]: Dictionary with CI environment information

    """
    # Operating System Detection
    os_info = {
        "platform": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "is_windows": platform.system() == "Windows",
        "is_macos": platform.system() == "Darwin",
        "is_linux": platform.system() == "Linux",
    }

    # WSL Detection
    is_wsl = False
    if os_info["is_linux"]:
        is_wsl = (
            os.environ.get("WSL_DISTRO_NAME") is not None
            or os.environ.get("WSLENV") is not None
            or (
                safe_file_exists("/proc/version")
                and safe_read_file("/proc/version") is not None
                and "microsoft" in (safe_read_file("/proc/version") or "").lower()
            )
            or "microsoft" in platform.release().lower()
        )
    os_info["is_wsl"] = is_wsl

    # CI Environment Detection
    ci_info = {
        "is_ci": (
            os.environ.get("CI") == "true"
            or os.environ.get("CI") == "1"
            or os.environ.get("GITHUB_ACTIONS") == "true"
            or os.environ.get("GITHUB_WORKFLOW") is not None
            or os.environ.get("JENKINS_URL") is not None
            or os.environ.get("GITLAB_CI") is not None
            or os.environ.get("CIRCLECI") is not None
            or os.environ.get("TRAVIS") is not None
            or os.environ.get("TF_BUILD") is not None
            or os.environ.get("TEAMCITY_VERSION") is not None
            or os.environ.get("BITBUCKET_COMMIT") is not None
            or os.environ.get("BITBUCKET_BUILD_NUMBER") is not None
            or os.environ.get("APPVEYOR") is not None
            or os.environ.get("DRONE") is not None
            or os.environ.get("BUDDY") is not None
            or os.environ.get("BUDDY_WORKSPACE_ID") is not None
            or os.environ.get("BUILDKITE") is not None
            or os.environ.get("CODEBUILD_BUILD_ID") is not None
            or os.environ.get("VERCEL") is not None
            or os.environ.get("NOW_BUILDER") is not None
            or os.environ.get("NETLIFY") is not None
            or os.environ.get("HEROKU_TEST_RUN_ID") is not None
            or os.environ.get("SEMAPHORE") is not None
            or os.environ.get("SEMAPHORE_WORKFLOW_ID") is not None
            or os.environ.get("CF_BUILD_ID") is not None
            or (
                os.environ.get("CI_PIPELINE_ID") is not None
                and os.environ.get("CI_REPO") is not None
            )
            or os.environ.get("HARNESS_BUILD_ID") is not None
            or os.environ.get("RENDER") is not None
            or os.environ.get("RAILWAY_ENVIRONMENT_ID") is not None
            or os.environ.get("FLY_APP_NAME") is not None
            # New CI platforms
            or os.environ.get("CM_BUILD_ID") is not None
            or os.environ.get("CODEMAGIC_ID") is not None
            or os.environ.get("CODESPACE_NAME") is not None
            or os.environ.get("GITHUB_CODESPACE_NAME") is not None
            or os.environ.get("CLOUD_BUILD") is not None
            or os.environ.get("CLOUD_BUILD_ID") is not None
            or os.environ.get("ALIBABA_CLOUD") is not None
            or os.environ.get("ALICLOUD_ACCOUNT_ID") is not None
            or os.environ.get("DEVCLOUD_PIPELINE_ID") is not None
            or os.environ.get("HUAWEICLOUD_PIPELINE") is not None
            or os.environ.get("CODING_PIPELINE_ID") is not None
            or os.environ.get("TENCENT_CLOUD_CI") is not None
            or os.environ.get("BAIDU_CLOUD_CI") is not None
            or os.environ.get("BAIDU_PIPELINE_ID") is not None
            or os.environ.get("SOURCEGRAPH_EXECUTOR") is not None
            or os.environ.get("SRC_EXECUTOR_NAME") is not None
            or os.environ.get("GITPOD_WORKSPACE_ID") is not None
            or os.environ.get("GITPOD_WORKSPACE_URL") is not None
            or os.environ.get("REPL_ID") is not None
            or os.environ.get("REPL_OWNER") is not None
            or os.environ.get("STACKBLITZ_ENV") is not None
            or os.environ.get("STACKBLITZ_PROJECT_ID") is not None
            or os.environ.get("GLITCH_EDITOR_URL") is not None
            or os.environ.get("GLITCH_PROJECT_ID") is not None
        ),
        "ci_type": "unknown",
        "ci_platform": "unknown",
        "ci_environment_variables": {},
    }

    # Specific CI Platform Detection
    if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("GITHUB_WORKFLOW"):
        ci_info["ci_type"] = "github"
        ci_info["ci_platform"] = "GitHub Actions"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("GITHUB_")
        }
    elif os.environ.get("JENKINS_URL"):
        ci_info["ci_type"] = "jenkins"
        ci_info["ci_platform"] = "Jenkins"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("JENKINS_", "BUILD_"))
        }
    elif os.environ.get("GITLAB_CI"):
        ci_info["ci_type"] = "gitlab"
        ci_info["ci_platform"] = "GitLab CI"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("CI_", "GITLAB_"))
        }
    elif os.environ.get("CIRCLECI"):
        ci_info["ci_type"] = "circle"
        ci_info["ci_platform"] = "CircleCI"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("CIRCLE_")
        }
    elif os.environ.get("TRAVIS"):
        ci_info["ci_type"] = "travis"
        ci_info["ci_platform"] = "Travis CI"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("TRAVIS_")
        }
    elif os.environ.get("TF_BUILD"):
        ci_info["ci_type"] = "azure"
        ci_info["ci_platform"] = "Azure Pipelines"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("AGENT_", "BUILD_", "SYSTEM_"))
        }
    elif os.environ.get("TEAMCITY_VERSION"):
        ci_info["ci_type"] = "teamcity"
        ci_info["ci_platform"] = "TeamCity"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("TEAMCITY_")
        }
    elif os.environ.get("BITBUCKET_COMMIT") or os.environ.get("BITBUCKET_BUILD_NUMBER"):
        ci_info["ci_type"] = "bitbucket"
        ci_info["ci_platform"] = "Bitbucket Pipelines"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("BITBUCKET_")
        }
    elif os.environ.get("APPVEYOR"):
        ci_info["ci_type"] = "appveyor"
        ci_info["ci_platform"] = "AppVeyor"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("APPVEYOR_")
        }
    elif os.environ.get("DRONE"):
        ci_info["ci_type"] = "drone"
        ci_info["ci_platform"] = "Drone CI"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("DRONE_")
        }
    elif os.environ.get("BUDDY") or os.environ.get("BUDDY_WORKSPACE_ID"):
        ci_info["ci_type"] = "buddy"
        ci_info["ci_platform"] = "Buddy"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("BUDDY_")
        }
    elif os.environ.get("BUILDKITE"):
        ci_info["ci_type"] = "buildkite"
        ci_info["ci_platform"] = "Buildkite"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("BUILDKITE_")
        }
    elif os.environ.get("CODEBUILD_BUILD_ID"):
        ci_info["ci_type"] = "codebuild"
        ci_info["ci_platform"] = "AWS CodeBuild"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("CODEBUILD_")
        }
    elif os.environ.get("VERCEL") or os.environ.get("NOW_BUILDER"):
        ci_info["ci_type"] = "vercel"
        ci_info["ci_platform"] = "Vercel"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("VERCEL_", "NOW_"))
        }
    elif os.environ.get("NETLIFY"):
        ci_info["ci_type"] = "netlify"
        ci_info["ci_platform"] = "Netlify"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("NETLIFY_")
        }
    elif os.environ.get("HEROKU_TEST_RUN_ID"):
        ci_info["ci_type"] = "heroku"
        ci_info["ci_platform"] = "Heroku CI"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("HEROKU_")
        }
    elif os.environ.get("SEMAPHORE") or os.environ.get("SEMAPHORE_WORKFLOW_ID"):
        ci_info["ci_type"] = "semaphore"
        ci_info["ci_platform"] = "Semaphore"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("SEMAPHORE_")
        }
    elif os.environ.get("CF_BUILD_ID"):
        ci_info["ci_type"] = "codefresh"
        ci_info["ci_platform"] = "Codefresh"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("CF_")
        }
    elif os.environ.get("CI_PIPELINE_ID") and os.environ.get("CI_REPO"):
        ci_info["ci_type"] = "woodpecker"
        ci_info["ci_platform"] = "Woodpecker CI"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("CI_")
        }
    elif os.environ.get("HARNESS_BUILD_ID"):
        ci_info["ci_type"] = "harness"
        ci_info["ci_platform"] = "Harness CI"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("HARNESS_")
        }
    elif os.environ.get("RENDER"):
        ci_info["ci_type"] = "render"
        ci_info["ci_platform"] = "Render"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("RENDER_")
        }
    elif os.environ.get("RAILWAY_ENVIRONMENT_ID"):
        ci_info["ci_type"] = "railway"
        ci_info["ci_platform"] = "Railway"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("RAILWAY_")
        }
    elif os.environ.get("FLY_APP_NAME"):
        ci_info["ci_type"] = "flyio"
        ci_info["ci_platform"] = "Fly.io"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("FLY_")
        }
    # New CI platforms
    elif os.environ.get("CM_BUILD_ID") or os.environ.get("CODEMAGIC_ID"):
        ci_info["ci_type"] = "codemagic"
        ci_info["ci_platform"] = "Codemagic"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("CM_", "CODEMAGIC_"))
        }
    elif os.environ.get("CODESPACE_NAME") or os.environ.get("GITHUB_CODESPACE_NAME"):
        ci_info["ci_type"] = "github-codespaces"
        ci_info["ci_platform"] = "GitHub Codespaces"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("CODESPACE_", "GITHUB_CODESPACE_"))
        }
    elif os.environ.get("CLOUD_BUILD") or os.environ.get("CLOUD_BUILD_ID"):
        ci_info["ci_type"] = "google-cloud-build"
        ci_info["ci_platform"] = "Google Cloud Build"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("CLOUD_BUILD_") or key == "CLOUD_BUILD"
        }
    elif os.environ.get("ALIBABA_CLOUD") or os.environ.get("ALICLOUD_ACCOUNT_ID"):
        ci_info["ci_type"] = "alibaba-cloud"
        ci_info["ci_platform"] = "Alibaba Cloud DevOps"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("ALIBABA_", "ALICLOUD_"))
        }
    elif os.environ.get("DEVCLOUD_PIPELINE_ID") or os.environ.get(
        "HUAWEICLOUD_PIPELINE"
    ):
        ci_info["ci_type"] = "huawei-cloud"
        ci_info["ci_platform"] = "Huawei Cloud DevCloud"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("DEVCLOUD_", "HUAWEICLOUD_"))
        }
    elif os.environ.get("CODING_PIPELINE_ID") or os.environ.get("TENCENT_CLOUD_CI"):
        ci_info["ci_type"] = "tencent-cloud"
        ci_info["ci_platform"] = "Tencent Cloud CODING"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("CODING_", "TENCENT_"))
        }
    elif os.environ.get("BAIDU_CLOUD_CI") or os.environ.get("BAIDU_PIPELINE_ID"):
        ci_info["ci_type"] = "baidu-cloud"
        ci_info["ci_platform"] = "Baidu Cloud CICD"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("BAIDU_")
        }
    elif os.environ.get("SOURCEGRAPH_EXECUTOR") or os.environ.get("SRC_EXECUTOR_NAME"):
        ci_info["ci_type"] = "sourcegraph"
        ci_info["ci_platform"] = "Sourcegraph"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("SOURCEGRAPH_", "SRC_"))
        }
    elif os.environ.get("GITPOD_WORKSPACE_ID") or os.environ.get(
        "GITPOD_WORKSPACE_URL"
    ):
        ci_info["ci_type"] = "gitpod"
        ci_info["ci_platform"] = "Gitpod"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("GITPOD_")
        }
    elif os.environ.get("REPL_ID") or os.environ.get("REPL_OWNER"):
        ci_info["ci_type"] = "replit"
        ci_info["ci_platform"] = "Replit"
        ci_info["ci_environment_variables"] = {
            key: value for key, value in os.environ.items() if key.startswith("REPL_")
        }
    elif os.environ.get("STACKBLITZ_ENV") or os.environ.get("STACKBLITZ_PROJECT_ID"):
        ci_info["ci_type"] = "stackblitz"
        ci_info["ci_platform"] = "Stackblitz"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("STACKBLITZ_")
        }
    elif os.environ.get("GLITCH_EDITOR_URL") or os.environ.get("GLITCH_PROJECT_ID"):
        ci_info["ci_type"] = "glitch"
        ci_info["ci_platform"] = "Glitch"
        ci_info["ci_environment_variables"] = {
            key: value
            for key, value in os.environ.items()
            if key.startswith(("GLITCH_", "PROJECT_"))
        }
    elif ci_info["is_ci"]:
        ci_info["ci_type"] = "generic"
        ci_info["ci_platform"] = "Generic CI"

    # Container Environment Detection
    container_info = {
        "is_docker": False,
        "is_podman": False,
        "is_lxc": False,
        "is_containerd": False,
        "is_crio": False,
        "is_kubernetes": False,
        "is_docker_compose": False,
        "is_docker_swarm": False,
        "is_rkt": False,
        "is_singularity": False,
        "is_containerized": False,
        "detection_method": "none",
    }

    # Docker detection with multiple methods
    if (
        os.environ.get("DOCKER_ENVIRONMENT") == "true"
        or os.environ.get("DOCKER") == "true"
        or safe_file_exists("/.dockerenv")
        or safe_file_exists("/run/.containerenv")
        or (
            safe_file_exists("/proc/1/cgroup")
            and safe_read_file("/proc/1/cgroup") is not None
            and "docker" in (safe_read_file("/proc/1/cgroup") or "").lower()
        )
    ):
        container_info["is_docker"] = True
        container_info["is_containerized"] = True

        # Determine detection method
        if safe_file_exists("/.dockerenv"):
            container_info["detection_method"] = ".dockerenv file"
        elif safe_file_exists("/run/.containerenv"):
            container_info["detection_method"] = ".containerenv file"
        elif (
            safe_file_exists("/proc/1/cgroup")
            and safe_read_file("/proc/1/cgroup") is not None
            and "docker" in (safe_read_file("/proc/1/cgroup") or "").lower()
        ):
            container_info["detection_method"] = "cgroup file"
        else:
            container_info["detection_method"] = "environment variable"

    # Kubernetes detection
    if (
        os.environ.get("KUBERNETES_SERVICE_HOST")
        or os.environ.get("KUBERNETES_PORT")
        or safe_file_exists("/var/run/secrets/kubernetes.io")
    ):
        container_info["is_kubernetes"] = True
        container_info["is_containerized"] = True

    # Docker Compose detection
    if (
        os.environ.get("COMPOSE_PROJECT_NAME")
        or os.environ.get("COMPOSE_FILE")
        or os.environ.get("COMPOSE_PATH_SEPARATOR")
    ):
        container_info["is_docker_compose"] = True
        container_info["is_containerized"] = True

    # Docker Swarm detection
    if (
        os.environ.get("DOCKER_SWARM")
        or os.environ.get("SWARM_NODE_ID")
        or os.environ.get("SWARM_MANAGER")
    ):
        container_info["is_docker_swarm"] = True
        container_info["is_containerized"] = True

    # Podman detection
    if (
        os.environ.get("PODMAN_ENVIRONMENT") == "true"
        or os.environ.get("PODMAN") == "true"
        or (
            safe_file_exists("/proc/1/cgroup")
            and safe_read_file("/proc/1/cgroup") is not None
            and "podman" in (safe_read_file("/proc/1/cgroup") or "").lower()
        )
    ):
        container_info["is_podman"] = True
        container_info["is_containerized"] = True

    # LXC/LXD detection
    if (
        os.environ.get("LXC_ENVIRONMENT") == "true"
        or os.environ.get("LXC") == "true"
        or os.environ.get("LXD") == "true"
        or safe_file_exists("/dev/.lxc")
        or safe_file_exists("/dev/.lxd")
        or (
            safe_file_exists("/proc/1/cgroup")
            and safe_read_file("/proc/1/cgroup") is not None
            and "lxc" in (safe_read_file("/proc/1/cgroup") or "").lower()
        )
    ):
        container_info["is_lxc"] = True
        container_info["is_containerized"] = True

    # Containerd detection
    if (
        os.environ.get("CONTAINERD_ENVIRONMENT") == "true"
        or os.environ.get("CONTAINERD") == "true"
        or (
            safe_file_exists("/proc/1/cgroup")
            and safe_read_file("/proc/1/cgroup") is not None
            and "containerd" in (safe_read_file("/proc/1/cgroup") or "").lower()
        )
    ):
        container_info["is_containerd"] = True
        container_info["is_containerized"] = True

    # CRI-O detection
    if (
        os.environ.get("CRIO_ENVIRONMENT") == "true"
        or os.environ.get("CRIO") == "true"
        or (
            safe_file_exists("/proc/1/cgroup")
            and safe_read_file("/proc/1/cgroup") is not None
            and "crio" in (safe_read_file("/proc/1/cgroup") or "").lower()
        )
    ):
        container_info["is_crio"] = True
        container_info["is_containerized"] = True

    # rkt detection
    if (
        os.environ.get("RKT_ENVIRONMENT") == "true"
        or os.environ.get("RKT") == "true"
        or (
            safe_file_exists("/proc/1/cgroup")
            and safe_read_file("/proc/1/cgroup") is not None
            and "rkt" in (safe_read_file("/proc/1/cgroup") or "").lower()
        )
        or safe_file_exists("/var/lib/rkt")
    ):
        container_info["is_rkt"] = True
        container_info["is_containerized"] = True

    # Singularity detection
    if (
        os.environ.get("SINGULARITY_ENVIRONMENT") == "true"
        or os.environ.get("SINGULARITY") == "true"
        or os.environ.get("SINGULARITY_CONTAINER") is not None
        or safe_file_exists("/.singularity.d")
        or safe_file_exists("/singularity")
    ):
        container_info["is_singularity"] = True
        container_info["is_containerized"] = True

    # Cloud Environment Detection
    cloud_info = {
        "is_aws": False,
        "is_azure": False,
        "is_gcp": False,
        "is_oci": False,
        "is_ibm_cloud": False,
        "is_digitalocean": False,
        "is_linode": False,
        "is_vultr": False,
        "is_cloudflare": False,
        "is_alibaba_cloud": False,
        "is_tencent_cloud": False,
        "is_huawei_cloud": False,
        "is_cloud": False,
        "is_lambda": False,
        "is_azure_functions": False,
        "is_cloud_functions": False,
        "is_serverless": False,
    }

    # AWS detection
    if (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        or os.environ.get("AWS_EXECUTION_ENV")
    ):
        cloud_info["is_aws"] = True
        cloud_info["is_cloud"] = True

        # AWS Lambda detection
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            cloud_info["is_lambda"] = True
            cloud_info["is_serverless"] = True

    # Azure detection
    if (
        os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT")
        or os.environ.get("WEBSITE_SITE_NAME")
        or os.environ.get("APPSETTING_WEBSITE_SITE_NAME")
    ):
        cloud_info["is_azure"] = True
        cloud_info["is_cloud"] = True

        # Azure Functions detection
        if os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT"):
            cloud_info["is_azure_functions"] = True
            cloud_info["is_serverless"] = True

    # GCP detection
    if (
        os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("GCLOUD_PROJECT")
        or os.environ.get("GCP_PROJECT")
        or (os.environ.get("FUNCTION_NAME") and os.environ.get("FUNCTION_REGION"))
    ):
        cloud_info["is_gcp"] = True
        cloud_info["is_cloud"] = True

        # Cloud Functions detection
        if os.environ.get("FUNCTION_NAME") and os.environ.get("FUNCTION_REGION"):
            cloud_info["is_cloud_functions"] = True
            cloud_info["is_serverless"] = True

    # Oracle Cloud Infrastructure (OCI) detection
    if (
        os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION")
        or os.environ.get("OCI_COMPARTMENT_ID")
        or os.environ.get("OCI_REGION")
        or os.environ.get("OCI_TENANT_ID")
    ):
        cloud_info["is_oci"] = True
        cloud_info["is_cloud"] = True

    # IBM Cloud detection
    if (
        os.environ.get("BLUEMIX_REGION")
        or os.environ.get("BLUEMIX_API_KEY")
        or os.environ.get("IBM_CLOUD_API_KEY")
        or os.environ.get("VCAP_SERVICES")
    ):
        cloud_info["is_ibm_cloud"] = True
        cloud_info["is_cloud"] = True

    # DigitalOcean detection
    if (
        os.environ.get("DIGITALOCEAN_ACCESS_TOKEN")
        or os.environ.get("DIGITALOCEAN_REGION")
        or os.environ.get("DIGITALOCEAN_DROPLET_ID")
    ):
        cloud_info["is_digitalocean"] = True
        cloud_info["is_cloud"] = True

    # Linode detection
    if (
        os.environ.get("LINODE_API_TOKEN")
        or os.environ.get("LINODE_REGION")
        or os.environ.get("LINODE_INSTANCE_ID")
    ):
        cloud_info["is_linode"] = True
        cloud_info["is_cloud"] = True

    # Vultr detection
    if (
        os.environ.get("VULTR_API_KEY")
        or os.environ.get("VULTR_REGION")
        or os.environ.get("VULTR_INSTANCE_ID")
    ):
        cloud_info["is_vultr"] = True
        cloud_info["is_cloud"] = True

    # Cloudflare detection
    if (
        os.environ.get("CLOUDFLARE_API_TOKEN")
        or os.environ.get("CLOUDFLARE_ZONE_ID")
        or os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        or os.environ.get("CF_PAGES")
    ):
        cloud_info["is_cloudflare"] = True
        cloud_info["is_cloud"] = True

    # Alibaba Cloud detection
    if (
        os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
        or os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        or os.environ.get("ALICLOUD_ACCESS_KEY")
        or os.environ.get("ALICLOUD_SECRET_KEY")
        or os.environ.get("ALICLOUD_REGION")
    ):
        cloud_info["is_alibaba_cloud"] = True
        cloud_info["is_cloud"] = True

    # Tencent Cloud detection
    if (
        os.environ.get("TENCENTCLOUD_SECRET_ID")
        or os.environ.get("TENCENTCLOUD_SECRET_KEY")
        or os.environ.get("TENCENTCLOUD_REGION")
    ):
        cloud_info["is_tencent_cloud"] = True
        cloud_info["is_cloud"] = True

    # Huawei Cloud detection
    if (
        os.environ.get("HUAWEICLOUD_ACCESS_KEY")
        or os.environ.get("HUAWEICLOUD_SECRET_KEY")
        or os.environ.get("HUAWEICLOUD_REGION")
    ):
        cloud_info["is_huawei_cloud"] = True
        cloud_info["is_cloud"] = True

    return {
        "os": os_info,
        "ci": ci_info,
        "container": container_info,
        "cloud": cloud_info,
    }


def create_ci_directories() -> list[dict[str, Any]]:
    """
    Create CI-specific directories.

    Returns:
        List[Dict[str, Any]]: List of created directories with status

    """
    directories = [
        "ci-reports",
        "ci-artifacts",
        "ci-logs",
        "ci-temp",
        "ci-cache",
    ]

    results = []
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            results.append({"directory": directory, "created": True, "error": None})
        except (OSError, PermissionError) as e:  # noqa: PERF203
            results.append({"directory": directory, "created": False, "error": str(e)})

    return results


def main() -> int:  # noqa: PLR0915
    """
    Run the CI environment detection script.

    Returns:
        int: Exit code

    """
    parser = argparse.ArgumentParser(description="CI Environment Detection Script")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", action="store_true", help="Include verbose output")
    parser.add_argument(
        "--create-dirs", action="store_true", help="Create CI directories"
    )
    args = parser.parse_args()

    # Detect CI environment
    env_info = detect_ci_environment()

    # Create CI directories if requested
    if args.create_dirs:
        env_info["ci_directories"] = create_ci_directories()

    # Add system information if verbose
    if args.verbose:
        env_info["system"] = {
            "hostname": socket.gethostname(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_compiler": platform.python_compiler(),
            "python_build": platform.python_build(),
            "python_executable": sys.executable,
        }

    # Output in JSON format if requested
    if args.json:
        print(json.dumps(env_info, indent=2))
    else:
        print("\n=== CI Environment Detection ===\n")

        # OS Information
        print("OS Information:")
        print(f"  Platform: {env_info['os']['platform']}")
        print(f"  Release: {env_info['os']['release']}")
        print(f"  Machine: {env_info['os']['machine']}")
        print(f"  Windows: {env_info['os']['is_windows']}")
        print(f"  macOS: {env_info['os']['is_macos']}")
        print(f"  Linux: {env_info['os']['is_linux']}")
        print(f"  WSL: {env_info['os']['is_wsl']}")

        # CI Information
        print("\nCI Information:")
        print(f"  CI Environment: {env_info['ci']['is_ci']}")
        print(f"  CI Platform: {env_info['ci']['ci_platform']}")
        print(f"  CI Type: {env_info['ci']['ci_type']}")

        # Container Information
        print("\nContainer Information:")
        print(f"  Containerized: {env_info['container']['is_containerized']}")
        print(f"  Docker: {env_info['container']['is_docker']}")
        print(f"  Kubernetes: {env_info['container']['is_kubernetes']}")
        print(f"  Docker Compose: {env_info['container']['is_docker_compose']}")
        print(f"  Docker Swarm: {env_info['container']['is_docker_swarm']}")
        print(f"  Podman: {env_info['container']['is_podman']}")
        print(f"  LXC/LXD: {env_info['container']['is_lxc']}")
        print(f"  Containerd: {env_info['container']['is_containerd']}")
        print(f"  CRI-O: {env_info['container']['is_crio']}")
        print(f"  rkt: {env_info['container']['is_rkt']}")
        print(f"  Singularity: {env_info['container']['is_singularity']}")

        # Cloud Information
        print("\nCloud Information:")
        print(f"  Cloud Environment: {env_info['cloud']['is_cloud']}")
        print(f"  AWS: {env_info['cloud']['is_aws']}")
        print(f"  Azure: {env_info['cloud']['is_azure']}")
        print(f"  GCP: {env_info['cloud']['is_gcp']}")
        print(f"  Oracle Cloud: {env_info['cloud']['is_oci']}")
        print(f"  IBM Cloud: {env_info['cloud']['is_ibm_cloud']}")
        print(f"  Alibaba Cloud: {env_info['cloud']['is_alibaba_cloud']}")
        print(f"  Tencent Cloud: {env_info['cloud']['is_tencent_cloud']}")
        print(f"  Huawei Cloud: {env_info['cloud']['is_huawei_cloud']}")
        print(f"  DigitalOcean: {env_info['cloud']['is_digitalocean']}")
        print(f"  Linode: {env_info['cloud']['is_linode']}")
        print(f"  Vultr: {env_info['cloud']['is_vultr']}")
        print(f"  Cloudflare: {env_info['cloud']['is_cloudflare']}")
        print(f"  Serverless: {env_info['cloud']['is_serverless']}")
        print(f"  Lambda: {env_info['cloud']['is_lambda']}")
        print(f"  Azure Functions: {env_info['cloud']['is_azure_functions']}")
        print(f"  Cloud Functions: {env_info['cloud']['is_cloud_functions']}")

        # CI Directories
        if args.create_dirs and "ci_directories" in env_info:
            print("\nCI Directories:")
            for directory in env_info["ci_directories"]:
                status = (
                    "✅ Created"
                    if directory["created"]
                    else f"❌ Failed: {directory['error']}"
                )
                print(f"  {directory['directory']}: {status}")

        # System Information (if verbose)
        if args.verbose and "system" in env_info:
            print("\nSystem Information:")
            print(f"  Hostname: {env_info['system']['hostname']}")
            print(f"  Python Version: {env_info['system']['python_version']}")
            print(
                f"  Python Implementation: {env_info['system']['python_implementation']}"
            )
            print(f"  Python Executable: {env_info['system']['python_executable']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
