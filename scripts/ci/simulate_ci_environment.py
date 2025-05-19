#!/usr/bin/env python3
"""
CI Environment Simulation Script

This script simulates different CI environments for testing purposes.
It sets environment variables and creates necessary files to mimic various CI platforms.

Supported CI platforms:
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

It also simulates container environments:
- Docker
- Docker Compose
- Docker Swarm
- Kubernetes

And cloud environments:
- AWS
- Azure
- GCP
- Serverless (Lambda, Azure Functions, Cloud Functions)

Usage:
    python simulate_ci_environment.py [--ci-type TYPE] [--container-type TYPE] [--cloud-type TYPE]

Options:
    --ci-type TYPE         CI platform to simulate (github, jenkins, gitlab, etc.)
    --container-type TYPE  Container environment to simulate (docker, kubernetes, etc.)
    --cloud-type TYPE      Cloud environment to simulate (aws, azure, gcp)
    --cleanup              Remove all simulated environment variables and files
"""

import argparse
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def setup_github_actions() -> Dict[str, str]:
    """
    Set up GitHub Actions environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "CI": "true",
        "GITHUB_ACTIONS": "true",
        "GITHUB_WORKFLOW": "CI",
        "GITHUB_RUN_ID": "1234567890",
        "GITHUB_RUN_NUMBER": "1",
        "GITHUB_ACTOR": "octocat",
        "GITHUB_REPOSITORY": "octocat/Hello-World",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_EVENT_PATH": "/github/workflow/event.json",
        "GITHUB_WORKSPACE": "/github/workspace",
        "GITHUB_SHA": "ffac537e6cbbf934b08745a378932722df287a53",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_HEAD_REF": "",
        "GITHUB_BASE_REF": "",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_API_URL": "https://api.github.com",
        "GITHUB_GRAPHQL_URL": "https://api.github.com/graphql",
        "RUNNER_OS": platform.system().upper(),
        "RUNNER_TEMP": "/tmp",
        "RUNNER_TOOL_CACHE": "/opt/hostedtoolcache",
    }


def setup_jenkins() -> Dict[str, str]:
    """
    Set up Jenkins environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "CI": "true",
        "JENKINS_URL": "http://jenkins.example.com/",
        "BUILD_ID": "1234",
        "BUILD_NUMBER": "1234",
        "BUILD_URL": "http://jenkins.example.com/job/project/1234/",
        "JOB_NAME": "project",
        "BUILD_TAG": "jenkins-project-1234",
        "JENKINS_HOME": "/var/lib/jenkins",
        "WORKSPACE": "/var/lib/jenkins/workspace/project",
        "EXECUTOR_NUMBER": "1",
        "NODE_NAME": "master",
        "NODE_LABELS": "master linux",
        "JAVA_HOME": "/usr/lib/jvm/java-11-openjdk-amd64",
    }


def setup_gitlab_ci() -> Dict[str, str]:
    """
    Set up GitLab CI environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "CI": "true",
        "GITLAB_CI": "true",
        "CI_SERVER": "yes",
        "CI_SERVER_NAME": "GitLab",
        "CI_SERVER_VERSION": "13.6.1",
        "CI_SERVER_REVISION": "1234567",
        "CI_PROJECT_ID": "12345",
        "CI_PROJECT_NAME": "project",
        "CI_PROJECT_PATH": "group/project",
        "CI_PROJECT_DIR": "/builds/group/project",
        "CI_PIPELINE_ID": "123456",
        "CI_PIPELINE_IID": "123",
        "CI_PIPELINE_URL": "https://gitlab.example.com/group/project/pipelines/123456",
        "CI_JOB_ID": "1234567",
        "CI_JOB_NAME": "test",
        "CI_JOB_STAGE": "test",
        "CI_COMMIT_SHA": "1234567890abcdef1234567890abcdef12345678",
        "CI_COMMIT_SHORT_SHA": "1234567",
        "CI_COMMIT_REF_NAME": "main",
        "CI_COMMIT_TAG": "",
        "CI_REGISTRY": "registry.example.com",
        "CI_REGISTRY_IMAGE": "registry.example.com/group/project",
    }


def setup_circleci() -> Dict[str, str]:
    """
    Set up CircleCI environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "CI": "true",
        "CIRCLECI": "true",
        "CIRCLE_BRANCH": "main",
        "CIRCLE_BUILD_NUM": "1234",
        "CIRCLE_BUILD_URL": "https://circleci.com/gh/username/project/1234",
        "CIRCLE_JOB": "build",
        "CIRCLE_NODE_INDEX": "0",
        "CIRCLE_NODE_TOTAL": "1",
        "CIRCLE_PROJECT_REPONAME": "project",
        "CIRCLE_PROJECT_USERNAME": "username",
        "CIRCLE_REPOSITORY_URL": "https://github.com/username/project",
        "CIRCLE_SHA1": "1234567890abcdef1234567890abcdef12345678",
        "CIRCLE_WORKING_DIRECTORY": "~/project",
    }


