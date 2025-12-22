# Actium Examples

This directory contains example implementations demonstrating Actium's architecture and design philosophy.

## Architecture Overview

Actium is built on a **layered architecture** that separates concerns into distinct components:

### Core Layers

1. **Agent Layer** (`@agent` decorator)
   - Provides a minimal, function-like API for defining agents
   - Handles LLM interaction and tool orchestration
   - Built on top of SimpleLLMFunc's `llm_chat` decorator

2. **Runtime Layer** (Built-in Tools)
   - `execute_python`: Persistent IPython execution environment
   - `execute_shell`: Shell command execution in sandbox
   - `search_variables`: Variable discovery in Python environment

3. **Execution Layer** (Sessions)
   - `IPythonSession`: Long-lived Python execution context
   - `ShellSession`: Shell execution with fixed working directory
   - Variables and state persist across multiple tool calls

4. **Infrastructure Layer** (Sandbox & Skills)
   - `Sandbox`: Isolated file system workspace
   - Skills discovery and linking via file system
   - Automatic symlink creation for skills access

5. **Skills Layer** (File System-based)
   - Skills are directories with `SKILL.md` metadata
   - Discovered automatically from `skills_dir`
   - Agents explore and use skills through file system operations

## Design Philosophy

### 1. FS is the World

The file system is a **first-class citizen** in Actium's world model. Agents don't need special APIs to discover capabilities—they explore the file system just like a human developer would:

- Skills are discovered by reading directory structures
- Documentation is accessed via file system operations
- Agents use standard shell commands (`ls`, `cat`, `grep`) to explore

This design enables **emergent discovery**: agents can find and use new skills without explicit registration or API changes.

### 2. CodeAct over ToolCall

Agents act by **generating and executing code**, not by calling pre-defined tool functions. This approach:

- Provides maximum flexibility: agents can write any Python code
- Enables incremental development: build up complex workflows step by step
- Matches programmer intuition: agents think in code, not API calls

### 3. Persistent Runtime

Agents run in a **Jupyter notebook-like environment** where:

- Variables persist across executions (like notebook cells)
- Imported modules remain available
- Complex workflows can be built incrementally

This persistence enables agents to:

- Define helper functions and reuse them
- Build up data structures across multiple steps
- Maintain context without explicit state management

### 4. Programmer-Native UX

Defining an agent should feel like defining a regular function:

```python
@agent(
    model="openai/gpt-4",
    sandbox_dir="./sandbox",
    skills_dir="./skills"
)
async def my_agent(task: str):
    """You are a helpful assistant."""
    pass
```

No complex configuration, no boilerplate—just a decorator and a docstring.

## Code Examples

### Basic Agent Definition

```python
import asyncio
from actium import agent

@agent(
    model="openrouter/anthropic/claude-sonnet-4.5",
    sandbox_dir="./sandbox",
    skills_dir="./skills",
    max_steps=30,
    stream=True
)
async def data_analyst(task: str):
    """
    You are a professional data analyst specializing in Python-based 
    data analysis and visualization.
    
    Your capabilities include:
    - Data cleaning and preprocessing
    - Exploratory data analysis (EDA)
    - Statistical analysis
    - Data visualization using matplotlib and seaborn
    - Using available Skills tools (e.g., better-plot) for high-quality charts
    """
    pass

async def main():
    # The async for loop is ONLY for custom rendering of the agent's thinking process.
    # ReAct loop, tool calls, and execution are handled automatically by the framework.
    async for raw_response, history in data_analyst("Analyze the sales data"):
        # Process streaming response for custom rendering
        if hasattr(raw_response, "choices") and raw_response.choices:
            choice = raw_response.choices[0]
            if hasattr(choice, "delta") and choice.delta:
                content = getattr(choice.delta, "content", None)
                if content:
                    print(content, end="", flush=True)
    print()  # Newline

asyncio.run(main())

# If you don't need custom rendering, you can simply ignore the generator:
async def main_simple():
    # Just consume the generator - agent handles everything internally
    async for _ in data_analyst("Analyze the sales data"):
        pass
    # Agent completes all tool calls and ReAct internally

asyncio.run(main_simple())
```

### Interactive CLI

This example shows how to use `async for` for **custom rendering** in an interactive CLI:

```python
async def run_interactive_cli():
    """Run an interactive CLI loop with custom streaming rendering"""
    history = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ("quit", "exit"):
            break
        
        print("Assistant: ", end="", flush=True)
        
        # async for is ONLY for custom rendering - ReAct is handled automatically
        async for raw_response, updated_history in data_analyst(user_input):
            # Custom rendering: print streaming chunks as they arrive
            if hasattr(raw_response, "choices") and raw_response.choices:
                choice = raw_response.choices[0]
                if hasattr(choice, "delta") and choice.delta:
                    content = getattr(choice.delta, "content", None)
                    if content:
                        print(content, end="", flush=True)
            history = updated_history
        
        print()  # Newline

asyncio.run(run_interactive_cli())
```

