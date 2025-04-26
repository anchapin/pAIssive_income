"""
Cloud deployment utilities for AI models.

This module provides utilities for deploying AI models to cloud platforms.
"""

import os
import enum
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CloudProvider(enum.Enum):
    """
    Enumeration of cloud providers.
    """
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


@dataclass
class CloudConfig:
    """
    Configuration for cloud deployment.
    """
    # Basic configuration
    provider: CloudProvider
    name: str
    region: str
    
    # Server configuration
    server_type: str = "rest"  # "rest" or "grpc"
    port: int = 8000
    
    # Model configuration
    model_path: str = ""
    model_type: str = "text-generation"
    model_id: str = ""
    
    # Resource configuration
    instance_type: str = ""
    cpu_count: int = 2
    memory_gb: int = 8
    gpu_type: Optional[str] = None
    gpu_count: int = 0
    
    # Scaling configuration
    min_instances: int = 1
    max_instances: int = 1
    
    # Network configuration
    vpc_id: Optional[str] = None
    subnet_ids: List[str] = field(default_factory=list)
    security_group_ids: List[str] = field(default_factory=list)
    
    # Storage configuration
    storage_size_gb: int = 20
    storage_type: str = "ssd"
    
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Authentication configuration
    auth_enabled: bool = False
    auth_type: str = "api_key"  # "api_key", "oauth", "iam"
    
    # Additional configuration
    additional_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "provider": self.provider.value,
            "name": self.name,
            "region": self.region,
            "server_type": self.server_type,
            "port": self.port,
            "model_path": self.model_path,
            "model_type": self.model_type,
            "model_id": self.model_id,
            "instance_type": self.instance_type,
            "cpu_count": self.cpu_count,
            "memory_gb": self.memory_gb,
            "gpu_type": self.gpu_type,
            "gpu_count": self.gpu_count,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "vpc_id": self.vpc_id,
            "subnet_ids": self.subnet_ids,
            "security_group_ids": self.security_group_ids,
            "storage_size_gb": self.storage_size_gb,
            "storage_type": self.storage_type,
            "env_vars": self.env_vars,
            "auth_enabled": self.auth_enabled,
            "auth_type": self.auth_type,
            **self.additional_params
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'CloudConfig':
        """
        Create a configuration from a dictionary.
        
        Args:
            config_dict: Dictionary with configuration parameters
            
        Returns:
            Cloud configuration
        """
        # Extract provider
        provider_str = config_dict.pop("provider", "aws")
        try:
            provider = CloudProvider(provider_str)
        except ValueError:
            provider = CloudProvider.AWS
        
        # Extract additional parameters
        additional_params = {}
        for key, value in list(config_dict.items()):
            if key not in cls.__annotations__:
                additional_params[key] = config_dict.pop(key)
        
        # Create configuration
        config = cls(
            provider=provider,
            **config_dict
        )
        
        config.additional_params = additional_params
        return config


