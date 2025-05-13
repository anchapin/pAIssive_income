# Cursor AI Integration

This document describes the integration with Cursor AI in the pAIssive_income project, including configuration files and rules.

## Overview

[Cursor](https://cursor.sh/) is an AI-powered code editor that enhances developer productivity. Our project includes configuration files and rules to standardize how Cursor AI is used within the development workflow.

## Directory Structure

The `.cursor` directory contains configuration files and rules for the Cursor AI integration:

```
.cursor/
├── mcp.json             # MCP server configuration
└── rules/               # Rules for code standards
    ├── cursor_rules.mdc # Guidelines for creating Cursor rules
    ├── dev_workflow.mdc # Development workflow guidelines
    ├── self_improve.mdc # Self-improvement guidelines
    └── taskmaster.mdc   # Task management guidelines
```

## Configuration Files

### mcp.json

The `mcp.json` file configures the MCP (Model Control Protocol) servers used by Cursor. It includes:

- Server configurations
- API key environment variables
- Command and argument settings

Example:
```json
{
    "mcpServers": {
        "task-master-ai": {
            "command": "npx",
            "args": [
                "-y",
                "--package=task-master-ai",
                "task-master-ai"
            ],
            "env": {
                "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY_HERE",
                "PERPLEXITY_API_KEY": "PERPLEXITY_API_KEY_HERE",
                "OPENAI_API_KEY": "OPENAI_API_KEY_HERE",
                "GOOGLE_API_KEY": "GOOGLE_API_KEY_HERE",
                "XAI_API_KEY": "XAI_API_KEY_HERE",
                "OPENROUTER_API_KEY": "OPENROUTER_API_KEY_HERE",
                "MISTRAL_API_KEY": "MISTRAL_API_KEY_HERE",
                "AZURE_OPENAI_API_KEY": "AZURE_OPENAI_API_KEY_HERE",
                "OLLAMA_API_KEY": "OLLAMA_API_KEY_HERE"
            }
        }
    }
}
```

## Rules

The `.cursor/rules/` directory contains Markdown files (`.mdc`) that define coding standards and workflows for the project.

### cursor_rules.mdc

This file defines the structure and format for creating Cursor rules, ensuring consistency across all rule files.

Key guidelines:
- Required rule structure with frontmatter
- File reference format
- Code example formatting
- Rule content and maintenance guidelines

### dev_workflow.mdc

Contains guidelines for the development workflow, including:
- Code review processes
- Branch management
- Testing requirements
- Documentation standards

### self_improve.mdc

Guidelines for continuous improvement of code and processes.

### taskmaster.mdc

Rules for task management and organization within the project.

## Usage

1. Install Cursor AI from [cursor.sh](https://cursor.sh/)
2. Clone the repository with the `.cursor` directory
3. Configure your API keys in your local environment
4. Cursor will automatically apply the rules when working with relevant files

## Environment Variables

The Cursor integration uses various API keys that should be configured in your local environment. These keys are referenced in both the `.cursor/mcp.json` file and the `.env.example` file.

## Related Documentation

- [IDE Setup](ide_setup.md) - General IDE configuration including Cursor
- [Contributing](contributing.md) - Contribution guidelines that reference these rules
