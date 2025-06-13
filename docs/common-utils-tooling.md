# Common Utils - Tooling

The `common_utils.tooling` module provides an extensible registry system for agentic reasoning and tool integration. It enables registration, discovery, and autonomous selection of callable tools (functions, APIs, etc.) along with rich metadata, empowering agents to reason about and use tools automatically.

---

## Overview

Key features of the tooling module:

1. **Extensible Tool Registry**: A global registry for storing tool callables and their metadata (keywords, input preprocessors, etc).
2. **Registration Functions**: Register, retrieve, and list tools with metadata.
3. **Metadata-driven Tool Selection**: Agents can match tools by keywords and prepare inputs automatically.
4. **Example Tools**: Built-in tools like a calculator, with metadata-driven registration.

---

## Tool Registry and Metadata

The tool registry is a global dictionary that maps tool names to a metadata dictionary, which includes the callable, descriptive keywords, input preprocessors, and more. This enables flexible, agentic tool selection and extension.

**Example: Registering a Tool with Metadata**

```python
from common_utils import tooling

# Define a custom tool
def greet(name: str) -> str:
    """Return a personalized greeting."""
    return f"Hello, {name}!"

tooling.register_tool(
    name="greet",
    func=greet,
    keywords=["hello", "introduction", "name", "greeting"],
    input_preprocessor=lambda x: {"name": x.strip().title()},
)
```

---

## Registration Functions

### `register_tool(name: str, func: Callable[..., Any], *, keywords: list[str] = None, input_preprocessor: Callable = None, **kwargs) -> None`

Registers a callable tool with a name and metadata.

- `name` (str): Name for the tool.
- `func` (callable): The tool function.
- `keywords` (list of str, optional): Keywords describing the tool's domain, for agentic matching.
- `input_preprocessor` (callable, optional): Function that prepares or transforms input before calling the tool.
- Additional keyword arguments are stored in the tool's metadata.

**Example: Registering a Calculator Tool with Metadata**

```python
from common_utils import tooling

def calculator(expression: str) -> float:
    """Evaluate a mathematical expression and return the result."""
    return eval(expression, {"__builtins__": None}, {})

def calc_input_prep(raw_input: str) -> dict:
    # Strip, validate, and wrap user input for the calculator
    return {"expression": raw_input.strip()}

tooling.register_tool(
    name="calculator",
    func=calculator,
    keywords=["math", "arithmetic", "calculate", "expression", "evaluate"],
    input_preprocessor=calc_input_prep,
)
```

---

### `get_tool(name: str) -> dict`

Retrieves a registered tool's metadata dictionary by name. The metadata dict always includes at least:

- `"func"`: the tool function/callable
- `"keywords"`: list of keywords (optional)
- `"input_preprocessor"`: callable or None (optional)
- ...plus any additional metadata fields

**Example:**

```python
from common_utils import tooling

# Retrieve the calculator tool metadata
calc_meta = tooling.get_tool("calculator")
result = calc_meta["func"]("2 + 2")
print(f"2 + 2 = {result}")  # Output: 2 + 2 = 4
```

---

### `list_tools() -> Dict[str, dict]`

Returns a dictionary mapping tool names to their metadata dicts (not just callables).

**Example:**

```python
from common_utils import tooling

tools = tooling.list_tools()
print("Available tools and metadata:")
for name, meta in tools.items():
    print(f"- {name}: {meta.get('func').__doc__ or 'No description'}")
    print(f"  Keywords: {meta.get('keywords')}")
    print(f"  Input preprocessor: {meta.get('input_preprocessor')}")
```

---

## How Agents Use Tool Metadata: Agentic Reasoning & Autonomous Selection

When an agent reasons about which tool to use, it leverages the metadata in the tool registry:

- **Keywords**: Agents match user intent or task requirements to the keywords defined for each tool. This allows for flexible, domain-aware tool selection.
- **Input Preprocessors**: Before calling a tool, agents can use the tool's input preprocessor to reformat, validate, or adapt input, enabling robust autonomous operation.
- **Metadata**: Agents may consider other metadata fields (description, examples, etc.) for richer reasoning.