def generate_cloud_config(
    config: CloudConfig,
    output_dir: str
) -> str:
    """
    Generate cloud deployment configuration files.
    
    Args:
        config: Cloud configuration
        output_dir: Directory to save the configuration files
        
    Returns:
        Path to the generated configuration file
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate configuration based on provider
    if config.provider == CloudProvider.AWS:
        return _generate_aws_config(config, output_dir)
    elif config.provider == CloudProvider.GCP:
        return _generate_gcp_config(config, output_dir)
    elif config.provider == CloudProvider.AZURE:
        return _generate_azure_config(config, output_dir)
    else:
        raise ValueError(f"Unsupported cloud provider: {config.provider}")


def _generate_aws_config(config: CloudConfig, output_dir: str) -> str:
    """
    Generate AWS deployment configuration files.
    
    Args:
        config: Cloud configuration
        output_dir: Directory to save the configuration files
        
    Returns:
        Path to the generated configuration file
    """
    # Generate CloudFormation template
    template_path = os.path.join(output_dir, "cloudformation.yaml")
    _generate_cloudformation_template(config, template_path)
    
    # Generate deployment script
    script_path = os.path.join(output_dir, "deploy.sh")
    _generate_aws_deploy_script(config, script_path)
    
    logger.info(f"AWS configuration files generated in {output_dir}")
    
    return template_path


def _generate_gcp_config(config: CloudConfig, output_dir: str) -> str:
    """
    Generate GCP deployment configuration files.
    
    Args:
        config: Cloud configuration
        output_dir: Directory to save the configuration files
        
    Returns:
        Path to the generated configuration file
    """
    # Generate Terraform configuration
    terraform_path = os.path.join(output_dir, "main.tf")
    _generate_gcp_terraform(config, terraform_path)
    
    # Generate deployment script
    script_path = os.path.join(output_dir, "deploy.sh")
    _generate_gcp_deploy_script(config, script_path)
    
    logger.info(f"GCP configuration files generated in {output_dir}")
    
    return terraform_path


def _generate_azure_config(config: CloudConfig, output_dir: str) -> str:
    """
    Generate Azure deployment configuration files.
    
    Args:
        config: Cloud configuration
        output_dir: Directory to save the configuration files
        
    Returns:
        Path to the generated configuration file
    """
    # Generate ARM template
    template_path = os.path.join(output_dir, "azuredeploy.json")
    _generate_arm_template(config, template_path)
    
    # Generate deployment script
    script_path = os.path.join(output_dir, "deploy.sh")
    _generate_azure_deploy_script(config, script_path)
    
    logger.info(f"Azure configuration files generated in {output_dir}")
    
    return template_path


def _generate_cloudformation_template(config: CloudConfig, output_path: str) -> None:
    """
    Generate an AWS CloudFormation template.
    
    Args:
        config: Cloud configuration
        output_path: Path to save the CloudFormation template
    """
    # Create CloudFormation template content
    content = f"""
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AI Model Deployment'

Parameters:
  ModelName:
    Type: String
    Default: {config.name}
    Description: Name of the model deployment
  
  ModelPath:
    Type: String
    Default: {config.model_path}
    Description: Path to the model
  
  ModelType:
    Type: String
    Default: {config.model_type}
    Description: Type of the model
  
  ServerType:
    Type: String
    Default: {config.server_type}
    Description: Type of the server (rest or grpc)
  
  Port:
    Type: Number
    Default: {config.port}
    Description: Port for the server
  
  InstanceType:
    Type: String
    Default: {config.instance_type or "ml.m5.large"}
    Description: Instance type for the deployment
  
  MinInstances:
    Type: Number
    Default: {config.min_instances}
    Description: Minimum number of instances
  
  MaxInstances:
    Type: Number
    Default: {config.max_instances}
    Description: Maximum number of instances

Resources:
  ModelRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: sagemaker.amazonaws.com
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
        - 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'

  ModelEndpoint:
    Type: AWS::SageMaker::Endpoint
    Properties:
      EndpointName: !Ref ModelName
      EndpointConfigName: !GetAtt ModelEndpointConfig.EndpointConfigName

  ModelEndpointConfig:
    Type: AWS::SageMaker::EndpointConfig
    Properties:
      ProductionVariants:
        - InitialInstanceCount: !Ref MinInstances
          InstanceType: !Ref InstanceType
          ModelName: !GetAtt Model.ModelName
          VariantName: AllTraffic
          InitialVariantWeight: 1.0

  Model:
    Type: AWS::SageMaker::Model
    Properties:
      ModelName: !Ref ModelName
      ExecutionRoleArn: !GetAtt ModelRole.Arn
      PrimaryContainer:
        Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/${ModelName}:latest'
        Environment:
          MODEL_PATH: !Ref ModelPath
          MODEL_TYPE: !Ref ModelType
          SERVER_TYPE: !Ref ServerType
          PORT: !Ref Port
"""
    
    # Add environment variables
    for key, value in config.env_vars.items():
        content += f"          {key}: {value}\n"
    
    # Add outputs
    content += """
Outputs:
  EndpointName:
    Description: Name of the SageMaker endpoint
    Value: !Ref ModelEndpoint
  
  EndpointUrl:
    Description: URL of the SageMaker endpoint
    Value: !Sub 'https://runtime.sagemaker.${AWS::Region}.amazonaws.com/endpoints/${ModelEndpoint}'
