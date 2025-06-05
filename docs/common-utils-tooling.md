# Common Utils - Tooling

The `common_utils.tooling` module provides a registry system for agentic reasoning and tool integration. It allows registration and retrieval of callable tools (functions, APIs, etc.) for use by agent wrappers.

## Overview

The tooling module consists of several key components:

1. **Tool Registry**: A global registry for storing callable tools.
2. **Registration Functions**: Functions for registering and retrieving tools.
3. **Example Tools**: Built-in example tools like a calculator.

## Tool Registry

The tool registry is a global dictionary that maps tool names to callable functions. It serves as a central repository for all tools that can be used by agents.

```python
from common_utils import tooling

# Register a custom tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

tooling.register_tool("greet", greet)

# List all registered tools
tools = tooling.list_tools()
print(f"Available tools: {list(tools.keys())}")
```

## Registration Functions

### `register_tool(name: str, func: Callable[..., Any]) -> None`

Registers a callable tool with a name.

```python
from common_utils import tooling

# Define a custom tool
def word_count(text: str) -> int:
    """Count the number of words in a text."""
    return len(text.split())

# Register the tool
tooling.register_tool("word_count", word_count)
```

### `get_tool(name: str) -> Callable[..., Any]`

Retrieves a registered tool by name.

```python
from common_utils import tooling

# Get a tool by name
calculator = tooling.get_tool("calculator")

# Use the tool
result = calculator("2 + 2")
print(f"2 + 2 = {result}")  # Output: 2 + 2 = 4
```

### `list_tools() -> Dict[str, Callable[..., Any]]`

Lists all registered tools.

```python
from common_utils import tooling

# List all registered tools
tools = tooling.list_tools()
print("Available tools:")
for name, func in tools.items():
    print(f"- {name}: {func.__doc__ or 'No description'}")
```

## Built-in Tools

### Calculator

The module includes a built-in calculator tool that can evaluate mathematical expressions.

```python
from common_utils import tooling

# Get the calculator tool
calculator = tooling.get_tool("calculator")

# Use the calculator
result = calculator("2 + 3 * 4")
print(f"2 + 3 * 4 = {result}")  # Output: 2 + 3 * 4 = 14

# Try more complex expressions
print(calculator("10 / 2"))  # Output: 5.0
print(calculator("2 ** 3"))  # Output: 8
```

The calculator tool uses Python's `ast.literal_eval()` and a custom AST parser for safety, avoiding the dangerous `eval()` function.

## Integration with Agents

The tooling module is designed to be used with agent wrappers, such as the `ArtistAgent` in the `ai_models` module.

```python
from ai_models.artist_agent import ArtistAgent
from common_utils import tooling

# Define a custom tool
def reverse_text(text: str) -> str:
    """Reverse the input text."""
    return text[::-1]

# Register the tool
tooling.register_tool("reverse", reverse_text)

# Create an agent
agent = ArtistAgent()

# The agent will automatically discover the new tool
print("Available tools:", list(agent.tools.keys()))
```

## Extending with Custom Tools

You can extend the tool registry with your own custom tools:

```python
from common_utils import tooling
import requests

# Define a weather tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # This is a simplified example
    api_key = "your_api_key"
    url = f"https://api.example.com/weather?location={location}&api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    return f"Weather in {location}: {data['description']}, {data['temperature']}°C"

# Register the tool
tooling.register_tool("weather", get_weather)
```

## Best Practices

1. **Tool Documentation**: Always include docstrings for your tools to help users understand their purpose and usage.
2. **Input Validation**: Validate inputs in your tool functions to prevent errors.
3. **Error Handling**: Include proper error handling in your tools to provide helpful error messages.
4. **Security**: Be cautious with tools that execute code or make external requests.

## Example: Creating a Tool Suite

```python
from common_utils import tooling
from typing import List, Dict, Any

# Text analysis tools
def count_words(text: str) -> int:
    """Count the number of words in a text."""
    return len(text.split())

def count_chars(text: str) -> int:
    """Count the number of characters in a text."""
    return len(text)

def find_keywords(text: str, num_keywords: int = 5) -> List[str]:
    """Find the most common words in a text."""
    words = text.lower().split()
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:num_keywords]]

# Register the tools
tooling.register_tool("count_words", count_words)
tooling.register_tool("count_chars", count_chars)
tooling.register_tool("find_keywords", find_keywords)

# List all registered tools
tools = tooling.list_tools()
print(f"Available tools: {list(tools.keys())}")
```

## Conclusion

The `common_utils.tooling` module provides a flexible and extensible system for registering and using tools in agent-based applications. By creating a central registry of tools, it enables agents to discover and use a wide range of capabilities without tight coupling.

### Tool Registry
The `common_utils/tooling.py` module allows registration and retrieval of tools for agentic reasoning.

#### Example Tool: Calculator
The calculator evaluates simple mathematical expressions passed as strings. Use the `register_tool` method to add custom tools.

#### Example:
```python
# Register a custom tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

register_tool("greet", greet)

# List tools
print(list_tools())  # Outputs: {'calculator': <func>, 'greet': <func>}
```
