# Secrets Management

This module provides a secure and flexible system for managing secrets within the pAIssive Income application.

## Features

- Multiple backend options for storing secrets:
  - Environment variables (default)
  - Encrypted file storage
  - In-memory storage (for testing)
  - HashiCorp Vault integration
- Configuration management that handles secret references
- Secret rotation capabilities
- Command-line interface for secret management
- Auditing tool to scan for hardcoded secrets

## Quick Start

```python
from common_utils.secrets import get_secret, set_secret

# Store a secret (defaults to environment variable storage)
set_secret("API_KEY", "your-secret-api-key")

# Retrieve a secret
api_key = get_secret("API_KEY")

# Use a different backend
from common_utils.secrets.secrets_manager import SecretsBackend
db_password = get_secret("DB_PASSWORD", backend=SecretsBackend.FILE)
```

## Using the Configuration Manager

The `SecretConfig` class provides a unified way to manage application configuration that might contain secrets.

```python
from common_utils.secrets.config import SecretConfig

# Create a configuration manager
config = SecretConfig()

# Get values (tries env vars, then config file)
db_host = config.get("database.host", default="localhost")

# Get a secret value
db_password = config.get("database.password", use_secret=True)

# Set a normal configuration value (stored in config file)
config.set("app.log_level", "INFO")

# Set a secret value (stored in secrets backend)
config.set("app.api_key", "your-secret-api-key", use_secret=True)
```

## Command Line Interface

The module includes a CLI for managing secrets:

```bash
# Set a secret (will prompt for value)
python -m common_utils.secrets.cli set API_KEY

# With explicit value (less secure, avoid in production)
python -m common_utils.secrets.cli set API_KEY --value="example-secret-value"

# Get a secret
python -m common_utils.secrets.cli get API_KEY

# List all secrets
python -m common_utils.secrets.cli list

# Delete a secret
python -m common_utils.secrets.cli delete API_KEY

# Use a specific backend
python -m common_utils.secrets.cli --backend file set DB_PASSWORD
```

## Vault Integration

To use HashiCorp Vault as a backend:

1. Set up Vault environment variables:
   ```bash
   export VAULT_ADDR="http://127.0.0.1:8200"
   export VAULT_TOKEN="example-vault-token"
   ```

2. Use the Vault backend:
   ```python
   from common_utils.secrets import get_secret
   from common_utils.secrets.secrets_manager import SecretsBackend

   # Get a secret from Vault
   api_key = get_secret("API_KEY", backend=SecretsBackend.VAULT)
   ```

## Secrets Auditing

The module includes a tool to audit your codebase for hardcoded secrets:

```bash
# Scan the current directory
python -m common_utils.secrets.audit

# Scan a specific directory
python -m common_utils.secrets.audit /path/to/code

# Save the report to a file
python -m common_utils.secrets.audit --output report.txt

# Export in JSON format
python -m common_utils.secrets.audit --json --output report.json

# Exclude specific directories
python -m common_utils.secrets.audit --exclude tests temp
```

## Best Practices

1. **Never hardcode secrets**: Always use the secrets management system.

2. **Use environment variables** for simple deployments and development.

3. **Use encrypted file storage** for more security when environment variables aren't practical.

4. **Use Vault** for production environments with many secrets and rotation requirements.

5. **Audit regularly**: Run the secrets audit tool periodically to catch any hardcoded secrets.

6. **Rotate secrets**: Change secrets periodically and after any security incident.

7. **Least privilege**: Limit access to secrets to only the functions that need them.

## Security Considerations

- The file-based storage encrypts secrets with a master password.
- Set the master password in the `PAISSIVE_MASTER_PASSWORD` environment variable.
- Secret files are created with restricted permissions (0600).
- Always treat the `.paissive` directory as sensitive and secure it appropriately.
