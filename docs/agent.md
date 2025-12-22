# Agent Module

The `agent` module provides the core `@agent` decorator that transforms regular async functions into intelligent CodeAct agents.

## Overview

The `@agent` decorator is the main entry point for creating Actium agents. It wraps a function with LLM-powered tool calling capabilities, providing a persistent execution environment and built-in tools for code execution.

## Core Components

### `agent` Decorator

The `@agent` decorator creates an agent from a function definition:

```python
@agent(
    model="openai/gpt-3.5-turbo",
    sandbox_dir="./sandbox",
    skills_dir="./skills",
    max_steps=20,
    timeout=300,
    stream=True,
    **llm_kwargs
)
async def my_agent(task: str):
    """Agent system prompt (from docstring)"""
    pass
```

#### Parameters

- **`model`** (str): LLM model identifier (e.g., `"openai/gpt-3.5-turbo"`)
- **`sandbox_dir`** (str): Sandbox root directory path (required)
- **`skills_dir`** (str): Skills directory path (required)
- **`max_steps`** (int): Maximum execution steps, maps to `max_tool_calls` (default: `20`)
- **`timeout`** (int): Single execution timeout in seconds (default: `300`)
- **`stream`** (bool): Enable streaming output (default: `True`)
- **`provider_config_path`** (Optional[str]): Path to `provider.json` configuration file
- **`**llm_kwargs`**: Additional parameters passed to `llm_chat` (e.g., `temperature`, `top_p`)

#### Return Type

Returns an async generator function that yields `(raw_response, history)` tuples:

```python
async for raw_response, history in my_agent("task"):
    # Process raw_response
    pass
```

### System Prompt Construction

The decorator automatically constructs a comprehensive system prompt by:

1. **User Prompt**: Extracted from the function's docstring
2. **Base Prompt**: Includes:
   - Working environment description (Jupyter notebook-like persistent execution)
   - Available tools documentation
   - Workflow guidelines
   - Best practices
   - Common shell commands reference
3. **Skills Prompt**: Automatically discovered from the `skills_dir` and formatted as XML

The final system prompt combines all three components, with the user prompt taking precedence.

## Architecture

### Integration with SimpleLLMFunc

The `@agent` decorator is built on top of SimpleLLMFunc's `llm_chat` decorator:

- Uses `llm_chat` for LLM interaction and tool calling
- Provides built-in tools: `execute_python`, `execute_shell`, `search_variables`
- Returns raw responses for maximum flexibility

### Execution Flow

1. **Initialization**: Creates sandbox and execution sessions
2. **Session Setup**: Initializes IPython and Shell sessions with proper working directories
3. **Tool Registration**: Registers built-in tools with the LLM interface
4. **Execution Loop**: Iterates through LLM responses and tool calls
5. **Cleanup**: Closes sessions and cleans up resources

### Built-in Tools

The agent automatically provides three built-in tools:

- **`execute_python`**: Executes Python code in a persistent IPython environment
- **`execute_shell`**: Executes shell commands in the sandbox directory
- **`search_variables`**: Searches for variables in the Python execution environment

See [Runtime Module](./runtime.md) for detailed tool documentation.

## Example Usage

### Basic Agent

```python
from actium import agent

@agent(
    model="openai/gpt-3.5-turbo",
    sandbox_dir="./sandbox",
    skills_dir="./skills"
)
async def calculator(task: str):
    """You are a helpful calculator agent."""
    pass

async def main():
    async for response, history in calculator("Calculate 2^10"):
        # Process response
        pass
```

### Agent with Custom Configuration

```python
@agent(
    model="openai/gpt-4",
    sandbox_dir="./sandbox/advanced",
    skills_dir="./skills/advanced",
    max_steps=50,
    timeout=600,
    temperature=0.7,
    top_p=0.9
)
async def advanced_agent(task: str):
    """You are an advanced agent with extended capabilities."""
    pass
```

## Implementation Details

### Session Management

Each agent invocation creates:
- A `Sandbox` instance for file system isolation
- An `IPythonSession` for Python code execution
- A `ShellSession` for shell command execution

Sessions are properly initialized and cleaned up, ensuring resource management.

### Skills Integration

The agent automatically:
1. Discovers skills from the `skills_dir`
2. Formats skill information as XML in the system prompt
3. Creates a symbolic link to skills in the sandbox directory

This allows agents to explore and use skills through the file system.

## See Also

- [Execution Module](./execution.md): Execution session implementation
- [Runtime Module](./runtime.md): Built-in tools implementation
- [Infrastructure Module](./infrastructure.md): Sandbox and resource management
- [Skills Module](./skills.md): Skills system
- [Config Module](./config.md): Configuration management

