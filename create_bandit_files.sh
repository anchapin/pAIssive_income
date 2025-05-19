#!/bin/bash
# Create Bandit configuration files for GitHub Actions workflows

# Create directories
mkdir -p .github/bandit
mkdir -p security-reports

echo "Created directories: .github/bandit, security-reports"

# Create template file
cat > .github/bandit/bandit-config-template.yaml << 'EOF'
# Bandit Configuration Template
# This configuration is used by GitHub Advanced Security for Bandit scanning

# Exclude directories from security scans
exclude_dirs:
  - tests
  - venv
  - .venv
  - env
  - .env
  - __pycache__
  - custom_stubs
  - node_modules
  - build
  - dist
  - docs
  - docs_source
  - junit
  - bin
  - dev_tools
  - scripts
  - tool_templates

# Skip specific test IDs
skips:
  # B101: Use of assert detected
  - B101
  # B311: Standard pseudo-random generators are not suitable for security/cryptographic purposes
  - B311

# Set the output format for GitHub Advanced Security
output_format: sarif

# Output file for GitHub Advanced Security
output_file: security-reports/bandit-results.sarif

# Set the severity level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
severity: MEDIUM

# Set the confidence level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
confidence: MEDIUM

# Simplified shell configuration
shell_injection:
  no_shell: []
  shell: []
EOF

echo "Created template file: .github/bandit/bandit-config-template.yaml"

# Create platform-specific files
for platform in windows linux macos; do
  # Regular config
  cp .github/bandit/bandit-config-template.yaml .github/bandit/bandit-config-${platform}.yaml
  echo "Created configuration file: .github/bandit/bandit-config-${platform}.yaml"

  # Test run ID config
  cp .github/bandit/bandit-config-template.yaml .github/bandit/bandit-config-${platform}-test_run_id.yaml
  echo "Created test run ID configuration file: .github/bandit/bandit-config-${platform}-test_run_id.yaml"
done

# Create empty SARIF file
cat > empty-sarif.json << 'EOF'
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Bandit",
          "informationUri": "https://github.com/PyCQA/bandit",
          "version": "1.7.5",
          "rules": []
        }
      },
      "results": []
    }
  ]
}
EOF

echo "Created empty SARIF file: empty-sarif.json"
echo "Successfully created all Bandit configuration files"
