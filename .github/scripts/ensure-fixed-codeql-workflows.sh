#!/bin/bash
# Script to ensure fixed versions of CodeQL workflow files are used

# Define the workflow files
CODEQL_WORKFLOW=".github/workflows/codeql.yml"
CODEQL_WINDOWS_WORKFLOW=".github/workflows/codeql-windows.yml"
CODEQL_MACOS_WORKFLOW=".github/workflows/codeql-macos.yml"
CODEQL_UBUNTU_WORKFLOW=".github/workflows/codeql-ubuntu.yml"

# Define the fixed workflow files
CODEQL_FIXED_WORKFLOW=".github/workflows/codeql-fixed.yml"
CODEQL_WINDOWS_FIXED_WORKFLOW=".github/workflows/codeql-windows-fixed.yml"
CODEQL_MACOS_FIXED_WORKFLOW=".github/workflows/codeql-macos-fixed.yml"
CODEQL_UBUNTU_FIXED_WORKFLOW=".github/workflows/codeql-ubuntu-fixed.yml"

# Function to log messages
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check and replace a workflow file with its fixed version
replace_workflow() {
  local original_file="$1"
  local fixed_file="$2"
  local description="$3"

  if [ -f "$fixed_file" ]; then
    log "Fixed $description workflow file exists: $fixed_file"
    
    if [ -f "$original_file" ]; then
      log "Replacing $original_file with $fixed_file"
      cp "$fixed_file" "$original_file"
      log "Successfully replaced $description workflow file"
    else
      log "Original $description workflow file does not exist: $original_file"
      log "Creating $original_file from $fixed_file"
      cp "$fixed_file" "$original_file"
      log "Successfully created $description workflow file"
    fi
  else
    log "Fixed $description workflow file does not exist: $fixed_file"
    log "Cannot replace $description workflow file"
  fi
}

# Main script
log "Starting workflow file replacement..."

# Replace the workflow files
replace_workflow "$CODEQL_WORKFLOW" "$CODEQL_FIXED_WORKFLOW" "CodeQL"
replace_workflow "$CODEQL_WINDOWS_WORKFLOW" "$CODEQL_WINDOWS_FIXED_WORKFLOW" "CodeQL Windows"
replace_workflow "$CODEQL_MACOS_WORKFLOW" "$CODEQL_MACOS_FIXED_WORKFLOW" "CodeQL macOS"
replace_workflow "$CODEQL_UBUNTU_WORKFLOW" "$CODEQL_UBUNTU_FIXED_WORKFLOW" "CodeQL Ubuntu"

log "Workflow file replacement completed"
