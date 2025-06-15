#!/usr/bin/env python3
"""
Final comprehensive fix for consolidated-ci-cd.yml workflow
Addresses all remaining syntax issues and structural problems.
"""

import re
from pathlib import Path
from typing import Optional

import yaml


def fix_consolidated_workflow() -> bool:
    """Fix all remaining issues in consolidated-ci-cd.yml."""
    workflow_file = Path(".github/workflows/consolidated-ci-cd.yml")
    if not workflow_file.exists():
        return False


    # Read the file
    content = workflow_file.read_text(encoding="utf-8")

    # Fix 1: Replace pyrefly with pyright (pyrefly doesn't exist)
    content = re.sub(r"pyrefly", "pyright", content)

    # Fix 2: Remove duplicate and misplaced steps in build-deploy jobs
    # Remove duplicate QEMU/Buildx setups and fix the structure

    # Fix the build-deploy job structure
    build_deploy_pattern = r"(  build-deploy:.*?)(  build-deploy-arm64:)"
    match = re.search(build_deploy_pattern, content, re.DOTALL)

    if match:
        build_deploy_section = match.group(1)

        # Clean up the build-deploy section
        fixed_build_deploy = """  build-deploy:
    name: Build & Deploy
    runs-on: ubuntu-latest
    needs:
    - lint-test
    - security
    - frontend-test
    if: '(github.event_name == ''push'' && (github.ref == ''refs/heads/main'' || github.ref
      == ''refs/heads/dev'' || github.ref == ''refs/heads/master'' || github.ref ==
      ''refs/heads/develop'')) ||
      github.event_name == ''workflow_dispatch'' ||
      startsWith(github.ref, ''refs/tags/v'')
      '
    permissions:
      contents: read
      packages: write
      id-token: write
    outputs:
      docker_tag: ${{ steps.set-docker-tag.outputs.docker_tag }}
      should_push: ${{ steps.set-docker-tag.outputs.should_push }}

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set Docker image tag
      id: set-docker-tag
      run: |
        if [[ "${{ github.ref }}" == refs/tags/v* ]]; then
          echo "docker_tag=${{ secrets.DOCKERHUB_USERNAME }}/paissiveincome-app:${{ github.ref_name }}" >> $GITHUB_OUTPUT
          echo "should_push=true" >> $GITHUB_OUTPUT
        else
          echo "docker_tag=paissiveincome/app:test" >> $GITHUB_OUTPUT
          echo "should_push=false" >> $GITHUB_OUTPUT
        fi

    - name: Set up QEMU
      uses: docker/setup-qemu-action@v3
      with:
        platforms: linux/amd64,linux/arm64

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      with:
        platforms: linux/amd64,linux/arm64
        driver-opts: 'image=moby/buildkit:v0.12.0'

    - name: Log in to Docker Hub
      if: steps.set-docker-tag.outputs.should_push == 'true'
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Prepare build cache
      uses: actions/cache@v4
      with:
        path: /tmp/.buildx-cache
        key: ${{ runner.os }}-buildx-${{ github.sha }}
        restore-keys: '${{ runner.os }}-buildx-'

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: ${{ steps.set-docker-tag.outputs.should_push }}
        tags: ${{ steps.set-docker-tag.outputs.docker_tag }}
        platforms: linux/amd64,linux/arm64
        cache-from: type=local,src=/tmp/.buildx-cache
        cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
        build-args: 'BUILDKIT_INLINE_CACHE=1'
        provenance: mode=max

    - name: Move Docker cache
      run: |
        rm -rf /tmp/.buildx-cache
        mv /tmp/.buildx-cache-new /tmp/.buildx-cache

"""

        content = content.replace(build_deploy_section, fixed_build_deploy)

    # Fix 3: Clean up the build-deploy-arm64 job (remove duplicates and fix structure)
    arm64_pattern = r"(  build-deploy-arm64:.*?)(\n  \w+:|$)"
    match = re.search(arm64_pattern, content, re.DOTALL)

    if match:
        # Simplified ARM64 build job
        fixed_arm64_build = """  build-deploy-arm64:
    name: Build & Deploy (ARM64)
    runs-on: ubuntu-latest
    needs:
    - lint-test
    - security
    - frontend-test
    if: '(github.event_name == ''push'' && (github.ref == ''refs/heads/main'' || github.ref
      == ''refs/heads/dev'' || github.ref == ''refs/heads/master'' || github.ref ==
      ''refs/heads/develop'')) ||
      github.event_name == ''workflow_dispatch'' ||
      startsWith(github.ref, ''refs/tags/v'')
      '
    permissions:
      contents: read
      packages: write
      id-token: write
    timeout-minutes: 30

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set Docker image tag
      id: set-docker-tag
      run: |
        if [[ "${{ github.ref }}" == refs/tags/v* ]]; then
          echo "docker_tag=${{ secrets.DOCKERHUB_USERNAME }}/paissiveincome-app:${{ github.ref_name }}-arm64" >> $GITHUB_OUTPUT
          echo "should_push=true" >> $GITHUB_OUTPUT
        else
          echo "docker_tag=paissiveincome/app:test-arm64" >> $GITHUB_OUTPUT
          echo "should_push=false" >> $GITHUB_OUTPUT
        fi

    - name: Set up QEMU
      uses: docker/setup-qemu-action@v3
      with:
        platforms: linux/arm64

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      with:
        platforms: linux/arm64
        driver-opts: 'image=moby/buildkit:v0.12.0'

    - name: Log in to Docker Hub
      if: steps.set-docker-tag.outputs.should_push == 'true'
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Prepare build cache
      uses: actions/cache@v4
      with:
        path: /tmp/.buildx-cache-arm64
        key: ${{ runner.os }}-buildx-arm64-${{ github.sha }}
        restore-keys: '${{ runner.os }}-buildx-arm64-'

    - name: Build and push Docker image (ARM64)
      uses: docker/build-push-action@v5
      with:
        context: .
        push: ${{ steps.set-docker-tag.outputs.should_push }}
        tags: ${{ steps.set-docker-tag.outputs.docker_tag }}
        platforms: linux/arm64
        cache-from: type=local,src=/tmp/.buildx-cache-arm64
        cache-to: type=local,dest=/tmp/.buildx-cache-arm64-new,mode=max
        build-args: 'BUILDKIT_INLINE_CACHE=1'
        provenance: mode=max

    - name: Move Docker cache
      run: |
        rm -rf /tmp/.buildx-cache-arm64
        mv /tmp/.buildx-cache-arm64-new /tmp/.buildx-cache-arm64

"""

        # Replace the entire ARM64 section
        content = re.sub(arm64_pattern, fixed_arm64_build + "\n", content, flags=re.DOTALL)

    # Fix 4: Remove any stray quotes and malformed multiline strings
    content = re.sub(r'\n\s*"\s*\n', "\n", content)

    # Fix 5: Fix any remaining malformed run commands
    content = re.sub(r'(\s+run:\s*\|[^\n]*\n(?:\s+[^\n]*\n)*)\s*"\s*\n', r"\1", content)

    # Write the fixed content
    workflow_file.write_text(content, encoding="utf-8")

    return True

def validate_workflow() -> Optional[bool]:
    """Validate the fixed workflow."""
    try:
        with open(".github/workflows/consolidated-ci-cd.yml", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True
    except yaml.YAMLError:
        return False
    except Exception:
        return False

def main() -> None:

    if fix_consolidated_workflow():
        if validate_workflow():
            pass
        else:
            pass
    else:
        pass

if __name__ == "__main__":
    main()