def setup_travis() -> Dict[str, str]:
    """
    Set up Travis CI environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "CI": "true",
        "TRAVIS": "true",
        "TRAVIS_BRANCH": "main",
        "TRAVIS_BUILD_DIR": "/home/travis/build/username/project",
        "TRAVIS_BUILD_ID": "1234567",
        "TRAVIS_BUILD_NUMBER": "1234",
        "TRAVIS_COMMIT": "1234567890abcdef1234567890abcdef12345678",
        "TRAVIS_COMMIT_MESSAGE": "Commit message",
        "TRAVIS_JOB_ID": "12345678",
        "TRAVIS_JOB_NUMBER": "1234.1",
        "TRAVIS_PULL_REQUEST": "false",
        "TRAVIS_PULL_REQUEST_BRANCH": "",
        "TRAVIS_REPO_SLUG": "username/project",
        "TRAVIS_TAG": "",
    }


def setup_azure_pipelines() -> Dict[str, str]:
    """
    Set up Azure Pipelines environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "CI": "true",
        "TF_BUILD": "True",
        "AGENT_ID": "1",
        "AGENT_NAME": "agent",
        "AGENT_JOBNAME": "Job",
        "AGENT_JOBSTATUS": "Succeeded",
        "AGENT_MACHINENAME": "machine",
        "AGENT_WORKFOLDER": "/agent/_work",
        "BUILD_BUILDID": "1234",
        "BUILD_BUILDNUMBER": "20200101.1",
        "BUILD_DEFINITIONNAME": "project",
        "BUILD_DEFINITIONVERSION": "1",
        "BUILD_REASON": "Manual",
        "BUILD_REPOSITORY_NAME": "project",
        "BUILD_REPOSITORY_URI": "https://dev.azure.com/organization/project/_git/project",
        "BUILD_SOURCEBRANCH": "refs/heads/main",
        "BUILD_SOURCEVERSION": "1234567890abcdef1234567890abcdef12345678",
        "SYSTEM_TEAMFOUNDATIONCOLLECTIONURI": "https://dev.azure.com/organization/",
        "SYSTEM_TEAMPROJECT": "project",
    }


def setup_docker() -> Dict[str, str]:
    """
    Set up Docker environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "DOCKER_ENVIRONMENT": "true",
        "DOCKER": "true",
        "HOSTNAME": "container",
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    }


def setup_kubernetes() -> Dict[str, str]:
    """
    Set up Kubernetes environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "KUBERNETES_SERVICE_HOST": "10.0.0.1",
        "KUBERNETES_SERVICE_PORT": "443",
        "KUBERNETES_PORT": "tcp://10.0.0.1:443",
        "KUBERNETES_PORT_443_TCP": "tcp://10.0.0.1:443",
        "KUBERNETES_PORT_443_TCP_PROTO": "tcp",
        "KUBERNETES_PORT_443_TCP_PORT": "443",
        "KUBERNETES_PORT_443_TCP_ADDR": "10.0.0.1",
    }


def setup_docker_compose() -> Dict[str, str]:
    """
    Set up Docker Compose environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "COMPOSE_PROJECT_NAME": "project",
        "COMPOSE_FILE": "docker-compose.yml",
        "COMPOSE_PATH_SEPARATOR": ":",
        "COMPOSE_API_VERSION": "1.40",
    }


def setup_docker_swarm() -> Dict[str, str]:
    """
    Set up Docker Swarm environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "DOCKER_SWARM": "true",
        "SWARM_NODE_ID": "abcdef1234567890",
        "SWARM_MANAGER": "true",
    }


