#!/bin/bash
# Script to validate file paths to prevent command injection
# Usage: validate_file_path.sh <file_path> [<default_path>]
# Returns the validated path or the default path if validation fails

# Function to validate a file path
validate_file_path() {
  local file_path="$1"
  local default_path="${2:-}"

  # Remove newlines and other control characters
  local clean_path=$(echo "$file_path" | tr -d '\n' | sed 's/[^a-zA-Z0-9_\.\/-]//g')

  # Validate path - only allow alphanumeric characters, underscores, dots, dashes, and slashes
  if [[ "$clean_path" =~ ^[a-zA-Z0-9_\.\/-]+$ ]]; then
    # Path is valid, check if it exists (if not empty)
    if [ -n "$clean_path" ] && [ ! -e "$clean_path" ]; then
      echo "Warning: Path '$clean_path' does not exist." >&2
      # Still return the path if it's syntactically valid
      echo "$clean_path"
    else
      # Path exists or is empty, return it
      echo "$clean_path"
    fi
  else
    # Invalid path, use default
    echo "Warning: Invalid path provided. Using default path instead." >&2
    echo "$default_path"
  fi
}

# Main script execution
if [ $# -lt 1 ]; then
  echo "Usage: $0 <file_path> [<default_path>]" >&2
  exit 1
fi

validate_file_path "$1" "${2:-}"