**Note**: The `async for` loop here is **only for custom rendering** of the streaming output. The agent automatically handles all ReAct logic, tool calls, and execution internally.

### Agent Workflow

When you call an agent, it **automatically handles everything**:

1. **Initializes** the sandbox and execution sessions
2. **Discovers** available skills from the `skills_dir`
3. **Builds** a system prompt combining:
   - Your custom prompt (from docstring)
   - Base prompt (environment description, tools, best practices)
   - Skills information (discovered from file system)
4. **Executes** the ReAct loop internally:
   - Agent thinks about the task
   - Agent calls tools (`execute_python`, `execute_shell`)
   - Agent observes results
   - Agent reflects and continues or completes
5. **Streams** responses in real-time (if enabled)
6. **Cleans up** sessions when done

**Important**: The `async for` loop is **only for custom rendering** of the agent's thinking process. You don't need to handle the ReAct loop, tool calls, or execution—the framework does this automatically. If you don't need custom rendering, you can simply consume the generator without processing the output.

### Skills System

Skills are organized as directories with metadata:

```text
skills/
├── better-plot/
│   ├── SKILL.md          # YAML frontmatter + description
│   ├── plotting.py       # Python modules
│   └── __init__.py
└── better-pandas/
    ├── SKILL.md
    ├── pandas_operations.py
    └── __init__.py
```

The agent automatically:

- Discovers skills by scanning `skills_dir`
- Includes skill metadata in the system prompt
- Allows agents to explore skills via file system operations
- Enables agents to import and use skill modules

Example `SKILL.md`:

```markdown
---
name: better-plot
description: High-quality plotting utilities using matplotlib and seaborn
license: MIT
compatibility: python>=3.8
---

# better-plot

A set of functions for creating publication-quality plots.

## Functions

- `setup_plot_style()`: Configure global plot styling
- `create_scatter_plot()`: Create scatter plots
- `save_plot()`: Save plots to files
```

## Configuration

### Provider Configuration

Actium uses `provider.json` to manage LLM API keys:

```json
{
  "openrouter": [
    {
      "model_name": "anthropic/claude-sonnet-4.5",
      "api_keys": ["your-api-key"],
      "base_url": "https://openrouter.ai/api/v1"
    }
  ]
}
```

### Agent Configuration

Each agent can have independent configuration:

```python
@agent(
    model="openrouter/anthropic/claude-sonnet-4.5",
    sandbox_dir="./sandbox",           # Isolated workspace
    skills_dir="./skills",              # Skills directory
    max_steps=30,                      # Maximum tool calls
    timeout=300,                       # Execution timeout (seconds)
    stream=True,                       # Enable streaming
    provider_config_path="./provider.json"
)
async def my_agent(task: str):
    """Agent description."""
    pass
```

## Key Concepts

### Persistent Execution Environment

Unlike stateless function calls, Actium agents run in a persistent environment:

```python
# First execution: define a function
await execute_python("""
def process_data(data):
    return data * 2
""")

# Second execution: reuse the function
await execute_python("""
result = process_data([1, 2, 3])
print(result)  # [2, 4, 6]
""")
```

### File System as Discovery Mechanism

Agents discover capabilities through file system exploration:

```python
# Agent explores skills
await execute_shell("ls -la skills/")
await execute_shell("cat skills/better-plot/SKILL.md")

# Agent uses discovered skills
await execute_python("""
from better_plot import setup_plot_style, create_scatter_plot
setup_plot_style()
# ... create plots
""")
```

### Streaming Responses

Actium supports real-time streaming of agent thinking and execution. **The `async for` loop is optional and only needed for custom rendering**:

```python
# With custom rendering (optional)
async for raw_response, history in agent("task"):
    # Process streaming chunks for custom UI/display
    # Tool calls and ReAct are handled automatically by the framework
    # You only process the stream if you want custom rendering
    pass

# Without custom rendering (simpler)
async for _ in agent("task"):
    pass
# Agent completes all work internally - no rendering needed
```

**Key Point**: The framework automatically handles the entire ReAct loop, tool execution, and state management. The `async for` loop is **only for developers who want to customize how the agent's thinking process is displayed** to users.

## Running the Example

1. **Install dependencies**:

   ```bash
   pip install -e .
   ```

2. **Configure LLM**:

   Edit `examples/provider.json` with your API keys.

3. **Run the example**:

   ```bash
   python examples/data_analyst.py
   ```

4. **Interact**:
   - Enter tasks or questions
   - Type `quit` or `exit` to exit
   - Type `clear` to clear conversation history

## Further Reading

- [Main README](../README.md): Framework overview and API reference
- [Agent Documentation](../docs/agent.md): Detailed agent decorator documentation
- [Skills Documentation](../docs/skills.md): Skills system architecture
- [Execution Documentation](../docs/execution.md): Execution layer details
