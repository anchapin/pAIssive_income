#!/usr/bin/env pwsh
# Script to ensure all required CodeQL configuration files exist

# Define the configuration files
$windowsConfigFile = ".github/codeql/security-os-windows.yml"
$ubuntuConfigFile = ".github/codeql/security-os-ubuntu.yml"
$macosConfigFile = ".github/codeql/security-os-macos.yml"
$unifiedConfigFile = ".github/codeql/security-os-config.yml"

# Ensure the directory exists
New-Item -ItemType Directory -Force -Path ".github/codeql" | Out-Null
Write-Host "Ensuring .github/codeql directory exists"

# Windows configuration content
$windowsConfigContent = @"
name: "CodeQL Configuration for Windows"

# This configuration file customizes the CodeQL analysis for Windows
# It inherits settings from the unified configuration and adds Windows-specific settings

# Inherit from the unified configuration
extends: security-os-config.yml

# Windows-specific settings
os: windows-latest

# Additional Windows-specific paths to exclude
paths-ignore:
  # Windows specific files
  - '**/*.exe'
  - '**/*.dll'
  - '**/*.obj'
  - '**/*.pdb'
  - '**/*.lib'
  - '**/*.exp'
  - '**/*.ilk'
  - '**/*.res'
  - '**/*.pch'
  - '**/*.idb'
  - '**/*.manifest'
  - '**/*.msi'
  - '**/*.msm'
  - '**/*.msp'
  - '**/*.lnk'
  - '**/Thumbs.db'
  - '**/ehthumbs.db'
  - '**/Desktop.ini'
  - '**/System Volume Information/**'
  - '**/NTUSER.DAT*'
  - '**/ntuser.dat*'
  - '**/ntuser.ini'
  - '**/pagefile.sys'
  - '**/hiberfil.sys'
  - '**/swapfile.sys'

# Query filters
queries:
  # Include the standard security and quality queries
  - uses: security-and-quality

  # Include additional security queries
  - uses: security-extended

  # Use standard security queries
  - uses: security

# Disable noisy alerts
disable-default-queries: false

# Query suite definitions
query-filters:
  - exclude:
      tags contain: test
  - exclude:
      tags contain: maintainability
      precision below: high

# Trap errors during extraction
trap-for-errors: true
"@

# Ubuntu configuration content
$ubuntuConfigContent = @"
name: "CodeQL Configuration for Ubuntu"

# This configuration file customizes the CodeQL analysis for Ubuntu
# It inherits settings from the unified configuration and adds Ubuntu-specific settings

# Inherit from the unified configuration
extends: security-os-config.yml

# Ubuntu-specific settings
os: ubuntu-latest

# Additional Ubuntu-specific paths to exclude
paths-ignore:
  # Linux specific files
  - '**/lost+found/**'
  - '**/proc/**'
  - '**/sys/**'
  - '**/var/tmp/**'
  - '**/tmp/**'
  - '**/.bash_history'
  - '**/.bashrc'
  - '**/.profile'
  - '**/.ssh/**'
  - '**/core.*'
  - '**/*.so'
  - '**/*.o'

# Query filters
queries:
  # Include the standard security and quality queries
  - uses: security-and-quality

  # Include additional security queries
  - uses: security-extended

  # Use standard security queries
  - uses: security

# Disable noisy alerts
disable-default-queries: false

# Query suite definitions
query-filters:
  - exclude:
      tags contain: test
  - exclude:
      tags contain: maintainability
      precision below: high

# Trap errors during extraction
trap-for-errors: true
"@

# macOS configuration content
$macosConfigContent = @"
name: "CodeQL Configuration for macOS"

# This configuration file customizes the CodeQL analysis for macOS
# It inherits settings from the unified configuration and adds macOS-specific settings

# Inherit from the unified configuration
extends: security-os-config.yml

# macOS-specific settings
os: macos-latest

# Additional macOS-specific paths to exclude
paths-ignore:
  # macOS specific files
  - '**/.DS_Store'
  - '**/.AppleDouble'
  - '**/.LSOverride'
  # Using '?' instead of '\r' to avoid backslash issues in CodeQL filters
  - '**/Icon?'
  - '**/*.app/**'
  - '**/*.pkg'
  - '**/*.dmg'
  - '**/._*'
  - '**/.Spotlight-V100/**'
  - '**/.Trashes/**'
  - '**/ehthumbs.db'
  - '**/Thumbs.db'

# Query filters
queries:
  # Include the standard security and quality queries
  - uses: security-and-quality

  # Include additional security queries
  - uses: security-extended

  # Use standard security queries
  - uses: security

# Disable noisy alerts
disable-default-queries: false

# Query suite definitions
query-filters:
  - exclude:
      tags contain: test
  - exclude:
      tags contain: maintainability
      precision below: high