"""
    
    # Write CloudFormation template
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())


def _generate_aws_deploy_script(config: CloudConfig, output_path: str) -> None:
    """
    Generate an AWS deployment script.
    
    Args:
        config: Cloud configuration
        output_path: Path to save the deployment script
    """
    # Create deployment script content
    content = f"""#!/bin/bash
set -e

# Configuration
STACK_NAME="{config.name}"
REGION="{config.region}"
MODEL_NAME="{config.name}"
ECR_REPOSITORY="{config.name}"

# Build and push Docker image
echo "Building Docker image..."
docker build -t $ECR_REPOSITORY:latest .

echo "Logging in to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "Creating ECR repository if it doesn't exist..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $REGION || aws ecr create-repository --repository-name $ECR_REPOSITORY --region $REGION

echo "Pushing Docker image to ECR..."
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:latest

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \\
  --template-file cloudformation.yaml \\
  --stack-name $STACK_NAME \\
  --capabilities CAPABILITY_IAM \\
  --region $REGION \\
  --parameter-overrides \\
    ModelName=$MODEL_NAME \\
    ModelPath="{config.model_path}" \\
    ModelType="{config.model_type}" \\
    ServerType="{config.server_type}" \\
    Port={config.port} \\
    InstanceType="{config.instance_type or "ml.m5.large"}" \\
    MinInstances={config.min_instances} \\
    MaxInstances={config.max_instances}

echo "Deployment completed successfully!"
echo "Endpoint URL: https://runtime.sagemaker.$REGION.amazonaws.com/endpoints/$MODEL_NAME"
"""
    
    # Write deployment script
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    # Make script executable
    os.chmod(output_path, 0o755)


def _generate_gcp_terraform(config: CloudConfig, output_path: str) -> None:
    """
    Generate a GCP Terraform configuration.
    
    Args:
        config: Cloud configuration
        output_path: Path to save the Terraform configuration
    """
    # Create Terraform configuration content
    content = f"""
provider "google" {{
  project = var.project_id
  region  = "{config.region}"
}}

variable "project_id" {{
  description = "GCP Project ID"
  type        = string
}}

resource "google_artifact_registry_repository" "model_repository" {{
  location      = "{config.region}"
  repository_id = "{config.name}"
  format        = "DOCKER"
}}

resource "google_cloud_run_service" "model_service" {{
  name     = "{config.name}"
  location = "{config.region}"

  template {{
    spec {{
      containers {{
        image = "${{google_artifact_registry_repository.model_repository.location}}-docker.pkg.dev/${{var.project_id}}/${{google_artifact_registry_repository.model_repository.repository_id}}/{config.name}:latest"
        
        resources {{
          limits = {{
            cpu    = "{config.cpu_count}"
            memory = "{config.memory_gb}Gi"
          }}
        }}
        
        ports {{
          container_port = {config.port}
        }}
        
        env {{
          name  = "MODEL_PATH"
          value = "{config.model_path}"
        }}
        
        env {{
          name  = "MODEL_TYPE"
          value = "{config.model_type}"
        }}
        
        env {{
          name  = "SERVER_TYPE"
          value = "{config.server_type}"
        }}
        
        env {{
          name  = "PORT"
          value = "{config.port}"
        }}
"""
    
    # Add environment variables
    for key, value in config.env_vars.items():
        content += f"""
        env {{
          name  = "{key}"
          value = "{value}"
        }}"""
    
    # Add GPU configuration if needed
    if config.gpu_count > 0 and config.gpu_type:
        content += f"""
        
        # GPU configuration
        resources {{
          limits {{
            "nvidia.com/gpu" = {config.gpu_count}
          }}
        }}"""
    
    # Add scaling configuration
    content += f"""
      }}
      
      container_concurrency = 80
      timeout_seconds       = 300
    }}
    
    metadata {{
      annotations = {{
        "autoscaling.knative.dev/minScale" = "{config.min_instances}"
        "autoscaling.knative.dev/maxScale" = "{config.max_instances}"
      }}
    }}
  }}
  
  traffic {{
    percent         = 100
    latest_revision = true
  }}
}}

resource "google_cloud_run_service_iam_member" "public_access" {{
  service  = google_cloud_run_service.model_service.name
  location = google_cloud_run_service.model_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}}