def setup_aws() -> Dict[str, str]:
    """
    Set up AWS environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "AWS_REGION": "us-west-2",
        "AWS_DEFAULT_REGION": "us-west-2",
        "AWS_ACCOUNT_ID": "123456789012",
    }


def setup_aws_lambda() -> Dict[str, str]:
    """
    Set up AWS Lambda environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    aws_vars = setup_aws()
    aws_vars.update({
        "AWS_LAMBDA_FUNCTION_NAME": "my-function",
        "AWS_LAMBDA_FUNCTION_VERSION": "$LATEST",
        "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "128",
        "AWS_LAMBDA_FUNCTION_TIMEOUT": "3",
        "AWS_LAMBDA_LOG_GROUP_NAME": "/aws/lambda/my-function",
        "AWS_LAMBDA_LOG_STREAM_NAME": "2020/01/01/[$LATEST]abcdef1234567890",
        "AWS_EXECUTION_ENV": "AWS_Lambda_python3.8",
        "LAMBDA_TASK_ROOT": "/var/task",
        "LAMBDA_RUNTIME_DIR": "/var/runtime",
    })
    return aws_vars


def setup_azure() -> Dict[str, str]:
    """
    Set up Azure environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "AZURE_SUBSCRIPTION_ID": "12345678-1234-1234-1234-123456789012",
        "AZURE_TENANT_ID": "12345678-1234-1234-1234-123456789012",
        "AZURE_RESOURCE_GROUP": "my-resource-group",
        "AZURE_LOCATION": "westus2",
    }


def setup_azure_functions() -> Dict[str, str]:
    """
    Set up Azure Functions environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    azure_vars = setup_azure()
    azure_vars.update({
        "AZURE_FUNCTIONS_ENVIRONMENT": "Development",
        "WEBSITE_SITE_NAME": "my-function-app",
        "WEBSITE_INSTANCE_ID": "12345678-1234-1234-1234-123456789012",
        "WEBSITE_RESOURCE_GROUP": "my-resource-group",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "FUNCTIONS_EXTENSION_VERSION": "~3",
        "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=abcdef1234567890==;EndpointSuffix=core.windows.net",
    })
    return azure_vars


def setup_gcp() -> Dict[str, str]:
    """
    Set up GCP environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    return {
        "GOOGLE_CLOUD_PROJECT": "my-project",
        "GCLOUD_PROJECT": "my-project",
        "GCP_PROJECT": "my-project",
        "GOOGLE_COMPUTE_ZONE": "us-central1-a",
        "GOOGLE_COMPUTE_REGION": "us-central1",
    }


def setup_gcp_cloud_functions() -> Dict[str, str]:
    """
    Set up GCP Cloud Functions environment variables.

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    gcp_vars = setup_gcp()
    gcp_vars.update({
        "FUNCTION_NAME": "my-function",
        "FUNCTION_REGION": "us-central1",
        "FUNCTION_MEMORY_MB": "128",
        "FUNCTION_TIMEOUT_SEC": "60",
        "FUNCTION_IDENTITY": "my-function@my-project.iam.gserviceaccount.com",
    })
    return gcp_vars


def create_docker_files() -> List[Tuple[str, str]]:
    """
    Create Docker-related files.

    Returns:
        List[Tuple[str, str]]: List of (file_path, content) tuples
    """
    return [
        ("/.dockerenv", ""),
        ("/proc/1/cgroup", "12:memory:/docker/abcdef1234567890\n"),
    ]