# Trap errors during extraction
trap-for-errors: true
"@

# Unified configuration content
$unifiedConfigContent = @"
name: "Unified CodeQL Configuration for All Platforms"

# This configuration file provides a unified configuration for CodeQL analysis
# across all platforms (Windows, macOS, Linux)
# Updated for better Windows compatibility

# Specify paths to analyze
paths:
  # JavaScript/TypeScript paths
  - 'ui'
  - 'sdk/javascript'
  - '**/*.js'
  - '**/*.jsx'
  - '**/*.ts'
  - '**/*.tsx'
  - '**/*.json'
  - '**/*.html'

  # Python paths
  - '**/*.py'
  - '**/*.pyw'
  - '**/*.pyi'

# Specify paths to exclude from analysis
paths-ignore:
  # Package management
  - '**/node_modules/**'
  # Don't ignore lock files for CodeQL analysis
  # - '**/package-lock.json'
  # - '**/yarn.lock'
  # - '**/pnpm-lock.yaml'
  - '**/.venv/**'
  - '**/venv/**'
  - '**/env/**'
  - '**/.env/**'
  - '**/pip-wheel-metadata/**'

  # Build artifacts
  - '**/dist/**'
  - '**/build/**'
  - '**/out/**'
  - '**/vendor/**'
  - '**/.next/**'
  - '**/__pycache__/**'
  - '**/*.egg-info/**'
  - '**/.pytest_cache/**'
  - '**/.mypy_cache/**'
  - '**/.ruff_cache/**'

  # Test files
  - '**/*.test.js'
  - '**/*.test.jsx'
  - '**/*.test.ts'
  - '**/*.test.tsx'
  - '**/*.spec.js'
  - '**/*.spec.jsx'
  - '**/*.spec.ts'
  - '**/*.spec.tsx'
  - '**/__tests__/**'
  - '**/__mocks__/**'
  - '**/test/**'
  - '**/tests/**'
  - '**/jest.config.js'
  - '**/jest.setup.js'
  - '**/cypress/**'
  - '**/playwright-report/**'
  - '**/pytest.ini'
  - '**/conftest.py'

  # Minified files and type definitions
  - '**/*.min.js'
  - '**/*.d.ts'

  # Configuration files
  - '**/.eslintrc.*'
  - '**/.prettierrc.*'
  - '**/tsconfig.json'
  - '**/babel.config.js'
  - '**/webpack.config.js'
  - '**/rollup.config.js'
  - '**/setup.py'
  - '**/setup.cfg'
  - '**/pyproject.toml'
  - '**/.flake8'
  - '**/.pylintrc'
  - '**/tox.ini'
  - '**/.coveragerc'

  # Documentation
  - '**/*.md'
  - '**/*.mdx'
  - '**/*.rst'
  - '**/docs/**'
  - '**/sphinx/**'

# Query filters
queries:
  # Use only the standard security-and-quality query suite to avoid conflicts and Windows path issues
  # This provides a comprehensive set of security and quality checks in a single suite
  - uses: security-and-quality

# Disable noisy alerts
disable-default-queries: false

# Query suite definitions
query-filters:
  - exclude:
      tags contain: test
  - exclude:
      tags contain: maintainability
      precision below: high
  - exclude:
      tags contain: correctness
      precision below: high

# Trap errors during extraction
trap-for-errors: true

# Database extraction settings
database:
  # Exclude files that are too large to analyze effectively
  max-file-size-mb: 10
  # Exclude files with too many lines
  max-lines-of-code: 25000
  # Exclude files with too many AST nodes
  max-ast-nodes: 500000
  # Extraction timeout per file
  extraction-timeout: 300
  # Windows-specific settings
  windows:
    # Increase timeout for Windows
    extraction-timeout: 600
"@

# Function to check and create a configuration file
function Ensure-ConfigFile {
    param (
        [string]$FilePath,
        [string]$Content,
        [string]$Description
    )

    if (Test-Path $FilePath) {
        Write-Host "CodeQL configuration file exists: $FilePath"
    } else {
        Write-Host "Creating $Description configuration file: $FilePath"
        Set-Content -Path $FilePath -Value $Content -Encoding UTF8 -Force
        Write-Host "Created $Description configuration file: $FilePath"
    }
}

# Ensure all configuration files exist
Ensure-ConfigFile -FilePath $windowsConfigFile -Content $windowsConfigContent -Description "Windows"
Ensure-ConfigFile -FilePath $ubuntuConfigFile -Content $ubuntuConfigContent -Description "Ubuntu"
Ensure-ConfigFile -FilePath $macosConfigFile -Content $macosConfigContent -Description "macOS"
Ensure-ConfigFile -FilePath $unifiedConfigFile -Content $unifiedConfigContent -Description "unified"

Write-Host "All CodeQL configuration files verified and created if needed."