output "service_url" {{
  value = google_cloud_run_service.model_service.status[0].url
}}
"""
    
    # Write Terraform configuration
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())


def _generate_gcp_deploy_script(config: CloudConfig, output_path: str) -> None:
    """
    Generate a GCP deployment script.
    
    Args:
        config: Cloud configuration
        output_path: Path to save the deployment script
    """
    # Create deployment script content
    content = f"""#!/bin/bash
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="{config.region}"
REPOSITORY="{config.name}"
IMAGE="{config.name}"

# Build and push Docker image
echo "Building Docker image..."
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest .

echo "Configuring Docker for Artifact Registry..."
gcloud auth configure-docker $REGION-docker.pkg.dev

echo "Creating Artifact Registry repository if it doesn't exist..."
gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION --description="Repository for $IMAGE" || true

echo "Pushing Docker image to Artifact Registry..."
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Apply Terraform configuration
echo "Applying Terraform configuration..."
terraform apply -var="project_id=$PROJECT_ID" -auto-approve

# Get service URL
SERVICE_URL=$(terraform output -raw service_url)

echo "Deployment completed successfully!"
echo "Service URL: $SERVICE_URL"
"""
    
    # Write deployment script
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    # Make script executable
    os.chmod(output_path, 0o755)


def _generate_arm_template(config: CloudConfig, output_path: str) -> None:
    """
    Generate an Azure ARM template.
    
    Args:
        config: Cloud configuration
        output_path: Path to save the ARM template
    """
    # Create ARM template content
    content = f"""{{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {{
    "containerRegistryName": {{
      "type": "string",
      "defaultValue": "{config.name}registry",
      "metadata": {{
        "description": "Name of the container registry"
      }}
    }},
    "containerAppName": {{
      "type": "string",
      "defaultValue": "{config.name}",
      "metadata": {{
        "description": "Name of the container app"
      }}
    }},
    "location": {{
      "type": "string",
      "defaultValue": "{config.region}",
      "metadata": {{
        "description": "Location for all resources"
      }}
    }}
  }},
  "variables": {{
    "containerAppEnvironmentName": "[concat(parameters('containerAppName'), '-env')]",
    "logAnalyticsWorkspaceName": "[concat(parameters('containerAppName'), '-logs')]",
    "imageName": "[concat(parameters('containerRegistryName'), '.azurecr.io/', parameters('containerAppName'), ':latest')]"
  }},
  "resources": [
    {{
      "type": "Microsoft.ContainerRegistry/registries",
      "apiVersion": "2021-06-01-preview",
      "name": "[parameters('containerRegistryName')]",
      "location": "[parameters('location')]",
      "sku": {{
        "name": "Basic"
      }},
      "properties": {{
        "adminUserEnabled": true
      }}
    }},
    {{
      "type": "Microsoft.OperationalInsights/workspaces",
      "apiVersion": "2021-06-01",
      "name": "[variables('logAnalyticsWorkspaceName')]",
      "location": "[parameters('location')]",
      "properties": {{
        "retentionInDays": 30,
        "features": {{
          "enableLogAccessUsingOnlyResourcePermissions": true
        }},
        "sku": {{
          "name": "PerGB2018"
        }}
      }}
    }},
    {{
      "type": "Microsoft.App/managedEnvironments",
      "apiVersion": "2022-03-01",
      "name": "[variables('containerAppEnvironmentName')]",
      "location": "[parameters('location')]",
      "properties": {{
        "appLogsConfiguration": {{
          "destination": "log-analytics",
          "logAnalyticsConfiguration": {{
            "customerId": "[reference(resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName'))).customerId]",
            "sharedKey": "[listKeys(resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName')), '2021-06-01').primarySharedKey]"
          }}
        }}
      }},
      "dependsOn": [
        "[resourceId('Microsoft.OperationalInsights/workspaces', variables('logAnalyticsWorkspaceName'))]"
      ]
    }},
    {{
      "type": "Microsoft.App/containerApps",
      "apiVersion": "2022-03-01",
      "name": "[parameters('containerAppName')]",
      "location": "[parameters('location')]",
      "properties": {{
        "managedEnvironmentId": "[resourceId('Microsoft.App/managedEnvironments', variables('containerAppEnvironmentName'))]",
        "configuration": {{
          "ingress": {{
            "external": true,
            "targetPort": {config.port},
            "allowInsecure": false,
            "traffic": [
              {{
                "latestRevision": true,
                "weight": 100
              }}
            ]
          }},
          "registries": [
            {{
              "server": "[concat(parameters('containerRegistryName'), '.azurecr.io')]",
              "username": "[listCredentials(resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName')), '2021-06-01-preview').username]",
              "passwordSecretRef": "registry-password"
            }}
          ],
          "secrets": [
            {{
              "name": "registry-password",
              "value": "[listCredentials(resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName')), '2021-06-01-preview').passwords[0].value]"
            }}
          ]
        }},
        "template": {{
          "containers": [
            {{
              "name": "[parameters('containerAppName')]",
              "image": "[variables('imageName')]",
              "resources": {{
                "cpu": {config.cpu_count},
                "memory": "{config.memory_gb}Gi"
              }},
              "env": [
                {{
                  "name": "MODEL_PATH",
                  "value": "{config.model_path}"
                }},
                {{
                  "name": "MODEL_TYPE",
                  "value": "{config.model_type}"
                }},
                {{
                  "name": "SERVER_TYPE",
                  "value": "{config.server_type}"
                }},
                {{
                  "name": "PORT",
                  "value": "{config.port}"
                }}"""
    
    # Add environment variables
    for i, (key, value) in enumerate(config.env_vars.items()):
        if i > 0 or len(config.env_vars) > 0:
            content += ","
        content += f"""
                {{
                  "name": "{key}",
                  "value": "{value}"
                }}"""
    
    # Add scaling configuration
    content += f"""
              ]
            }}
          ],
          "scale": {{
            "minReplicas": {config.min_instances},
            "maxReplicas": {config.max_instances}
          }}
        }}
      }},
      "dependsOn": [
        "[resourceId('Microsoft.App/managedEnvironments', variables('containerAppEnvironmentName'))]",
        "[resourceId('Microsoft.ContainerRegistry/registries', parameters('containerRegistryName'))]"
      ]
    }}
  ],
  "outputs": {{
    "containerAppFqdn": {{
      "type": "string",
      "value": "[reference(resourceId('Microsoft.App/containerApps', parameters('containerAppName'))).configuration.ingress.fqdn]"
    }}
  }}
}}"""
    
    # Write ARM template
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())


def _generate_azure_deploy_script(config: CloudConfig, output_path: str) -> None:
    """
    Generate an Azure deployment script.
    
    Args:
        config: Cloud configuration
        output_path: Path to save the deployment script
    """
    # Create deployment script content
    content = f"""#!/bin/bash