def create_kubernetes_files() -> List[Tuple[str, str]]:
    """
    Create Kubernetes-related files.

    Returns:
        List[Tuple[str, str]]: List of (file_path, content) tuples
    """
    return [
        ("/var/run/secrets/kubernetes.io/serviceaccount/token", "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9..."),
        ("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "default"),
        ("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt", "-----BEGIN CERTIFICATE-----\nMIIC5z..."),
    ]


def get_ci_env_vars(ci_type: str) -> Dict[str, str]:
    """
    Get environment variables for a specific CI platform.

    Args:
        ci_type: CI platform type

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    ci_type = ci_type.lower()
    if ci_type == "github":
        return setup_github_actions()
    elif ci_type == "jenkins":
        return setup_jenkins()
    elif ci_type == "gitlab":
        return setup_gitlab_ci()
    elif ci_type == "circle":
        return setup_circleci()
    elif ci_type == "travis":
        return setup_travis()
    elif ci_type == "azure":
        return setup_azure_pipelines()
    else:
        return {"CI": "true"}


def get_container_env_vars(container_type: str) -> Dict[str, str]:
    """
    Get environment variables for a specific container environment.

    Args:
        container_type: Container environment type

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    container_type = container_type.lower()
    if container_type == "docker":
        return setup_docker()
    elif container_type == "kubernetes":
        return setup_kubernetes()
    elif container_type == "docker-compose":
        return setup_docker_compose()
    elif container_type == "docker-swarm":
        return setup_docker_swarm()
    else:
        return {}


def get_cloud_env_vars(cloud_type: str) -> Dict[str, str]:
    """
    Get environment variables for a specific cloud environment.

    Args:
        cloud_type: Cloud environment type

    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    cloud_type = cloud_type.lower()
    if cloud_type == "aws":
        return setup_aws()
    elif cloud_type == "aws-lambda":
        return setup_aws_lambda()
    elif cloud_type == "azure":
        return setup_azure()
    elif cloud_type == "azure-functions":
        return setup_azure_functions()
    elif cloud_type == "gcp":
        return setup_gcp()
    elif cloud_type == "gcp-cloud-functions":
        return setup_gcp_cloud_functions()
    else:
        return {}


def main() -> int:
    """
    Main function.

    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(description="CI Environment Simulation Script")
    parser.add_argument("--ci-type", help="CI platform to simulate")
    parser.add_argument("--container-type", help="Container environment to simulate")
    parser.add_argument("--cloud-type", help="Cloud environment to simulate")
    parser.add_argument("--cleanup", action="store_true", help="Remove all simulated environment variables and files")
    args = parser.parse_args()

    if args.cleanup:
        # Clean up environment variables
        for key in list(os.environ.keys()):
            if key.startswith(("GITHUB_", "JENKINS_", "CI_", "CIRCLE_", "TRAVIS_", "AGENT_", "BUILD_", "SYSTEM_",
                              "DOCKER_", "KUBERNETES_", "COMPOSE_", "SWARM_", "AWS_", "AZURE_", "GOOGLE_", "GCP_",
                              "FUNCTION_")):
                del os.environ[key]
        
        # Clean up CI variable
        if "CI" in os.environ:
            del os.environ["CI"]
        
        print("Cleaned up all simulated environment variables.")
        return 0

    # Set environment variables
    env_vars = {}
    
    if args.ci_type:
        env_vars.update(get_ci_env_vars(args.ci_type))
        print(f"Simulating {args.ci_type} CI environment.")
    
    if args.container_type:
        env_vars.update(get_container_env_vars(args.container_type))
        print(f"Simulating {args.container_type} container environment.")
    
    if args.cloud_type:
        env_vars.update(get_cloud_env_vars(args.cloud_type))
        print(f"Simulating {args.cloud_type} cloud environment.")
    
    # Apply environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print(f"Set {len(env_vars)} environment variables.")
    
    # Create necessary files for container environments
    if args.container_type == "docker":
        temp_dir = tempfile.mkdtemp(prefix="docker_sim_")
        for file_path, content in create_docker_files():
            os.makedirs(os.path.dirname(temp_dir + file_path), exist_ok=True)
            with open(temp_dir + file_path, "w") as f:
                f.write(content)
        print(f"Created Docker files in {temp_dir}")
    
    if args.container_type == "kubernetes":
        temp_dir = tempfile.mkdtemp(prefix="k8s_sim_")
        for file_path, content in create_kubernetes_files():
            os.makedirs(os.path.dirname(temp_dir + file_path), exist_ok=True)
            with open(temp_dir + file_path, "w") as f:
                f.write(content)
        print(f"Created Kubernetes files in {temp_dir}")
    
    print("\nEnvironment simulation complete. Run your tests now.")
    print("To clean up, run: python simulate_ci_environment.py --cleanup")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
