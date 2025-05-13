# Deployment Guide

This document provides detailed instructions for deploying the pAIssive Income application using the GitHub Actions CI/CD pipeline.

## Overview

The deployment process is fully automated using GitHub Actions workflows. The process consists of the following steps:

1. Code is pushed to the repository
2. CI/CD pipeline runs tests and builds the application
3. If tests pass, a Docker image is built
4. The Docker image is pushed to DockerHub
5. The application is deployed to the appropriate environment (development or production)

## GitHub Actions Workflows

The deployment process uses the following GitHub Actions workflow files:

- `.github/workflows/ci-cd.yml`: Handles code linting, testing, and building the Docker image
- `.github/workflows/deploy.yml`: Handles deploying the application to development and production environments
- `.github/workflows/security-scan.yml`: Performs security scanning of the codebase

## Required Secrets

To use the deployment workflows, you need to set up the following secrets in your GitHub repository:

### DockerHub Secrets

- `DOCKERHUB_USERNAME`: Your DockerHub username
- `DOCKERHUB_TOKEN`: Your DockerHub access token (not your password)

These secrets are used for:

- Pushing Docker images to DockerHub during deployment
- Authenticating with DockerHub during Docker Compose integration tests to avoid rate limits
- Pulling Docker images in CI/CD workflows

### Development Environment Secrets

- `DEV_HOST`: The hostname or IP address of your development server
- `DEV_USER`: The SSH username for your development server
- `DEV_SSH_KEY`: The SSH private key for accessing your development server

### Production Environment Secrets

- `PROD_HOST`: The hostname or IP address of your production server
- `PROD_USER`: The SSH username for your production server
- `PROD_SSH_KEY`: The SSH private key for accessing your production server

## Setting Up Secrets

To set up secrets in your GitHub repository:

1. Go to your repository on GitHub
2. Click on "Settings"
3. Click on "Secrets and variables" in the left sidebar
4. Click on "Actions"
5. Click on "New repository secret"
6. Enter the name and value of the secret
7. Click on "Add secret"

## Deployment Process

### Automatic Deployment

The deployment process is triggered automatically when code is pushed to the `main` or `dev` branches:

- Pushing to the `dev` branch deploys to the development environment
- Pushing to the `main` branch deploys to the production environment

### Manual Deployment

You can also trigger the deployment process manually:

1. Go to your repository on GitHub
2. Click on "Actions"
3. Click on "Deploy" in the left sidebar
4. Click on "Run workflow"
5. Select the branch you want to deploy
6. Click on "Run workflow"

## Server Setup

The deployment process assumes that your servers are set up with Docker and Docker Compose. The following files should be present on your servers:

- `~/paissive-income/docker-compose.yml`: The Docker Compose file for running the application

### Example docker-compose.yml

```yaml
services:
  app:
    image: paissiveincome/app:latest
    container_name: paissive_income_app
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - PASSWORD_RESET_SECRET_KEY=${PASSWORD_RESET_SECRET_KEY}
      - REFRESH_TOKEN_SECRET_KEY=${REFRESH_TOKEN_SECRET_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

## Environment Variables

The application uses the following environment variables:

- `FLASK_ENV`: The environment to run the application in (`development` or `production`)
- `JWT_SECRET_KEY`: The secret key for JWT token generation
- `PASSWORD_RESET_SECRET_KEY`: The secret key for password reset token generation
- `REFRESH_TOKEN_SECRET_KEY`: The secret key for refresh token generation

These environment variables should be set on your servers. You can set them in a `.env` file in the same directory as your `docker-compose.yml` file.

## Troubleshooting

### Deployment Fails

If the deployment fails, check the following:

1. Make sure all required secrets are set up correctly
2. Check the GitHub Actions logs for error messages
3. Make sure your servers are accessible via SSH
4. Make sure Docker and Docker Compose are installed on your servers
5. Make sure the `docker-compose.yml` file exists on your servers

### Application Fails to Start

If the application fails to start after deployment, check the following:

1. Check the Docker logs: `docker logs paissive_income_app`
2. Make sure all required environment variables are set
3. Check the application logs for error messages

## Monitoring

After deployment, you can monitor the application using the following methods:

1. Check the application logs: `docker logs paissive_income_app`
2. Check the application status: `docker ps`
3. Check the application health: `docker inspect --format='{{json .State.Health}}' paissive_income_app`

## Rollback

If you need to rollback to a previous version of the application, you can use the following steps:

1. Find the tag of the previous version: `docker images paissiveincome/app`
2. Update the `docker-compose.yml` file to use the previous version
3. Restart the application: `docker-compose -f ~/paissive-income/docker-compose.yml down && docker-compose -f ~/paissive-income/docker-compose.yml up -d`

## Conclusion

This deployment guide provides all the information you need to deploy the pAIssive Income application using the GitHub Actions CI/CD pipeline. If you have any questions or issues, please contact the development team.
