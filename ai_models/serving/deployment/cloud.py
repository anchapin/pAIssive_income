"""
"""
Cloud deployment utilities for AI models.
Cloud deployment utilities for AI models.


This module provides utilities for deploying AI models to cloud platforms.
This module provides utilities for deploying AI models to cloud platforms.
"""
"""


# ModelName should be defined in the context
# ModelName should be defined in the context


import enum
import enum
import logging
import logging
import os
import os
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


import boto3
import boto3


# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class CloudProvider(enum.Enum):
    class CloudProvider(enum.Enum):
    """
    """
    Enumeration of cloud providers.
    Enumeration of cloud providers.
    """
    """


    AWS = "aws"
    AWS = "aws"
    GCP = "gcp"
    GCP = "gcp"
    AZURE = "azure"
    AZURE = "azure"




    @dataclass
    @dataclass
    class CloudConfig:
    class CloudConfig:
    """
    """
    Configuration for cloud deployment.
    Configuration for cloud deployment.
    """
    """


    # Basic configuration
    # Basic configuration
    provider: CloudProvider
    provider: CloudProvider
    name: str
    name: str
    region: str
    region: str


    # Server configuration
    # Server configuration
    server_type: str = "rest"  # "rest" or "grpc"
    server_type: str = "rest"  # "rest" or "grpc"
    port: int = 8000
    port: int = 8000


    # Model configuration
    # Model configuration
    model_path: str = ""
    model_path: str = ""
    model_type: str = "text-generation"
    model_type: str = "text-generation"
    model_id: str = ""
    model_id: str = ""


    # Resource configuration
    # Resource configuration
    instance_type: str = ""
    instance_type: str = ""
    cpu_count: int = 2
    cpu_count: int = 2
    memory_gb: int = 8
    memory_gb: int = 8
    gpu_type: Optional[str] = None
    gpu_type: Optional[str] = None
    gpu_count: int = 0
    gpu_count: int = 0


    # Scaling configuration
    # Scaling configuration
    min_instances: int = 1
    min_instances: int = 1
    max_instances: int = 1
    max_instances: int = 1


    # Network configuration
    # Network configuration
    vpc_id: Optional[str] = None
    vpc_id: Optional[str] = None
    subnet_ids: List[str] = field(default_factory=list)
    subnet_ids: List[str] = field(default_factory=list)
    security_group_ids: List[str] = field(default_factory=list)
    security_group_ids: List[str] = field(default_factory=list)


    # Storage configuration
    # Storage configuration
    storage_size_gb: int = 20
    storage_size_gb: int = 20
    storage_type: str = "ssd"
    storage_type: str = "ssd"


    # Environment variables
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)


    # Authentication configuration
    # Authentication configuration
    auth_enabled: bool = False
    auth_enabled: bool = False
    auth_type: str = "api_key"  # "api_key", "oauth", "iam"
    auth_type: str = "api_key"  # "api_key", "oauth", "iam"


    # Additional configuration
    # Additional configuration
    additional_params: Dict[str, Any] = field(default_factory=dict)
    additional_params: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the configuration to a dictionary.
    Convert the configuration to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the configuration
    Dictionary representation of the configuration
    """
    """
    return {
    return {
    "provider": self.provider.value,
    "provider": self.provider.value,
    "name": self.name,
    "name": self.name,
    "region": self.region,
    "region": self.region,
    "server_type": self.server_type,
    "server_type": self.server_type,
    "port": self.port,
    "port": self.port,
    "model_path": self.model_path,
    "model_path": self.model_path,
    "model_type": self.model_type,
    "model_type": self.model_type,
    "model_id": self.model_id,
    "model_id": self.model_id,
    "instance_type": self.instance_type,
    "instance_type": self.instance_type,
    "cpu_count": self.cpu_count,
    "cpu_count": self.cpu_count,
    "memory_gb": self.memory_gb,
    "memory_gb": self.memory_gb,
    "gpu_type": self.gpu_type,
    "gpu_type": self.gpu_type,
    "gpu_count": self.gpu_count,
    "gpu_count": self.gpu_count,
    "min_instances": self.min_instances,
    "min_instances": self.min_instances,
    "max_instances": self.max_instances,
    "max_instances": self.max_instances,
    "vpc_id": self.vpc_id,
    "vpc_id": self.vpc_id,
    "subnet_ids": self.subnet_ids,
    "subnet_ids": self.subnet_ids,
    "security_group_ids": self.security_group_ids,
    "security_group_ids": self.security_group_ids,
    "storage_size_gb": self.storage_size_gb,
    "storage_size_gb": self.storage_size_gb,
    "storage_type": self.storage_type,
    "storage_type": self.storage_type,
    "env_vars": self.env_vars,
    "env_vars": self.env_vars,
    "auth_enabled": self.auth_enabled,
    "auth_enabled": self.auth_enabled,
    "auth_type": self.auth_type,
    "auth_type": self.auth_type,
    **self.additional_params,
    **self.additional_params,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CloudConfig":
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CloudConfig":
    """
    """
    Create a configuration from a dictionary.
    Create a configuration from a dictionary.


    Args:
    Args:
    config_dict: Dictionary with configuration parameters
    config_dict: Dictionary with configuration parameters


    Returns:
    Returns:
    Cloud configuration
    Cloud configuration
    """
    """
    # Extract provider
    # Extract provider
    provider_str = config_dict.pop("provider", "aws")
    provider_str = config_dict.pop("provider", "aws")
    try:
    try:
    provider = CloudProvider(provider_str)
    provider = CloudProvider(provider_str)
except ValueError:
except ValueError:
    provider = CloudProvider.AWS
    provider = CloudProvider.AWS


    # Extract additional parameters
    # Extract additional parameters
    additional_params = {}
    additional_params = {}
    for key, value in list(config_dict.items()):
    for key, value in list(config_dict.items()):
    if key not in cls.__annotations__:
    if key not in cls.__annotations__:
    additional_params[key] = config_dict.pop(key)
    additional_params[key] = config_dict.pop(key)


    # Create configuration
    # Create configuration
    config = cls(provider=provider, **config_dict)
    config = cls(provider=provider, **config_dict)


    config.additional_params = additional_params
    config.additional_params = additional_params
    return config
    return config




    def generate_cloud_config(config: CloudConfig, output_dir: str) -> str:
    def generate_cloud_config(config: CloudConfig, output_dir: str) -> str:
    """
    """
    Generate cloud deployment configuration files.
    Generate cloud deployment configuration files.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_dir: Directory to save the configuration files
    output_dir: Directory to save the configuration files


    Returns:
    Returns:
    Path to the generated configuration file
    Path to the generated configuration file
    """
    """
    # Create output directory
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Generate configuration based on provider
    # Generate configuration based on provider
    if config.provider == CloudProvider.AWS:
    if config.provider == CloudProvider.AWS:
    return _generate_aws_config(config, output_dir)
    return _generate_aws_config(config, output_dir)
    elif config.provider == CloudProvider.GCP:
    elif config.provider == CloudProvider.GCP:
    return _generate_gcp_config(config, output_dir)
    return _generate_gcp_config(config, output_dir)
    elif config.provider == CloudProvider.AZURE:
    elif config.provider == CloudProvider.AZURE:
    return _generate_azure_config(config, output_dir)
    return _generate_azure_config(config, output_dir)
    else:
    else:
    raise ValueError(f"Unsupported cloud provider: {config.provider}")
    raise ValueError(f"Unsupported cloud provider: {config.provider}")




    def _generate_aws_config(config: CloudConfig, output_dir: str) -> str:
    def _generate_aws_config(config: CloudConfig, output_dir: str) -> str:
    """
    """
    Generate AWS deployment configuration files.
    Generate AWS deployment configuration files.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_dir: Directory to save the configuration files
    output_dir: Directory to save the configuration files


    Returns:
    Returns:
    Path to the generated configuration file
    Path to the generated configuration file
    """
    """
    # Generate CloudFormation template
    # Generate CloudFormation template
    template_path = os.path.join(output_dir, "cloudformation.yaml")
    template_path = os.path.join(output_dir, "cloudformation.yaml")
    _generate_cloudformation_template(config, template_path)
    _generate_cloudformation_template(config, template_path)


    # Generate deployment script
    # Generate deployment script
    script_path = os.path.join(output_dir, "deploy.sh")
    script_path = os.path.join(output_dir, "deploy.sh")
    _generate_aws_deploy_script(config, script_path)
    _generate_aws_deploy_script(config, script_path)


    logger.info(f"AWS configuration files generated in {output_dir}")
    logger.info(f"AWS configuration files generated in {output_dir}")


    return template_path
    return template_path




    def _generate_gcp_config(config: CloudConfig, output_dir: str) -> str:
    def _generate_gcp_config(config: CloudConfig, output_dir: str) -> str:
    """
    """
    Generate GCP deployment configuration files.
    Generate GCP deployment configuration files.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_dir: Directory to save the configuration files
    output_dir: Directory to save the configuration files


    Returns:
    Returns:
    Path to the generated configuration file
    Path to the generated configuration file
    """
    """
    # Generate Terraform configuration
    # Generate Terraform configuration
    terraform_path = os.path.join(output_dir, "main.t")
    terraform_path = os.path.join(output_dir, "main.t")
    _generate_gcp_terraform(config, terraform_path)
    _generate_gcp_terraform(config, terraform_path)


    # Generate deployment script
    # Generate deployment script
    script_path = os.path.join(output_dir, "deploy.sh")
    script_path = os.path.join(output_dir, "deploy.sh")
    _generate_gcp_deploy_script(config, script_path)
    _generate_gcp_deploy_script(config, script_path)


    logger.info(f"GCP configuration files generated in {output_dir}")
    logger.info(f"GCP configuration files generated in {output_dir}")


    return terraform_path
    return terraform_path




    def _generate_azure_config(config: CloudConfig, output_dir: str) -> str:
    def _generate_azure_config(config: CloudConfig, output_dir: str) -> str:
    """
    """
    Generate Azure deployment configuration files.
    Generate Azure deployment configuration files.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_dir: Directory to save the configuration files
    output_dir: Directory to save the configuration files


    Returns:
    Returns:
    Path to the generated configuration file
    Path to the generated configuration file
    """
    """
    # Generate ARM template
    # Generate ARM template
    template_path = os.path.join(output_dir, "azuredeploy.json")
    template_path = os.path.join(output_dir, "azuredeploy.json")
    _generate_arm_template(config, template_path)
    _generate_arm_template(config, template_path)


    # Generate deployment script
    # Generate deployment script
    script_path = os.path.join(output_dir, "deploy.sh")
    script_path = os.path.join(output_dir, "deploy.sh")
    _generate_azure_deploy_script(config, script_path)
    _generate_azure_deploy_script(config, script_path)


    logger.info(f"Azure configuration files generated in {output_dir}")
    logger.info(f"Azure configuration files generated in {output_dir}")


    return template_path
    return template_path




    def _generate_cloudformation_template(config: CloudConfig, output_path: str) -> None:
    def _generate_cloudformation_template(config: CloudConfig, output_path: str) -> None:
    """
    """
    Generate an AWS CloudFormation template.
    Generate an AWS CloudFormation template.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_path: Path to save the CloudFormation template
    output_path: Path to save the CloudFormation template
    """
    """
    # Create CloudFormation template content
    # Create CloudFormation template content
    content = """
    content = """
    AWSTemplateFormatVersion: '2010-09-09'
    AWSTemplateFormatVersion: '2010-09-09'
    Description: 'AI Model Deployment'
    Description: 'AI Model Deployment'


    Parameters:
    Parameters:
    ModelName:
    ModelName:
    Type: String
    Type: String
    Default: {config.name}
    Default: {config.name}
    Description: Name of the model deployment
    Description: Name of the model deployment


    ModelPath:
    ModelPath:
    Type: String
    Type: String
    Default: {config.model_path}
    Default: {config.model_path}
    Description: Path to the model
    Description: Path to the model


    ModelType:
    ModelType:
    Type: String
    Type: String
    Default: {config.model_type}
    Default: {config.model_type}
    Description: Type of the model
    Description: Type of the model


    ServerType:
    ServerType:
    Type: String
    Type: String
    Default: {config.server_type}
    Default: {config.server_type}
    Description: Type of the server (rest or grpc)
    Description: Type of the server (rest or grpc)


    Port:
    Port:
    Type: Number
    Type: Number
    Default: {config.port}
    Default: {config.port}
    Description: Port for the server
    Description: Port for the server


    InstanceType:
    InstanceType:
    Type: String
    Type: String
    Default: {config.instance_type or "ml.m5.large"}
    Default: {config.instance_type or "ml.m5.large"}
    Description: Instance type for the deployment
    Description: Instance type for the deployment


    MinInstances:
    MinInstances:
    Type: Number
    Type: Number
    Default: {config.min_instances}
    Default: {config.min_instances}
    Description: Minimum number of instances
    Description: Minimum number of instances


    MaxInstances:
    MaxInstances:
    Type: Number
    Type: Number
    Default: {config.max_instances}
    Default: {config.max_instances}
    Description: Maximum number of instances
    Description: Maximum number of instances


    Resources:
    Resources:
    ModelRole:
    ModelRole:
    Type: AWS::IAM::Role
    Type: AWS::IAM::Role
    Properties:
    Properties:
    AssumeRolePolicyDocument:
    AssumeRolePolicyDocument:
    Version: '2012-10-17'
    Version: '2012-10-17'
    Statement:
    Statement:
    - Effect: Allow
    - Effect: Allow
    Principal:
    Principal:
    Service: sagemaker.amazonaws.com
    Service: sagemaker.amazonaws.com
    Action: 'sts:AssumeRole'
    Action: 'sts:AssumeRole'
    ManagedPolicyArns:
    ManagedPolicyArns:
    - 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
    - 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
    - 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
    - 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'


    ModelEndpoint:
    ModelEndpoint:
    Type: AWS::SageMaker::Endpoint
    Type: AWS::SageMaker::Endpoint
    Properties:
    Properties:
    EndpointName: !Ref ModelName
    EndpointName: !Ref ModelName
    EndpointConfigName: !GetAtt ModelEndpointConfig.EndpointConfigName
    EndpointConfigName: !GetAtt ModelEndpointConfig.EndpointConfigName


    ModelEndpointConfig:
    ModelEndpointConfig:
    Type: AWS::SageMaker::EndpointConfig
    Type: AWS::SageMaker::EndpointConfig
    Properties:
    Properties:
    ProductionVariants:
    ProductionVariants:
    - InitialInstanceCount: !Ref MinInstances
    - InitialInstanceCount: !Ref MinInstances
    InstanceType: !Ref InstanceType
    InstanceType: !Ref InstanceType
    ModelName: !GetAtt Model.ModelName
    ModelName: !GetAtt Model.ModelName
    VariantName: AllTraffic
    VariantName: AllTraffic
    InitialVariantWeight: 1.0
    InitialVariantWeight: 1.0


    Model:
    Model:
    Type: AWS::SageMaker::Model
    Type: AWS::SageMaker::Model
    Properties:
    Properties:
    ModelName: !Ref ModelName
    ModelName: !Ref ModelName
    ExecutionRoleArn: !GetAtt ModelRole.Arn
    ExecutionRoleArn: !GetAtt ModelRole.Arn
    PrimaryContainer:
    PrimaryContainer:
    Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/${ModelName}:latest'
    Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/${ModelName}:latest'
    Environment:
    Environment:
    MODEL_PATH: !Ref ModelPath
    MODEL_PATH: !Ref ModelPath
    MODEL_TYPE: !Ref ModelType
    MODEL_TYPE: !Ref ModelType
    SERVER_TYPE: !Ref ServerType
    SERVER_TYPE: !Ref ServerType
    PORT: !Ref Port
    PORT: !Ref Port
    """
    """


    # Add environment variables
    # Add environment variables
    for key, value in config.env_vars.items():
    for key, value in config.env_vars.items():
    content += f"          {key}: {value}\n"
    content += f"          {key}: {value}\n"


    # Add outputs
    # Add outputs
    content += """
    content += """
    Outputs:
    Outputs:
    EndpointName:
    EndpointName:
    Description: Name of the SageMaker endpoint
    Description: Name of the SageMaker endpoint
    Value: !Ref ModelEndpoint
    Value: !Ref ModelEndpoint


    EndpointUrl:
    EndpointUrl:
    Description: URL of the SageMaker endpoint
    Description: URL of the SageMaker endpoint
    Value: !Sub 'https://runtime.sagemaker.${AWS::Region}.amazonaws.com/endpoints/${ModelEndpoint}'
    Value: !Sub 'https://runtime.sagemaker.${AWS::Region}.amazonaws.com/endpoints/${ModelEndpoint}'
    """
    """


    # Write CloudFormation template
    # Write CloudFormation template
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_aws_deploy_script(config: CloudConfig, output_path: str) -> None:
    def _generate_aws_deploy_script(config: CloudConfig, output_path: str) -> None:
    """
    """
    Generate an AWS deployment script.
    Generate an AWS deployment script.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_path: Path to save the deployment script
    output_path: Path to save the deployment script
    """
    """
    # Create deployment script content
    # Create deployment script content
    content = """#!/bin/bash
    content = """#!/bin/bash
    set -e
    set -e


    # Configuration
    # Configuration
    STACK_NAME="{config.name}"
    STACK_NAME="{config.name}"
    REGION="{config.region}"
    REGION="{config.region}"
    MODEL_NAME="{config.name}"
    MODEL_NAME="{config.name}"
    ECR_REPOSITORY="{config.name}"
    ECR_REPOSITORY="{config.name}"


    # Build and push Docker image
    # Build and push Docker image
    echo "Building Docker image..."
    echo "Building Docker image..."
    docker build -t $ECR_REPOSITORY:latest .
    docker build -t $ECR_REPOSITORY:latest .


    echo "Logging in to ECR..."
    echo "Logging in to ECR..."
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com


    echo "Creating ECR repository if it doesn't exist..."
    echo "Creating ECR repository if it doesn't exist..."
    aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $REGION || aws ecr create-repository --repository-name $ECR_REPOSITORY --region $REGION
    aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $REGION || aws ecr create-repository --repository-name $ECR_REPOSITORY --region $REGION


    echo "Pushing Docker image to ECR..."
    echo "Pushing Docker image to ECR..."
    docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest
    docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest


    # Deploy CloudFormation stack
    # Deploy CloudFormation stack
    echo "Deploying CloudFormation stack..."
    echo "Deploying CloudFormation stack..."
    aws cloudformation deploy \\
    aws cloudformation deploy \\
    --template-file cloudformation.yaml \\
    --template-file cloudformation.yaml \\
    --stack-name $STACK_NAME \\
    --stack-name $STACK_NAME \\
    --capabilities CAPABILITY_IAM \\
    --capabilities CAPABILITY_IAM \\
    --region $REGION \\
    --region $REGION \\
    --parameter-overrides \\
    --parameter-overrides \\
    ModelName=$MODEL_NAME \\
    ModelName=$MODEL_NAME \\
    ModelPath="{config.model_path}" \\
    ModelPath="{config.model_path}" \\
    ModelType="{config.model_type}" \\
    ModelType="{config.model_type}" \\
    ServerType="{config.server_type}" \\
    ServerType="{config.server_type}" \\
    Port={config.port} \\
    Port={config.port} \\
    InstanceType="{config.instance_type or "ml.m5.large"}" \\
    InstanceType="{config.instance_type or "ml.m5.large"}" \\
    MinInstances={config.min_instances} \\
    MinInstances={config.min_instances} \\
    MaxInstances={config.max_instances}
    MaxInstances={config.max_instances}


    echo "Deployment completed successfully!"
    echo "Deployment completed successfully!"
    echo "Endpoint URL: https://runtime.sagemaker.$REGION.amazonaws.com/endpoints/$MODEL_NAME"
    echo "Endpoint URL: https://runtime.sagemaker.$REGION.amazonaws.com/endpoints/$MODEL_NAME"
    """
    """


    # Write deployment script
    # Write deployment script
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())


    # Make script executable
    # Make script executable
    os.chmod(output_path, 0o755)
    os.chmod(output_path, 0o755)




    def _generate_gcp_terraform(config: CloudConfig, output_path: str) -> None:
    def _generate_gcp_terraform(config: CloudConfig, output_path: str) -> None:
    """
    """
    Generate a GCP Terraform configuration.
    Generate a GCP Terraform configuration.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_path: Path to save the Terraform configuration
    output_path: Path to save the Terraform configuration
    """
    """
    # Create Terraform configuration content
    # Create Terraform configuration content
    content = """
    content = """
    provider "google" {{
    provider "google" {{
    project = var.project_id
    project = var.project_id
    region  = "{config.region}"
    region  = "{config.region}"
    }}
    }}


    variable "project_id" {{
    variable "project_id" {{
    description = "GCP Project ID"
    description = "GCP Project ID"
    type        = string
    type        = string
    }}
    }}


    resource "google_artifact_registry_repository" "model_repository" {{
    resource "google_artifact_registry_repository" "model_repository" {{
    location      = "{config.region}"
    location      = "{config.region}"
    repository_id = "{config.name}"
    repository_id = "{config.name}"
    format        = "DOCKER"
    format        = "DOCKER"
    }}
    }}


    resource "google_cloud_run_service" "model_service" {{
    resource "google_cloud_run_service" "model_service" {{
    name     = "{config.name}"
    name     = "{config.name}"
    location = "{config.region}"
    location = "{config.region}"


    template {{
    template {{
    spec {{
    spec {{
    containers {{
    containers {{
    image = "${{google_artifact_registry_repository.model_repository.location}}-docker.pkg.dev/${{var.project_id}}/${{google_artifact_registry_repository.model_repository.repository_id}}/{config.name}:latest"
    image = "${{google_artifact_registry_repository.model_repository.location}}-docker.pkg.dev/${{var.project_id}}/${{google_artifact_registry_repository.model_repository.repository_id}}/{config.name}:latest"


    resources {{
    resources {{
    limits = {{
    limits = {{
    cpu    = "{config.cpu_count}"
    cpu    = "{config.cpu_count}"
    memory = "{config.memory_gb}Gi"
    memory = "{config.memory_gb}Gi"
    }}
    }}
    }}
    }}


    ports {{
    ports {{
    container_port = {config.port}
    container_port = {config.port}
    }}
    }}


    env {{
    env {{
    name  = "MODEL_PATH"
    name  = "MODEL_PATH"
    value = "{config.model_path}"
    value = "{config.model_path}"
    }}
    }}


    env {{
    env {{
    name  = "MODEL_TYPE"
    name  = "MODEL_TYPE"
    value = "{config.model_type}"
    value = "{config.model_type}"
    }}
    }}


    env {{
    env {{
    name  = "SERVER_TYPE"
    name  = "SERVER_TYPE"
    value = "{config.server_type}"
    value = "{config.server_type}"
    }}
    }}


    env {{
    env {{
    name  = "PORT"
    name  = "PORT"
    value = "{config.port}"
    value = "{config.port}"
    }}
    }}
    """
    """


    # Add environment variables
    # Add environment variables
    for key, value in config.env_vars.items():
    for key, value in config.env_vars.items():
    content += """
    content += """
    env {{
    env {{
    name  = "{key}"
    name  = "{key}"
    value = "{value}"
    value = "{value}"
    }}"""
    }}"""


    # Add GPU configuration if needed
    # Add GPU configuration if needed
    if config.gpu_count > 0 and config.gpu_type:
    if config.gpu_count > 0 and config.gpu_type:
    content += """
    content += """


    # GPU configuration
    # GPU configuration
    resources {{
    resources {{
    limits {{
    limits {{
    "nvidia.com/gpu" = {config.gpu_count}
    "nvidia.com/gpu" = {config.gpu_count}
    }}
    }}
    }}"""
    }}"""


    # Add scaling configuration
    # Add scaling configuration
    content += """
    content += """
    }}
    }}


    container_concurrency = 80
    container_concurrency = 80
    timeout_seconds       = 300
    timeout_seconds       = 300
    }}
    }}


    metadata {{
    metadata {{
    annotations = {{
    annotations = {{
    "autoscaling.knative.dev/minScale" = "{config.min_instances}"
    "autoscaling.knative.dev/minScale" = "{config.min_instances}"
    "autoscaling.knative.dev/maxScale" = "{config.max_instances}"
    "autoscaling.knative.dev/maxScale" = "{config.max_instances}"
    }}
    }}
    }}
    }}
    }}
    }}


    traffic {{
    traffic {{
    percent         = 100
    percent         = 100
    latest_revision = true
    latest_revision = true
    }}
    }}
    }}
    }}


    resource "google_cloud_run_service_iam_member" "public_access" {{
    resource "google_cloud_run_service_iam_member" "public_access" {{
    service  = google_cloud_run_service.model_service.name
    service  = google_cloud_run_service.model_service.name
    location = google_cloud_run_service.model_service.location
    location = google_cloud_run_service.model_service.location
    role     = "roles/run.invoker"
    role     = "roles/run.invoker"
    member   = "allUsers"
    member   = "allUsers"
    }}
    }}


    output "service_url" {{
    output "service_url" {{
    value = google_cloud_run_service.model_service.status[0].url
    value = google_cloud_run_service.model_service.status[0].url
    }}
    }}
    """
    """


    # Write Terraform configuration
    # Write Terraform configuration
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_gcp_deploy_script(config: CloudConfig, output_path: str) -> None:
    def _generate_gcp_deploy_script(config: CloudConfig, output_path: str) -> None:
    """
    """
    Generate a GCP deployment script.
    Generate a GCP deployment script.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_path: Path to save the deployment script
    output_path: Path to save the deployment script
    """
    """
    # Create deployment script content
    # Create deployment script content
    content = """#!/bin/bash
    content = """#!/bin/bash
    set -e
    set -e


    # Configuration
    # Configuration
    PROJECT_ID=$(gcloud config get-value project)
    PROJECT_ID=$(gcloud config get-value project)
    REGION="{config.region}"
    REGION="{config.region}"
    REPOSITORY="{config.name}"
    REPOSITORY="{config.name}"
    IMAGE="{config.name}"
    IMAGE="{config.name}"


    # Build and push Docker image
    # Build and push Docker image
    echo "Building Docker image..."
    echo "Building Docker image..."
    docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest .
    docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest .


    echo "Configuring Docker for Artifact Registry..."
    echo "Configuring Docker for Artifact Registry..."
    gcloud auth configure-docker $REGION-docker.pkg.dev
    gcloud auth configure-docker $REGION-docker.pkg.dev


    echo "Creating Artifact Registry repository if it doesn't exist..."
    echo "Creating Artifact Registry repository if it doesn't exist..."
    gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION --description="Repository for $IMAGE" || true
    gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION --description="Repository for $IMAGE" || true


    echo "Pushing Docker image to Artifact Registry..."
    echo "Pushing Docker image to Artifact Registry..."
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest
    docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest


    # Initialize Terraform
    # Initialize Terraform
    echo "Initializing Terraform..."
    echo "Initializing Terraform..."
    terraform init
    terraform init


    # Apply Terraform configuration
    # Apply Terraform configuration
    echo "Applying Terraform configuration..."
    echo "Applying Terraform configuration..."
    terraform apply -var="project_id=$PROJECT_ID" -auto-approve
    terraform apply -var="project_id=$PROJECT_ID" -auto-approve


    # Get service URL
    # Get service URL
    SERVICE_URL=$(terraform output -raw service_url)
    SERVICE_URL=$(terraform output -raw service_url)


    echo "Deployment completed successfully!"
    echo "Deployment completed successfully!"
    echo "Service URL: $SERVICE_URL"
    echo "Service URL: $SERVICE_URL"
    """
    """


    # Write deployment script
    # Write deployment script
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())


    # Make script executable
    # Make script executable
    os.chmod(output_path, 0o755)
    os.chmod(output_path, 0o755)




    def _generate_arm_template(config: CloudConfig, output_path: str) -> None:
    def _generate_arm_template(config: CloudConfig, output_path: str) -> None:
    """
    """
    Generate an Azure ARM template.
    Generate an Azure ARM template.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_path: Path to save the ARM template
    output_path: Path to save the ARM template
    """
    """
    # Create ARM template content
    # Create ARM template content
    content = """{{
    content = """{{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "contentVersion": "1.0.0.0",
    "parameters": {{
    "parameters": {{
    "containerRegistryName": {{
    "containerRegistryName": {{
    "type": "string",
    "type": "string",
    "defaultValue": "{config.name}registry",
    "defaultValue": "{config.name}registry",
    "metadata": {{
    "metadata": {{
    "description": "Name of the container registry"
    "description": "Name of the container registry"
    }}
    }}
    }},
    }},
    "containerAppName": {{
    "containerAppName": {{
    "type": "string",
    "type": "string",
    "defaultValue": "{config.name}",
    "defaultValue": "{config.name}",
    "metadata": {{
    "metadata": {{
    "description": "Name of the container app"
    "description": "Name of the container app"
    }}
    }}
    }},
    }},
    "location": {{
    "location": {{
    "type": "string",
    "type": "string",
    "defaultValue": "{config.region}",
    "defaultValue": "{config.region}",
    "metadata": {{
    "metadata": {{
    "description": "Location for all resources"
    "description": "Location for all resources"
    }}
    }}
    }}
    }}
    }},
    }},
    "variables": {{
    "variables": {{
    "containerAppEnvironmentName": "[concat(parameters('containerAppName'), '-env')]",
    "containerAppEnvironmentName": "[concat(parameters('containerAppName'), '-env')]",
    "logAnalyticsWorkspaceName": "[concat(parameters('containerAppName'), '-logs')]",
    "logAnalyticsWorkspaceName": "[concat(parameters('containerAppName'), '-logs')]",
    "imageName": "[concat(parameters('containerRegistryName'), '.azurecr.io/', parameters('containerAppName'), ':latest')]"
    "imageName": "[concat(parameters('containerRegistryName'), '.azurecr.io/', parameters('containerAppName'), ':latest')]"
    }},
    }},
    "resources": [
    "resources": [
    {{
    {{
    "type": "Microsoft.ContainerRegistry/registries",
    "type": "Microsoft.ContainerRegistry/registries",
    "apiVersion": "2021-06-01-preview",
    "apiVersion": "2021-06-01-preview",
    "name": "[parameters('containerRegistryName')]",
    "name": "[parameters('containerRegistryName')]",
    "location": "[parameters('location')]",
    "location": "[parameters('location')]",
    "sku": {{
    "sku": {{
    "name": "Basic"
    "name": "Basic"
    }},
    }},
    "properties": {{
    "properties": {{
    "adminUserEnabled": true
    "adminUserEnabled": true
    }}
    }}
    }},
    }},
    {{
    {{
    "type": "Microsoft.OperationalInsights/workspaces",
    "type": "Microsoft.OperationalInsights/workspaces",
    "apiVersion": "2021-06-01",
    "apiVersion": "2021-06-01",
    "name": "[variables('logAnalyticsWorkspaceName')]",
    "name": "[variables('logAnalyticsWorkspaceName')]",
    "location": "[parameters('location')]",
    "location": "[parameters('location')]",
    "properties": {{
    "properties": {{
    "retentionInDays": 30,
    "retentionInDays": 30,
    "features": {{
    "features": {{
    "enableLogAccessUsingOnlyResourcePermissions": true
    "enableLogAccessUsingOnlyResourcePermissions": true
    }},
    }},
    "sku": {{
    "sku": {{
    "name": "PerGB2018"
    "name": "PerGB2018"
    }}
    }}
    }}
    }}
    }},
    }},
    {{
    {{
    "type": "Microsoft.App/managedEnvironments",
    "type": "Microsoft.App/managedEnvironments",
    "apiVersion": "2022-03-01",
    "apiVersion": "2022-03-01",
    "name": "[variables('containerAppEnvironmentName')]",
    "name": "[variables('containerAppEnvironmentName')]",
    "location": "[parameters('location')]",
    "location": "[parameters('location')]",
    "properties": {{
    "properties": {{
    "appLogsConfiguration": {{
    "appLogsConfiguration": {{
    "destination": "log-analytics",
    "destination": "log-analytics",
    "logAnalyticsConfiguration": {{
    "logAnalyticsConfiguration": {{
    "customerId": "[reference(resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName'))).customerId]",
    "customerId": "[reference(resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName'))).customerId]",
    "sharedKey": "[listKeys(resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName')), '2021-06-01').primarySharedKey]"
    "sharedKey": "[listKeys(resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName')), '2021-06-01').primarySharedKey]"
    }}
    }}
    }}
    }}
    }},
    }},
    "dependsOn": [
    "dependsOn": [
    "[resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName'))]"
    "[resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName'))]"
    ]
    ]
    }},
    }},
    {{
    {{
    "type": "Microsoft.App/containerApps",
    "type": "Microsoft.App/containerApps",
    "apiVersion": "2022-03-01",
    "apiVersion": "2022-03-01",
    "name": "[parameters('containerAppName')]",
    "name": "[parameters('containerAppName')]",
    "location": "[parameters('location')]",
    "location": "[parameters('location')]",
    "properties": {{
    "properties": {{
    "managedEnvironmentId": "[resourceId('Microsoft.App/managedEnvironments', variables('containerAppEnvironmentName'))]",
    "managedEnvironmentId": "[resourceId('Microsoft.App/managedEnvironments', variables('containerAppEnvironmentName'))]",
    "configuration": {{
    "configuration": {{
    "ingress": {{
    "ingress": {{
    "external": true,
    "external": true,
    "targetPort": {config.port},
    "targetPort": {config.port},
    "allowInsecure": false,
    "allowInsecure": false,
    "traffic": [
    "traffic": [
    {{
    {{
    "latestRevision": true,
    "latestRevision": true,
    "weight": 100
    "weight": 100
    }}
    }}
    ]
    ]
    }},
    }},
    "registries": [
    "registries": [
    {{
    {{
    "server": "[concat(parameters('containerRegistryName'), '.azurecr.io')]",
    "server": "[concat(parameters('containerRegistryName'), '.azurecr.io')]",
    "username": "[listCredentials(resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName')), '2021-06-01-preview').username]",
    "username": "[listCredentials(resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName')), '2021-06-01-preview').username]",
    "passwordSecretRe": "registry-password"
    "passwordSecretRe": "registry-password"
    }}
    }}
    ],
    ],
    "secrets": [
    "secrets": [
    {{
    {{
    "name": "registry-password",
    "name": "registry-password",
    "value": "[listCredentials(resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName')), '2021-06-01-preview').passwords[0].value]"
    "value": "[listCredentials(resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName')), '2021-06-01-preview').passwords[0].value]"
    }}
    }}
    ]
    ]
    }},
    }},
    "template": {{
    "template": {{
    "containers": [
    "containers": [
    {{
    {{
    "name": "[parameters('containerAppName')]",
    "name": "[parameters('containerAppName')]",
    "image": "[variables('imageName')]",
    "image": "[variables('imageName')]",
    "resources": {{
    "resources": {{
    "cpu": {config.cpu_count},
    "cpu": {config.cpu_count},
    "memory": "{config.memory_gb}Gi"
    "memory": "{config.memory_gb}Gi"
    }},
    }},
    "env": [
    "env": [
    {{
    {{
    "name": "MODEL_PATH",
    "name": "MODEL_PATH",
    "value": "{config.model_path}"
    "value": "{config.model_path}"
    }},
    }},
    {{
    {{
    "name": "MODEL_TYPE",
    "name": "MODEL_TYPE",
    "value": "{config.model_type}"
    "value": "{config.model_type}"
    }},
    }},
    {{
    {{
    "name": "SERVER_TYPE",
    "name": "SERVER_TYPE",
    "value": "{config.server_type}"
    "value": "{config.server_type}"
    }},
    }},
    {{
    {{
    "name": "PORT",
    "name": "PORT",
    "value": "{config.port}"
    "value": "{config.port}"
    }}"""
    }}"""


    # Add environment variables
    # Add environment variables
    for i, (key, value) in enumerate(config.env_vars.items()):
    for i, (key, value) in enumerate(config.env_vars.items()):
    if i > 0 or len(config.env_vars) > 0:
    if i > 0 or len(config.env_vars) > 0:
    content += ","
    content += ","
    content += """
    content += """
    {{
    {{
    "name": "{key}",
    "name": "{key}",
    "value": "{value}"
    "value": "{value}"
    }}"""
    }}"""


    # Add scaling configuration
    # Add scaling configuration
    content += """
    content += """
    ]
    ]
    }}
    }}
    ],
    ],
    "scale": {{
    "scale": {{
    "minReplicas": {config.min_instances},
    "minReplicas": {config.min_instances},
    "maxReplicas": {config.max_instances}
    "maxReplicas": {config.max_instances}
    }}
    }}
    }}
    }}
    }},
    }},
    "dependsOn": [
    "dependsOn": [
    "[resourceId('Microsoft.App/managedEnvironments', variables('containerAppEnvironmentName'))]",
    "[resourceId('Microsoft.App/managedEnvironments', variables('containerAppEnvironmentName'))]",
    "[resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName'))]"
    "[resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName'))]"
    ]
    ]
    }}
    }}
    ],
    ],
    "outputs": {{
    "outputs": {{
    "containerAppFqdn": {{
    "containerAppFqdn": {{
    "type": "string",
    "type": "string",
    "value": "[reference(resourceId('Microsoft.App/containerApps', parameters('containerAppName'))).configuration.ingress.fqdn]"
    "value": "[reference(resourceId('Microsoft.App/containerApps', parameters('containerAppName'))).configuration.ingress.fqdn]"
    }}
    }}
    }}
    }}
    }}"""
    }}"""


    # Write ARM template
    # Write ARM template
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_azure_deploy_script(config: CloudConfig, output_path: str) -> None:
    def _generate_azure_deploy_script(config: CloudConfig, output_path: str) -> None:
    """
    """
    Generate an Azure deployment script.
    Generate an Azure deployment script.


    Args:
    Args:
    config: Cloud configuration
    config: Cloud configuration
    output_path: Path to save the deployment script
    output_path: Path to save the deployment script
    """
    """
    # Create deployment script content
    # Create deployment script content
    content = """#!/bin/bash
    content = """#!/bin/bash
    set -e
    set -e


    # Configuration
    # Configuration
    RESOURCE_GROUP="{config.name}-rg"
    RESOURCE_GROUP="{config.name}-rg"
    LOCATION="{config.region}"
    LOCATION="{config.region}"
    REGISTRY_NAME="{config.name}registry"
    REGISTRY_NAME="{config.name}registry"
    CONTAINER_APP_NAME="{config.name}"
    CONTAINER_APP_NAME="{config.name}"
    IMAGE_NAME="{config.name}"
    IMAGE_NAME="{config.name}"


    # Create resource group if it doesn't exist
    # Create resource group if it doesn't exist
    echo "Creating resource group if it doesn't exist..."
    echo "Creating resource group if it doesn't exist..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
    az group create --name $RESOURCE_GROUP --location $LOCATION


    # Build and push Docker image
    # Build and push Docker image
    echo "Building Docker image..."
    echo "Building Docker image..."
    docker build -t $IMAGE_NAME:latest .
    docker build -t $IMAGE_NAME:latest .


    echo "Creating container registry if it doesn't exist..."
    echo "Creating container registry if it doesn't exist..."
    az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true
    az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true


    echo "Logging in to container registry..."
    echo "Logging in to container registry..."
    az acr login --name $REGISTRY_NAME
    az acr login --name $REGISTRY_NAME


    echo "Tagging and pushing Docker image..."
    echo "Tagging and pushing Docker image..."
    docker tag $IMAGE_NAME:latest $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:latest
    docker tag $IMAGE_NAME:latest $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:latest
    docker push $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:latest
    docker push $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:latest


    # Deploy ARM template
    # Deploy ARM template
    echo "Deploying ARM template..."
    echo "Deploying ARM template..."
    az deployment group create \\
    az deployment group create \\
    --resource-group $RESOURCE_GROUP \\
    --resource-group $RESOURCE_GROUP \\
    --template-file azuredeploy.json \\
    --template-file azuredeploy.json \\
    --parameters \\
    --parameters \\
    containerRegistryName=$REGISTRY_NAME \\
    containerRegistryName=$REGISTRY_NAME \\
    containerAppName=$CONTAINER_APP_NAME \\
    containerAppName=$CONTAINER_APP_NAME \\
    location=$LOCATION
    location=$LOCATION


    # Get container app URL
    # Get container app URL
    CONTAINER_APP_URL=$(az deployment group show \\
    CONTAINER_APP_URL=$(az deployment group show \\
    --resource-group $RESOURCE_GROUP \\
    --resource-group $RESOURCE_GROUP \\
    --name azuredeploy \\
    --name azuredeploy \\
    --query properties.outputs.containerAppFqdn.value \\
    --query properties.outputs.containerAppFqdn.value \\
    --output tsv)
    --output tsv)


    echo "Deployment completed successfully!"
    echo "Deployment completed successfully!"
    echo "Container App URL: https://$CONTAINER_APP_URL"
    echo "Container App URL: https://$CONTAINER_APP_URL"
    """
    """


    # Write deployment script
    # Write deployment script
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())


    # Make script executable
    # Make script executable
    os.chmod(output_path, 0o755)
    os.chmod(output_path, 0o755)