set -e

# Configuration
RESOURCE_GROUP="{config.name}-rg"
LOCATION="{config.region}"
REGISTRY_NAME="{config.name}registry"
CONTAINER_APP_NAME="{config.name}"
IMAGE_NAME="{config.name}"

# Create resource group if it doesn't exist
echo "Creating resource group if it doesn't exist..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Build and push Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:latest .

echo "Creating container registry if it doesn't exist..."
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true

echo "Logging in to container registry..."
az acr login --name $REGISTRY_NAME

echo "Tagging and pushing Docker image..."
docker tag $IMAGE_NAME:latest $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:latest
docker push $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:latest

# Deploy ARM template
echo "Deploying ARM template..."
az deployment group create \\
  --resource-group $RESOURCE_GROUP \\
  --template-file azuredeploy.json \\
  --parameters \\
    containerRegistryName=$REGISTRY_NAME \\
    containerAppName=$CONTAINER_APP_NAME \\
    location=$LOCATION

# Get container app URL
CONTAINER_APP_URL=$(az deployment group show \\
  --resource-group $RESOURCE_GROUP \\
  --name azuredeploy \\
  --query properties.outputs.containerAppFqdn.value \\
  --output tsv)

echo "Deployment completed successfully!"
echo "Container App URL: https://$CONTAINER_APP_URL"
"""
    
    # Write deployment script
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    # Make script executable
    os.chmod(output_path, 0o755)
