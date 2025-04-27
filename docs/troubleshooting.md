# Troubleshooting

This guide provides solutions to common issues you might encounter when using the pAIssive Income Framework.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [AI Model Issues](#ai-model-issues)
3. [Agent Team Issues](#agent-team-issues)
4. [UI Issues](#ui-issues)
5. [Performance Issues](#performance-issues)
6. [Error Messages](#error-messages)
7. [Getting Help](#getting-help)

## Installation Issues

### Package Installation Failures

**Issue**: Error when installing dependencies with pip.

**Solution**:
1. Make sure you're using Python 3.8 or higher:
   ```bash
   python --version
   ```
2. Try updating pip:
   ```bash
   python -m pip install --upgrade pip
   ```
3. Install dependencies one by one to identify the problematic package:
   ```bash
   pip install package-name
   ```

### Import Errors

**Issue**: `ImportError` or `ModuleNotFoundError` when importing framework modules.

**Solution**:
1. Make sure you've installed the framework correctly:
   ```bash
   pip install -e .
   ```
2. Check if the module is in your Python path:
   ```python
   import sys
   print(sys.path)
   ```
3. Try reinstalling the framework:
   ```bash
   pip uninstall pAIssive_income
   pip install -e .
   ```

## AI Model Issues

### Model Loading Failures

**Issue**: Error when loading AI models.

**Solution**:
1. Check if the model exists in your models directory:
   ```python
   from ai_models import ModelManager
   manager = ModelManager()
   print(manager.list_models())
   ```
2. Make sure you have enough RAM for the model.
3. Try downloading the model again:
   ```python
   from ai_models import ModelDownloader
   downloader = ModelDownloader()
   downloader.download_model("model-id", source="huggingface")
   ```

### Slow Model Inference

**Issue**: Model inference is too slow.

**Solution**:
1. Use a smaller or quantized model:
   ```python
   from ai_models import ModelManager
   manager = ModelManager()
   model = manager.load_model("model-id-quantized")
   ```
2. Enable model caching:
   ```python
   from ai_models import ModelConfig
   config = ModelConfig.get_default()
   config.enable_cache = True
   config.save()
   ```
3. Use a GPU if available:
   ```python
   from ai_models import ModelConfig
   config = ModelConfig.get_default()
   config.device = "cuda"
   config.save()
   ```

## Agent Team Issues

### Agent Initialization Failures

**Issue**: Error when initializing agents.

**Solution**:
1. Check if the agent configuration is valid:
   ```python
   from agent_team import AgentTeam
   team = AgentTeam("My Team", config_path="path/to/config.json")
   print(team.config)
   ```
2. Make sure the required AI models are available:
   ```python
   from ai_models import ModelManager
   manager = ModelManager()
   print(manager.list_models())
   ```

### Agent Communication Failures

**Issue**: Agents fail to communicate with each other.

**Solution**:
1. Check if the agent team is properly initialized:
   ```python
   from agent_team import AgentTeam
   team = AgentTeam("My Team")
   print(team.agents)
   ```
2. Make sure the agent model provider is working:
   ```python
   from agent_team import AgentModelProvider
   provider = AgentModelProvider()
   print(provider.get_available_models())
   ```

## UI Issues

### UI Server Fails to Start

**Issue**: Error when starting the UI server.

**Solution**:
1. Check if the port is already in use:
   ```bash
   netstat -ano | findstr :5000
   ```
2. Try using a different port:
   ```python
   from ui import app
   app.run(port=5001)
   ```
3. Make sure Flask is installed:
   ```bash
   pip install flask
   ```

### UI Components Not Loading

**Issue**: UI components are not loading properly.

**Solution**:
1. Clear your browser cache and reload the page.
2. Check if the static files are being served correctly:
   ```bash
   ls ui/static
   ```
3. Make sure the templates are in the correct location:
   ```bash
   ls ui/templates
   ```

## Performance Issues

### High Memory Usage

**Issue**: The framework uses too much memory.

**Solution**:
1. Use smaller AI models:
   ```python
   from ai_models import ModelConfig
   config = ModelConfig.get_default()
   config.default_text_model = "smaller-model-id"
   config.save()
   ```
2. Unload models when not in use:
   ```python
   from ai_models import ModelManager
   manager = ModelManager()
   manager.unload_model("model-id")
   ```
3. Limit the number of concurrent agents:
   ```python
   from agent_team import AgentTeam
   team = AgentTeam("My Team", max_concurrent_agents=2)
   ```

### Slow Performance

**Issue**: The framework is running slowly.

**Solution**:
1. Use smaller or quantized models:
   ```python
   from ai_models import ModelManager
   manager = ModelManager()
   model = manager.load_model("model-id-quantized")
   ```
2. Enable caching:
   ```python
   from ai_models import ModelConfig
   config = ModelConfig.get_default()
   config.enable_cache = True
   config.save()
   ```
3. Use a GPU if available:
   ```python
   from ai_models import ModelConfig
   config = ModelConfig.get_default()
   config.device = "cuda"
   config.save()
   ```

## Error Messages

### "Model not found"

**Issue**: `ModelNotFoundError: Model 'model-id' not found.`

**Solution**:
1. Check if the model exists in your models directory:
   ```python
   from ai_models import ModelManager
   manager = ModelManager()
   print(manager.list_models())
   ```
2. Try downloading the model:
   ```python
   from ai_models import ModelDownloader
   downloader = ModelDownloader()
   downloader.download_model("model-id", source="huggingface")
   ```

### "Agent initialization failed"

**Issue**: `AgentInitializationError: Failed to initialize agent 'agent-name'.`

**Solution**:
1. Check if the agent configuration is valid:
   ```python
   from agent_team import AgentTeam
   team = AgentTeam("My Team", config_path="path/to/config.json")
   print(team.config)
   ```
2. Make sure the required AI models are available:
   ```python
   from ai_models import ModelManager
   manager = ModelManager()
   print(manager.list_models())
   ```

## Getting Help

If you're still experiencing issues after trying the solutions in this guide, you can get help from the community:

1. **GitHub Issues**: Create an issue on the [GitHub repository](https://github.com/anchapin/pAIssive_income/issues).
2. **Documentation**: Check the [documentation](README.md) for more information.
3. **Examples**: Look at the [examples](../examples) for guidance on how to use the framework.
4. **Community**: Join the community forum (coming soon) to ask questions and share your experiences.