This extensible metadata model allows for future enhancements, such as ranking tools by relevance, adding usage examples, or attaching documentation.

---

## Built-in Tools

### Calculator (with Metadata)

A built-in calculator tool is available, registered with descriptive keywords and an input preprocessor.

```python
from common_utils import tooling

calc_meta = tooling.get_tool("calculator")
result = calc_meta["func"]("2 + 3 * 4")
print(f"2 + 3 * 4 = {result}")  # Output: 14

# Use the input preprocessor
prep = calc_meta.get("input_preprocessor")
if prep:
    processed = prep("10 / 2")
    result = calc_meta["func"](**processed)
    print(f"10 / 2 = {result}")  # Output: 5.0
```

---

## Integration with Agents

Agents, such as `ArtistAgent` in `ai_models`, can discover all tools and their metadata, making autonomous decisions about which tool to call and how to format inputs.

```python
from ai_models.artist_agent import ArtistAgent
from common_utils import tooling

# Register a tool with keywords/input preprocessing
def reverse_text(text: str) -> str:
    "Reverse the input text."
    return text[::-1]

tooling.register_tool(
    "reverse",
    reverse_text,
    keywords=["reverse", "text", "string", "flip"],
    input_preprocessor=lambda s: {"text": s[::-1]}  # Example: double reverse for demo
)

agent = ArtistAgent()
# The agent will see all tool metadata, keywords, and input preprocessors
print("Available tools:", list(agent.tools.keys()))
```

---

## Extending with Custom Tools

You can extend the tool registry with custom tools and metadata for more robust, agent-friendly operation.

```python
from common_utils import tooling
import requests

def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # Example only; replace with production logic
    return f"Weather in {location}: Sunny, 22°C"

tooling.register_tool(
    "weather",
    get_weather,
    keywords=["weather", "forecast", "temperature", "location"],
    input_preprocessor=lambda s: {"location": s.strip().title()},
)
```

---

## Best Practices: Tool Metadata and Design

- **Docstrings**: Always add clear docstrings to tool functions for documentation and agent guidance.
- **Keywords**: Choose specific, relevant keywords that reflect the tool's domain and likely user intent.
- **Input Preprocessors**: Provide an input preprocessor if the tool requires input normalization, validation, or transformation. This increases agent reliability.
- **Error Handling**: Tools should raise informative errors or handle unexpected input gracefully.
- **Security**: Avoid unsafe operations in input preprocessors or tool functions (especially those using `eval()`).

---

## Example: Creating a Tool Suite with Metadata

```python
from common_utils import tooling

def count_words(text: str) -> int:
    """Count the number of words in a text."""
    return len(text.split())

def count_chars(text: str) -> int:
    """Count the number of characters in a text."""
    return len(text)

def find_keywords(text: str, num_keywords: int = 5) -> list[str]:
    """Find the most common words in a text."""
    from collections import Counter
    words = text.lower().split()
    return [w for w, _ in Counter(words).most_common(num_keywords)]

tooling.register_tool(
    "count_words",
    count_words,
    keywords=["words", "count", "text"],
    input_preprocessor=lambda s: {"text": s},
)
tooling.register_tool(
    "count_chars",
    count_chars,
    keywords=["characters", "count", "text", "length"],
    input_preprocessor=lambda s: {"text": s},
)
tooling.register_tool(
    "find_keywords",
    find_keywords,
    keywords=["keywords", "find", "common", "text", "frequency"],
    input_preprocessor=lambda s: {"text": s, "num_keywords": 5},
)

tools = tooling.list_tools()
print(f"Available tools: {list(tools.keys())}")
for name, meta in tools.items():
    print(f"{name}: {meta['func'].__doc__}")
```

---

## Conclusion

The `common_utils.tooling` module provides a modern, extensible, and metadata-driven system for registering and using tools in agent-based applications. Proper use of keywords and input preprocessors enables robust agentic reasoning and autonomous tool selection in your projects.